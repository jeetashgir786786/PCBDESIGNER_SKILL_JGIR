#!/usr/bin/env python3
"""Full autorouting pipeline: Freerouting (github.com/freerouting/freerouting) + plane fan-out + A* finisher.

usage: python3 route.py <board.kicad_pcb> [--passes 20] [--attempts 1] [--keep] [--no-fanout] [--rounds 4]
                        [--finish-layers F.Cu,B.Cu] [--jar /path/freerouting.jar] [--timeout 1800]

Pipeline (every pcbnew step runs in a fresh subprocess - the SWIG type registry breaks after board.Remove()):
 1 prepare   save outer-layer pours to <board>.zones.json, remove them (Freerouting treats a pour as a
             blockage), remove unlocked tracks (unless --keep)
 2 fanout    stub+via from SMD pads of inner-plane nets (nets that own a zone on an inner layer)
 3 freeroute export Specctra DSN -> java -jar freerouting.jar -de x.dsn -do x.ses -mp N -> custom SES import
             (KiCad 7's ImportSpecctraSES has no board argument from Python)
 4 finish    up to --rounds: DRC -> unconnected nets -> grid A* reroute (round 1), rip-up + reroute on a
             finer grid (round 2+), rip-up of neighbouring nets near the open pads (round 3+) -> dedupe
             (A* avoids inner plane layers unless --finish-layers says otherwise)
 5 restore   re-add the outer pours, refill all zones, write docs/<name>_DRC_routed.rpt and print a summary
Exit code 0 only when the routed board has 0 unconnected items and 0 DRC errors.
"""
import sys, os, json, subprocess, argparse, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drc

PY = sys.executable


def py(code, *args, env=None, check=True):
    """run a pcbnew snippet in a fresh interpreter"""
    e = dict(os.environ); e.update(env or {})
    r = subprocess.run([PY, '-c', code, *args], capture_output=True, text=True, env=e, cwd=HERE)
    if check and r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-3000:]); raise SystemExit(f'step failed: {code[:60]}')
    # SWIG prints 'swig/python detected a memory leak ...' to stdout on exit - drop those lines
    return '\n'.join(l for l in r.stdout.splitlines() if not l.startswith('swig/python'))


def script(name, *args, env=None, timeout=None):
    e = dict(os.environ); e.update(env or {})
    r = subprocess.run([PY, os.path.join(HERE, name), *args], capture_output=True, text=True, env=e, timeout=timeout)
    out = [l for l in (r.stdout + r.stderr).strip().splitlines() if not l.startswith('swig/python')]
    return r.returncode, out


def find_jar(arg):
    for c in [arg, os.environ.get('FREEROUTING_JAR'), '/opt/fr/freerouting.jar',
              os.path.expanduser('~/.local/share/freerouting/freerouting.jar'), os.path.join(HERE, 'freerouting.jar')]:
        if c and os.path.exists(c):
            return c
    sys.exit('freerouting.jar not found: run get_freerouting.sh or pass --jar / set FREEROUTING_JAR')


PREPARE = r'''
import sys, json, pcbnew
pcb, keep = sys.argv[1], sys.argv[2] == '1'
b = pcbnew.LoadBoard(pcb)
bb = b.GetBoardEdgesBoundingBox()
R = [(pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop())), (pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetTop())),
     (pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())), (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetBottom()))]
zones = [b.GetArea(i) for i in range(b.GetAreaCount())]
outer, inner_nets, inner_layers = [], set(), set()
for z in zones:
    if z.GetIsRuleArea(): continue
    L = z.GetLayer()
    if L in (pcbnew.F_Cu, pcbnew.B_Cu):
        ol = z.Outline().Outline(0)
        pts = [(pcbnew.ToMM(ol.CPoint(i).x), pcbnew.ToMM(ol.CPoint(i).y)) for i in range(ol.PointCount())]
        outer.append(dict(layer=b.GetLayerName(L), net=z.GetNetname(), clearance=pcbnew.ToMM(z.GetLocalClearance()),
                          prio=z.GetAssignedPriority(), pts=pts, name=z.GetZoneName()))
    else:
        inner_nets.add(z.GetNetname()); inner_layers.add(b.GetLayerName(L))
for z in zones:
    if not z.GetIsRuleArea() and z.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu): b.Remove(z)
n = 0
if not keep:
    for t in [t for t in b.GetTracks() if not t.IsLocked()]: b.Remove(t); n += 1
pcbnew.SaveBoard(pcb, b)
print(json.dumps(dict(R=R, outer=outer, inner_nets=sorted(inner_nets), inner_layers=sorted(inner_layers),
                      removed=n, layers=[b.GetLayerName(l) for l in b.GetEnabledLayers().CuStack()])))
'''

FREEROUTE_EXPORT = r'''
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
print(pcbnew.ExportSpecctraDSN(b, sys.argv[2]))
'''

SES_IMPORT = r'''
import sys, pcbnew
from ses_import import imp
b = pcbnew.LoadBoard(sys.argv[1])
nets0 = b.GetNetsByName(); nets = {str(k): nets0[k] for k in nets0.keys()}
if sys.argv[3] == '1':
    for t in [t for t in b.GetTracks() if not t.IsLocked()]: b.Remove(t)
print(imp(b, sys.argv[2], nets))
pcbnew.SaveBoard(sys.argv[1], b)
'''

RESTORE = r'''
import sys, json, os, pcbnew
sys.path.insert(0, os.getcwd())
from pcb_gen import add_zone
pcb, spec = sys.argv[1], json.load(open(sys.argv[2]))
b = pcbnew.LoadBoard(pcb)
nets0 = b.GetNetsByName(); nets = {str(k): nets0[k] for k in nets0.keys()}
for z in spec['outer']:
    add_zone(b, nets.get(z['net']), b.GetLayerID(z['layer']), z['pts'], prio=z['prio'], clearance=z['clearance'], name=z['name'])
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(pcb, b)
print('restored', len(spec['outer']))
'''

NEIGHBOURS = r'''
import sys, math, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); fail = set(sys.argv[2].split(',')); R = float(sys.argv[3])
pts = [tuple(map(float, q.split(':'))) for q in sys.argv[4].split(',')]
near = set()
for t in b.GetTracks():
    n = t.GetNetname()
    if n in fail or t.IsLocked() or not n: continue
    for (x, y) in pts:
        for p in ((t.GetStart(), t.GetEnd()) if t.Type() != pcbnew.PCB_VIA_T else (t.GetPosition(),)):
            if math.hypot(pcbnew.ToMM(p.x) - x, pcbnew.ToMM(p.y) - y) < R: near.add(n)
print(','.join(sorted(near)))
'''

VIASIZE = r'''
import sys, json
pro = json.load(open(sys.argv[1]))
d = [c for c in pro['net_settings']['classes'] if c['name'] == 'Default'][0]
r = pro['board']['design_settings']['rules']
print(d.get('via_diameter', 0.6), d.get('via_drill', 0.3), d.get('track_width', 0.2), d.get('clearance', 0.2),
      r.get('min_copper_edge_clearance', 0.3), r.get('min_hole_clearance', 0.25), r.get('min_hole_to_hole', 0.25))
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pcb'); ap.add_argument('--passes', default='20'); ap.add_argument('--keep', action='store_true')
    ap.add_argument('--no-fanout', action='store_true'); ap.add_argument('--rounds', type=int, default=4)
    ap.add_argument('--finish-layers'); ap.add_argument('--jar'); ap.add_argument('--timeout', type=int, default=1800)
    ap.add_argument('--threads', default='1')
    ap.add_argument('--attempts', type=int, default=1, help='Freerouting runs with different pass budgets; the best result is kept')
    a = ap.parse_args()
    pcb = os.path.abspath(a.pcb); base = os.path.splitext(pcb)[0]
    name = os.path.basename(base)
    jar = find_jar(a.jar)
    pro = base + '.kicad_pro'
    vd, vh, tw, clr, edge, hclr, h2h = [float(x) for x in py(VIASIZE, pro).split()]
    env = dict(VIA_D=str(vd), VIA_DR=str(vh), W=str(min(tw, 0.2)), CLR=str(clr), EDGE=str(edge), HCLR=str(hclr), H2H=str(h2h))
    t0 = time.time()

    # 1 prepare
    info = json.loads(py(PREPARE, pcb, '1' if a.keep else '0').strip().splitlines()[-1])
    json.dump(info, open(base + '.zones.json', 'w'))
    print(f"[prepare] outer pours saved: {len(info['outer'])}; inner planes: {info['inner_nets']} on {info['inner_layers']}; "
          f"tracks removed: {info['removed']}")

    # 2 fanout
    if info['inner_nets'] and not a.no_fanout:
        rc, out = script('fanout.py', pcb, ','.join(info['inner_nets']), env=env)
        print('[fanout]', out[-1] if out else rc)

    import shutil
    shutil.copy(pcb, base + '.pre.kicad_pcb')   # prepared + fanned-out board: every attempt starts here
    overall = None                              # (score, attempt)
    for att in range(a.attempts):
        shutil.copy(base + '.pre.kicad_pcb', pcb)
        for f in (base + '.ses',):
            if os.path.exists(f): os.remove(f)
        if a.attempts > 1:
            print(f'=== attempt {att + 1}/{a.attempts}')
        # 3 freerouting
        dsn, ses = base + '.dsn', base + '.ses'
        py(FREEROUTE_EXPORT, pcb, dsn)
        # identical input gives an identical Freerouting result, so each attempt changes the pass budget
        passes = str(int(a.passes) + 7 * att)
        cmd = ['java', '-jar', jar, '-de', dsn, '-do', ses, '-mp', passes, '-mt', a.threads]
        if os.environ.get('DISPLAY') is None and subprocess.run(['which', 'xvfb-run'], capture_output=True).returncode == 0:
            cmd = ['xvfb-run', '-a'] + cmd          # Freerouting 1.x needs a display even in batch mode
        t = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout, cwd=tempfile.mkdtemp(prefix='freerouting_'))
        if not os.path.exists(ses):
            print(r.stdout[-2000:], r.stderr[-2000:]); sys.exit('Freerouting produced no .ses')
        print(f'[freerouting] {passes} passes, exit {r.returncode} in {time.time() - t:.0f}s')
        print('[ses import] tracks, vias =', py(SES_IMPORT, pcb, ses, '1' if a.keep else '0').strip().splitlines()[-1])

        # 4 finish rounds with the grid A* router (outer pours still removed -> conservative connectivity)
        lay = a.finish_layers or ','.join(l for l in info['layers'] if l not in info['inner_layers'])
        orders = [lay, ','.join(reversed(lay.split(','))), ','.join(info['layers']), lay, ','.join(info['layers'])]
        best = None                                # (score, round): keep the best board seen, later rounds can regress
        for rnd in range(a.rounds + 1):
            rpt, s = drc.run(pcb, base + '.work.rpt', refill=True)
            score = s['unconnected'] * 10 + s['errors']
            if best is None or score < best[0]:
                best = (score, rnd); shutil.copy(pcb, base + '.best.kicad_pcb')
            if rnd == a.rounds:
                break
            nets = list(s['unconnected_nets'])
            # clearance/short errors: rip up the routed net involved (not a plane net) and reroute it
            for v in s['violations']:
                if v['severity'] == 'error' and v['type'] in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance',
                                                              'copper_edge_clearance', 'via_dangling'):
                    cand = [m.group(1) for (_, _, t) in v['items'] for m in [drc.NET.search(t)] if m and ('Track' in t or 'Via' in t)]
                    cand = [c for c in cand if c not in info['inner_nets']]
                    if cand and cand[0] not in nets:
                        nets.append(cand[0])
            print(f'[finish {rnd + 1}] {drc.fmt(s)}')
            if not nets:
                break
            todo = list(nets)
            if rnd >= 2:
                # neighbour rip-up: free the area around the open pads, route the hard nets first, then the rest
                pts = ','.join(f'{x}:{y}' for v in s['violations'] if v['type'] == 'unconnected_items' for (x, y, _) in v['items'])
                near = py(NEIGHBOURS, pcb, ','.join(nets), str(1.0 + 0.5 * (rnd - 2)), pts).strip().splitlines()
                near = [n for n in (near[-1].split(',') if near and near[-1] else []) if n not in info['inner_nets']]
                print('    rip-up neighbours:', near)
                todo += near
            rip = todo if rnd > 0 else [n for n in todo if n not in s['unconnected_nets']]
            if rip:
                script('ripup.py', pcb, ','.join(rip))
            for k, n in enumerate(todo):
                rc, out = script('astar_net.py', pcb, n, orders[min(rnd, len(orders) - 1)],
                                 env=dict(env, RES='0.05' if rnd == 0 else '0.025'), timeout=900)
                print('   ', n, out[-1] if out else rc)
            script('dedupe.py', pcb)

        if best[1] != rnd:
            print(f'[best] attempt {att + 1}: keeping finish round {best[1] + 1} (score {best[0]})')
        shutil.copy(base + '.best.kicad_pcb', pcb); os.remove(base + '.best.kicad_pcb')
        if overall is None or best[0] < overall[0]:
            overall = (best[0], att); shutil.copy(pcb, base + '.overall.kicad_pcb')
        if best[0] == 0:
            break
    shutil.copy(base + '.overall.kicad_pcb', pcb)
    for f in (base + '.overall.kicad_pcb', base + '.pre.kicad_pcb'):
        os.remove(f)
    if a.attempts > 1:
        print(f'[attempts] best attempt {overall[1] + 1} (score {overall[0]})')
    # 5 restore pours + final DRC
    print('[restore]', py(RESTORE, pcb, base + '.zones.json').strip())
    rpt, s = drc.run(pcb, os.path.join(os.path.dirname(pcb), 'docs', f'{name}_DRC_routed.rpt'), refill=True)
    for f in (base + '.zones.json', base + '.work.rpt'):
        if os.path.exists(f): os.remove(f)
    print(f'[done] {time.time() - t0:.0f}s  {drc.fmt(s)}')
    print('report:', rpt)
    if s['unconnected_nets']:
        print('still unconnected:', s['unconnected_nets'],
              '\n -> move the blocking parts / swap pins / add room, rebuild and route again (see references/kicad-automation.md)')
    sys.exit(0 if not (s['errors'] or s['unconnected']) else 1)


if __name__ == '__main__':
    main()
