#!/usr/bin/env python3
"""Manufacturing package for JLCPCB-style PCBA: Gerbers (X2) + Excellon drills (PTH/NPTH + maps) + zip,
BOM (JLCPCB format + full), CPL, schematic PDF, assembly PDFs, STEP.

usage: python3 fab.py <project_dir> <NAME>
LCSC numbers marked lcsc_ok=True in the spec are reported as verified; all others as UNVERIFIED.
JLCPCB CPL rotations differ from KiCad for some footprints: always check the placement preview on jlcpcb.com."""
import sys, os, json, csv, subprocess, re, zipfile, glob, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kenv
kenv.setup()
import pcbnew


def nat(r):
    m = re.match(r'([A-Za-z]+)(\d+)', r)
    return (m.group(1), int(m.group(2))) if m else (r, 0)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def hand_soldered(p):
    m = (p.get('mpn') or '').lower()
    return p.get('hand') or any(k in m for k in ('solder pad', 'solder jumper', 'wire', 'not placed'))


def main(d, name):
    d = os.path.abspath(d); os.chdir(d)
    fab, docs = os.path.join(d, 'fab'), os.path.join(d, 'docs')
    gdir = os.path.join(fab, 'gerbers')
    os.makedirs(gdir, exist_ok=True); os.makedirs(docs, exist_ok=True)
    pcb, sch = f'{name}.kicad_pcb', f'{name}.kicad_sch'
    b = pcbnew.LoadBoard(pcb)
    n_cu = b.GetCopperLayerCount()
    cu = ['F.Cu'] + [f'In{k}.Cu' for k in range(1, n_cu - 1)] + ['B.Cu']
    layers = cu + ['F.Paste', 'B.Paste', 'F.SilkS', 'B.SilkS', 'F.Mask', 'B.Mask', 'Edge.Cuts']
    for f in glob.glob(os.path.join(gdir, '*')):
        os.remove(f)
    rc, o = run(['kicad-cli', 'pcb', 'export', 'gerbers', '-o', gdir + '/', '-l', ','.join(layers), '--subtract-soldermask', pcb])
    print('gerbers', rc, len(glob.glob(gdir + '/*')), 'files')
    rc, o = run(['kicad-cli', 'pcb', 'export', 'drill', '-o', gdir + '/', '--format', 'excellon', '--excellon-separate-th',
                 '--generate-map', '--map-format', 'gerberx2', '-u', 'mm', pcb])
    print('drill', rc)
    z = os.path.join(fab, f'{name}_Gerbers_JLCPCB.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(glob.glob(gdir + '/*')):
            zf.write(f, os.path.basename(f))
    print('zip', os.path.basename(z))

    design = json.load(open('design.json'))
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    groups = {}
    for ref, p in design.items():
        if p.get('virtual') or p.get('nobom') or not p.get('fp') or p.get('dnp'):
            continue
        key = (p['value'], p['fp'], p.get('lcsc', ''), p.get('mpn', ''), bool(p.get('lcsc_ok')), hand_soldered(p))
        groups.setdefault(key, []).append(ref)
    today = datetime.date.today().isoformat()
    unver = 0
    with open(f'fab/{name}_BOM_JLCPCB.csv', 'w', newline='') as f1, open(f'fab/{name}_BOM_full.csv', 'w', newline='') as f2:
        w1, w2 = csv.writer(f1), csv.writer(f2)
        w1.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
        w2.writerow(['Qty', 'Value', 'Designators', 'Footprint', 'MPN / spec', 'LCSC', 'LCSC status', 'Assembly'])
        for (val, fpn, lcsc, mpn, ok, hand), refs in sorted(groups.items(), key=lambda kv: nat(sorted(kv[1], key=nat)[0])):
            refs = sorted(refs, key=nat)
            if hand:
                status = 'n/a'
            elif lcsc and ok:
                status = f'verified (spec, {today})'
            elif lcsc:
                status = 'UNVERIFIED - check part + stock on jlcpcb.com/parts'; unver += 1
            else:
                status = 'NO LCSC PART - select one'; unver += 1
            w2.writerow([len(refs), val, ' '.join(refs), fpn.split(':')[1], mpn, lcsc, status, 'hand / not placed' if hand else 'SMT'])
            if not hand:
                w1.writerow([val, ','.join(refs), fpn.split(':')[1], lcsc])
    with open(f'fab/{name}_CPL_JLCPCB.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        for ref in sorted(fps, key=nat):
            p = design.get(ref)
            if not p or p.get('nobom') or p.get('dnp') or hand_soldered(p):
                continue
            fp = fps[ref]; pos = fp.GetPosition()
            w.writerow([ref, f'{pcbnew.ToMM(pos.x):.3f}mm', f'{-pcbnew.ToMM(pos.y):.3f}mm',
                        'Bottom' if fp.IsFlipped() else 'Top', f'{fp.GetOrientationDegrees() % 360:.0f}'])
    print(f'BOM/CPL written; {unver} BOM lines need an LCSC check')

    rc, _ = run(['kicad-cli', 'sch', 'export', 'pdf', '-o', f'docs/{name}_schematic.pdf', sch]); print('schematic pdf', rc)
    for side, ls, extra in (('top', 'F.Fab,F.SilkS,Edge.Cuts,F.CrtYd', []), ('bottom', 'B.Fab,B.SilkS,Edge.Cuts,B.CrtYd', ['--mirror'])):
        rc, _ = run(['kicad-cli', 'pcb', 'export', 'pdf', '-o', f'docs/{name}_assembly_{side}.pdf', '-l', ls] + extra + [pcb])
        print('assembly', side, rc)
    rc, _ = run(['kicad-cli', 'pcb', 'export', 'step', '--subst-models', '-f', '-o', f'{name}.step', pcb]); print('step', rc)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
