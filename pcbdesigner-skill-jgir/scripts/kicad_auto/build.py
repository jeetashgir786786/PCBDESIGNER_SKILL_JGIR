#!/usr/bin/env python3
"""Generate a complete KiCad project (schematic + placed PCB + project rules + stackup) from a design spec.

usage: python3 build.py <spec.py> <out_dir>

The spec is a Python file defining (see examples/spec_template.py):
  NAME, TITLE, COMPANY='', REV='A', LIB='proj', PAPER='A3', NOTES=[]
  CUSTOM_SYMBOLS = {name: sch_gen.custom_symbol(...)}            (optional)
  def custom_footprints(libdir): fpgen.write_fp(libdir, ...)     (optional)
  def parts(): return [part dicts with ref, sym, value, fp, pins, group, place=(x, y, rot, 'F'|'B'), lcsc, mpn]
  BOARD = dict(layers, thickness, outline=dict(w, h, r) | dict(poly=[...]), fab='jlcpcb',
               zones=[dict(net, layer, pts=None, prio=0, clearance=0.2)], keepouts=[dict(pts, layers)],
               classes=[...], patterns=[(class, pattern)], rules_override={}, finish, model_subst, box_models)
Outputs in <out_dir>: NAME.kicad_sch/.kicad_pcb/.kicad_pro, LIB.kicad_sym, LIB.pretty/, sym-lib-table,
fp-lib-table, design.json (the netlist of record used by the parity checks), docs/NAME_DRC_placement.rpt
"""
import sys, os, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kenv
kenv.setup()
import pcbnew
from sch_gen import build_schematic, write_symlib
import pcb_gen as G
import fab_rules
import drc


def load_spec(path):
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    spec = importlib.util.spec_from_file_location('design_spec', path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def main(spec_path, out):
    D = load_spec(spec_path)
    NAME, LIB = D.NAME, getattr(D, 'LIB', 'proj')
    B = D.BOARD
    out = os.path.abspath(out)
    os.makedirs(os.path.join(out, 'docs'), exist_ok=True)
    libdir = os.path.join(out, f'{LIB}.pretty')
    os.makedirs(libdir, exist_ok=True)
    if hasattr(D, 'custom_footprints'):
        D.custom_footprints(libdir)
    custom = getattr(D, 'CUSTOM_SYMBOLS', {})
    parts = D.parts()

    # duplicate refs / missing placement are silent killers - fail early
    refs = [p['ref'] for p in parts]
    dup = {r for r in refs if refs.count(r) > 1}
    if dup:
        sys.exit(f'duplicate refs: {sorted(dup)}')
    missing = [p['ref'] for p in parts if p.get('fp') and not p.get('virtual') and 'place' not in p]
    if missing:
        sys.exit(f'parts without place=(x,y,rot,side): {missing}')

    write_symlib(custom, os.path.join(out, f'{LIB}.kicad_sym'))
    open(os.path.join(out, 'sym-lib-table'), 'w').write(
        f'(sym_lib_table\n  (lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.kicad_sym")(options "")(descr "project symbols"))\n)\n')
    open(os.path.join(out, 'fp-lib-table'), 'w').write(
        f'(fp_lib_table\n  (lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.pretty")(options "")(descr "project footprints"))\n)\n')

    pinmap, root = build_schematic(parts, os.path.join(out, f'{NAME}.kicad_sch'), D.TITLE, custom,
                                   getattr(D, 'PAPER', 'A3'), getattr(D, 'NOTES', []), lib=LIB,
                                   company=getattr(D, 'COMPANY', ''), rev=getattr(D, 'REV', 'A'))
    sym_uuids = {p['ref']: p['uuid'] for p in parts}
    json.dump({p['ref']: {k: v for k, v in p.items() if k != 'place'} for p in parts},
              open(os.path.join(out, 'design.json'), 'w'), indent=1)

    layers = B.get('layers', 2)
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(layers)
    for k in range(1, layers - 1):
        lid = b.GetLayerID(f'In{k}.Cu')
        b.SetLayerType(lid, pcbnew.LT_POWER if B.get('inner_power', True) else pcbnew.LT_SIGNAL)
    CX, CY = B.get('origin', (100, 100))
    ol = B['outline']
    if 'poly' in ol:
        G.polygon_outline(b, [(CX + x, CY + y) for x, y in ol['poly']])
        full = [(CX + x, CY + y) for x, y in ol['poly']]
    else:
        G.rounded_rect_outline(b, CX, CY, ol['w'], ol['h'], ol.get('r', 0))
        w2, h2 = ol['w'] / 2, ol['h'] / 2
        full = [(CX - w2, CY - h2), (CX + w2, CY - h2), (CX + w2, CY + h2), (CX - w2, CY + h2)]
    fps, nets = G.place_parts(b, parts, libdir, LIB, (CX, CY), sym_uuids, B.get('model_subst'), B.get('box_models'),
                              os.path.join(out, f'{LIB}.3dshapes'))
    b.GetDesignSettings().SetBoardThickness(G.MM(B.get('thickness', 1.6)))
    for z in B.get('zones', []):
        if z['net'] not in nets:
            sys.exit(f'zone net {z["net"]} is not used by any pad')
        pts = [(CX + x, CY + y) for x, y in z['pts']] if z.get('pts') else full
        G.add_zone(b, nets[z['net']], b.GetLayerID(z['layer']), pts, prio=z.get('prio', 0), clearance=z.get('clearance', 0.2),
                   solid=z.get('solid', False), name=z.get('name', f"{z['net']}_{z['layer']}"))
    for k in B.get('keepouts', []):
        G.add_keepout(b, [(CX + x, CY + y) for x, y in k['pts']], [b.GetLayerID(l) for l in k['layers']],
                      k.get('tracks', True), k.get('vias', True), k.get('pour', True))
    pcb = os.path.join(out, f'{NAME}.kicad_pcb')
    pcbnew.SaveBoard(pcb, b)
    G.add_stackup(pcb, layers, B.get('thickness', 1.6), B.get('finish', 'HASL(with lead)'))

    rules = fab_rules.rules(B.get('fab', 'jlcpcb'), layers, **B.get('rules_override', {}))
    vd, vh = fab_rules.DEFAULT_VIA[min(layers, 6) if layers >= 4 else 2]
    classes = B.get('classes') or [dict(name='Default', clearance=0.2, track=0.25)]
    for c in classes:
        c.setdefault('via', vd); c.setdefault('drill', vh)
    G.write_project(os.path.join(out, f'{NAME}.kicad_pro'), classes, B.get('patterns', []), rules,
                    vias=[(vd, vh)])          # after SaveBoard (SaveBoard rewrites the .kicad_pro)

    # fill + placement DRC in a fresh process-state (reload)
    b2 = pcbnew.LoadBoard(pcb)
    pcbnew.ZONE_FILLER(b2).Fill(b2.Zones())
    pcbnew.SaveBoard(pcb, b2)
    G.write_project(os.path.join(out, f'{NAME}.kicad_pro'), classes, B.get('patterns', []), rules, vias=[(vd, vh)])
    rpt = os.path.join(out, 'docs', f'{NAME}_DRC_placement.rpt')
    pcbnew.WriteDRCReport(b2, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
    s = drc.summary(rpt)
    print(f'built {NAME}: {len(fps)} footprints, {len(nets)} nets, {layers} layers')
    for q in G.courtyard_check(b2):
        print('  COURTYARD', q)
    print('  placement DRC:', drc.fmt(s))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
