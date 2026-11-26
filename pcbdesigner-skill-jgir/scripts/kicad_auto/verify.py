#!/usr/bin/env python3
"""Verification gate: DRC + board-vs-design parity + schematic-netlist parity (+ ERC when the CLI has it).

usage: python3 verify.py <project_dir> <NAME>
design.json (written by build.py) is the netlist of record. Exit 0 only if every check passes.
Report this output verbatim in the handoff: tool, KiCad version, counts, and anything not run."""
import sys, os, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kenv, drc
from sexp import parse, find


def board_parity(pcb, design):
    import pcbnew
    b = pcbnew.LoadBoard(pcb)
    bad, n = [], 0
    seen = set()
    for fp in b.GetFootprints():
        ref = fp.GetReference(); seen.add(ref)
        p = design.get(ref)
        if not p:
            bad.append(f'{ref}: on board, not in design'); continue
        for pad in fp.Pads():
            if not pad.GetNumber():
                continue
            n += 1
            want = p['pins'].get(pad.GetNumber(), '')
            if pad.GetNetname() != want:
                bad.append(f'{ref}.{pad.GetNumber()}: board={pad.GetNetname()!r} design={want!r}')
    for ref, p in design.items():
        if p.get('fp') and not p.get('virtual') and ref not in seen:
            bad.append(f'{ref}: in design, missing on board')
    return n, bad


def sch_parity(sch, design):
    tmp = tempfile.mktemp(suffix='.net')
    r = subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '-o', tmp, sch], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None, [f'netlist export failed: {r.stderr.strip()[:200]}']
    net = parse(open(tmp).read())[0]
    got = {}
    for nn in find(find(net, 'nets')[0], 'net'):
        name = find(nn, 'name')[0][1].strip('"').lstrip('/')
        for nd in find(nn, 'node'):
            got[(find(nd, 'ref')[0][1].strip('"'), find(nd, 'pin')[0][1].strip('"'))] = name
    bad, n = [], 0
    for ref, p in design.items():
        if p.get('virtual'):
            continue
        for pin, want in p['pins'].items():
            n += 1
            g = got.get((ref, pin))
            if g is None:
                bad.append(f'{ref}.{pin}: missing in schematic netlist (want {want})')
            elif g != want:
                bad.append(f'{ref}.{pin}: schematic={g} design={want}')
    cnt = {}
    for k, v in got.items():
        cnt.setdefault(v, []).append(k)
    singles = [k for k, v in cnt.items() if len(v) == 1 and not k.startswith('unconnected') and not k.startswith('Net-(')]
    if singles:
        print(f'   note: single-pin nets (check for typos): {singles}')
    return n, bad


def erc(sch, out):
    r = subprocess.run(['kicad-cli', 'sch', 'erc', '--help'], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    r = subprocess.run(['kicad-cli', 'sch', 'erc', '--severity-all', '-o', out, sch], capture_output=True, text=True)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else f'exit {r.returncode}'


def main(d, name):
    d = os.path.abspath(d)
    pcb, sch = os.path.join(d, name + '.kicad_pcb'), os.path.join(d, name + '.kicad_sch')
    design = json.load(open(os.path.join(d, 'design.json')))
    ok = True
    print('KiCad', kenv.kicad_version())
    rpt, s = drc.run(pcb, os.path.join(d, 'docs', name + '_DRC.rpt'), refill=True)
    print('DRC          ', drc.fmt(s)); ok &= not (s['errors'] or s['unconnected'])
    n, bad = board_parity(pcb, design)
    print(f'board parity  {n} pads checked, {len(bad)} problems'); ok &= not bad
    for x in bad[:30]: print('   ', x)
    n, bad = sch_parity(sch, design)
    print(f'sch parity    {n} pin assignments checked, {len(bad)} problems'); ok &= not bad
    for x in bad[:30]: print('   ', x)
    e = erc(sch, os.path.join(d, 'docs', name + '_ERC.rpt'))
    print('ERC          ', e if e is not None else 'NOT RUN (kicad-cli sch erc needs KiCad 8+; run ERC in the GUI)')
    print('RESULT       ', 'PASS' if ok else 'FAIL')
    return ok


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(0 if main(sys.argv[1], sys.argv[2]) else 1)
