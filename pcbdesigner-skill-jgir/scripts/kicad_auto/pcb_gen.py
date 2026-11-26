"""Build a KiCad PCB from design data with the pcbnew SWIG API (tested on KiCad 7.0.11).

Gotchas learned the hard way (keep these when editing):
- Add a footprint to the board BEFORE Flip(), otherwise pcbnew can segfault.
- Flip first, then SetOrientationDegrees() (rotation is about the flipped part).
- BOARD_STACKUP is not usable from SWIG: write the board, then inject a text (stackup ...) block (add_stackup).
- pcbnew.SaveBoard() rewrites the .kicad_pro: write the project file AFTER saving the board.
"""
import os, json, sys
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import kenv

kenv.setup()
MM = pcbnew.FromMM


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def load_fp(fpid, locallib, libname):
    lib, name = fpid.split(':')
    path = locallib if lib == libname else os.path.join(kenv.fp_dir(), f'{lib}.pretty')
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None:
        raise RuntimeError(f'footprint not found: {fpid} (looked in {path})')
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def write_project(path, classes, patterns, rules, severities=None, track_widths=None, vias=None):
    """Write the .kicad_pro with net classes, pattern assignments and design-rule minimums."""
    nc = []
    for c in classes:
        nc.append(dict(name=c['name'], clearance=c['clearance'], track_width=c['track'], via_diameter=c.get('via', 0.6),
                       via_drill=c.get('drill', 0.3), diff_pair_width=c.get('dp_width', 0.2), diff_pair_gap=c.get('dp_gap', 0.2),
                       diff_pair_via_gap=0.25, microvia_diameter=0.3, microvia_drill=0.1, wire_width=6, bus_width=12,
                       line_style=0, pcb_color='rgba(0, 0, 0, 0.000)', schematic_color='rgba(0, 0, 0, 0.000)'))
    sev = {'lib_footprint_issues': 'ignore', 'lib_footprint_mismatch': 'ignore', 'silk_overlap': 'ignore',
           'silk_over_copper': 'warning', 'silk_edge_clearance': 'ignore', 'starved_thermal': 'warning', 'text_height': 'ignore', 'text_thickness': 'ignore'}
    sev.update(severities or {})
    pro = {
        'board': {'design_settings': {'defaults': {'board_outline_line_width': 0.1, 'copper_line_width': 0.2},
                                      'rules': rules, 'rule_severities': sev,
                                      'track_widths': [0.0] + (track_widths or [0.15, 0.2, 0.25, 0.3, 0.4, 0.6, 0.8, 1.0]),
                                      'via_dimensions': [{'diameter': 0.0, 'drill': 0.0}] +
                                                        [{'diameter': d, 'drill': h} for d, h in (vias or [(0.6, 0.3)])]},
                  'layer_presets': [], 'viewports': []},
        'meta': {'filename': os.path.basename(path), 'version': 1},
        'net_settings': {'classes': nc, 'meta': {'version': 3}, 'net_colors': None, 'netclass_assignments': None,
                         'netclass_patterns': [{'netclass': k, 'pattern': v} for k, v in patterns]},
        'pcbnew': {'last_paths': {}, 'page_layout_descr_file': ''},
        'schematic': {'drawing': {'default_line_thickness': 6.0, 'default_text_size': 50.0}, 'legacy_lib_dir': '',
                      'legacy_lib_list': []},
        'sheets': [], 'text_variables': {}}
    json.dump(pro, open(path, 'w'), indent=2)


def rounded_rect_outline(board, cx, cy, w, h, r, width=0.1):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    segs = [((x0 + r, y0), (x1 - r, y0)), ((x1, y0 + r), (x1, y1 - r)), ((x1 - r, y1), (x0 + r, y1)), ((x0, y1 - r), (x0, y0 + r))]
    for a, b in segs:
        s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(*a)); s.SetEnd(V(*b)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(width)); board.Add(s)
    if r > 0:
        for (ccx, ccy, sx, sy) in [(x0 + r, y0 + r, x0, y0 + r), (x1 - r, y0 + r, x1 - r, y0),
                                   (x1 - r, y1 - r, x1, y1 - r), (x0 + r, y1 - r, x0 + r, y1)]:
            s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_ARC)
            s.SetCenter(V(ccx, ccy)); s.SetStart(V(sx, sy)); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T), True)
            s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(width)); board.Add(s)


def polygon_outline(board, pts, width=0.1):
    for a, b in zip(pts, pts[1:] + pts[:1]):
        s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(*a)); s.SetEnd(V(*b)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(width)); board.Add(s)


def add_zone(board, net, layer, pts, prio=0, clearance=0.2, minw=0.2, thermal_gap=0.25, spoke=0.4, solid=False, name=''):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    if net is not None:
        z.SetNet(net)
    ol = z.Outline(); ol.NewOutline()
    for (x, y) in pts:
        ol.Append(MM(x), MM(y))
    z.SetAssignedPriority(prio)
    z.SetLocalClearance(MM(clearance))
    z.SetMinThickness(MM(minw))
    z.SetThermalReliefGap(MM(thermal_gap))
    z.SetThermalReliefSpokeWidth(MM(spoke))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if solid else pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    if name:
        z.SetZoneName(name)
    board.Add(z)
    return z


def add_keepout(board, pts, layers, tracks=True, vias=True, pour=True):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    ls = pcbnew.LSET()
    for l in layers:
        ls.AddLayer(l)
    z.SetLayerSet(ls)
    ol = z.Outline(); ol.NewOutline()
    for (x, y) in pts:
        ol.Append(MM(x), MM(y))
    z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(vias); z.SetDoNotAllowCopperPour(pour)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    board.Add(z)
    return z


def _fab_bbox(fpid, locallib, libname):
    fresh = load_fp(fpid, locallib, libname)
    fab = [g for g in fresh.GraphicalItems() if g.GetLayer() == pcbnew.F_Fab] or \
          [g for g in fresh.GraphicalItems() if g.GetLayer() == pcbnew.F_CrtYd]
    if not fab:
        return None
    bb = fab[0].GetBoundingBox()
    for g2 in fab[1:]:
        bb.Merge(g2.GetBoundingBox())
    ox, oy = fresh.GetPosition().x, fresh.GetPosition().y
    return (pcbnew.ToMM(bb.GetLeft() - ox), pcbnew.ToMM(bb.GetTop() - oy),
            pcbnew.ToMM(bb.GetRight() - ox), pcbnew.ToMM(bb.GetBottom() - oy))


def place_parts(board, parts, locallib, libname, origin, sym_uuids, model_subst=None, box_models=None, shapes_dir=None):
    """parts[i]['place'] = (x, y, rot_deg, 'F'|'B') relative to origin.
    model_subst: {footprint_name: (step_file_in_shapes_dir, z_rot)}  - replace/add a 3D model
    box_models:  {footprint_name: (height_mm, (r,g,b), has_actuator)} - auto-generate a box STEP from the F.Fab outline
    Pads with an empty number on an IC (thermal-via sub-pads) inherit the net of the highest-numbered pad (the EP)."""
    model_subst = model_subst or {}
    box_models = box_models or {}
    shapes_dir = shapes_dir or os.path.join(os.path.dirname(locallib), f'{libname}.3dshapes')
    nets = {}

    def net(n):
        if n not in nets:
            ni = pcbnew.NETINFO_ITEM(board, n); board.Add(ni); nets[n] = ni
        return nets[n]
    ox, oy = origin
    fps = {}
    for p in parts:
        if p.get('virtual') or not p.get('fp'):
            continue
        fp = load_fp(p['fp'], locallib, libname)
        fp.SetReference(p['ref']); fp.SetValue(p['value'])
        if p.get('lcsc'):
            fp.SetProperty('LCSC', p['lcsc'])
        if p['ref'] in sym_uuids:
            fp.SetPath(pcbnew.KIID_PATH('/' + sym_uuids[p['ref']]))
        x, y, rot, side = p['place']
        board.Add(fp)                       # add before flip (segfault otherwise)
        fp.SetPosition(V(ox + x, oy + y))
        if side == 'B':
            fp.Flip(fp.GetPosition(), False)
        fp.SetOrientationDegrees(rot)
        nm = str(fp.GetFPID().GetLibItemName())
        rel = '${KIPRJMOD}/' + os.path.basename(shapes_dir) + '/'
        if nm in model_subst:
            f, zr = model_subst[nm]
            fp.Models().clear()
            m = pcbnew.FP_3DMODEL(); m.m_Filename = rel + f; m.m_Rotation = pcbnew.VECTOR3D(0, 0, zr); fp.Models().append(m)
        elif nm in box_models:
            import models3d
            os.makedirs(shapes_dir, exist_ok=True)
            if not os.path.exists(os.path.join(shapes_dir, nm + '.step')):
                box = _fab_bbox(p['fp'], locallib, libname)
                if box:
                    h, rgb, act = box_models[nm]
                    models3d.box_from_fab(shapes_dir, nm, box, h, rgb, act)
            fp.Models().clear()
            m = pcbnew.FP_3DMODEL(); m.m_Filename = rel + nm + '.step'; fp.Models().append(m)
        if p.get('strip_vias'):             # drop PTH thermal pads (e.g. module EP vias that collide with bottom parts)
            for pad in list(fp.Pads()):
                if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                    fp.Remove(pad)
        numbered = [q.GetNumber() for q in fp.Pads() if q.GetNumber()]
        ep = max(numbered, key=lambda s: (len(s), s)) if numbered else None
        for pad in fp.Pads():
            num = pad.GetNumber()
            n = p['pins'].get(num)
            if n is None and num == '' and pad.IsOnCopperLayer() and pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH \
                    and p['ref'][:1] in ('U', 'Q') and ep:
                n = p['pins'].get(ep)
            if n:
                pad.SetNet(net(n))
        if p.get('nobom'):
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        fps[p['ref']] = fp
    return fps, nets


def courtyard_check(board):
    """Overlapping courtyards on the same side (bounding-box test - conservative)."""
    items = []
    for fp in board.GetFootprints():
        for side, lay in (('F', pcbnew.F_CrtYd), ('B', pcbnew.B_CrtYd)):
            bb = None
            for g in fp.GraphicalItems():
                if g.GetLayer() == lay:
                    b = g.GetBoundingBox()
                    if bb is None:
                        bb = b
                    else:
                        bb.Merge(b)
            if bb is not None:
                items.append((fp.GetReference(), side, pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()),
                              pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())))
    probs = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            if a[1] != b[1]:
                continue
            ox = min(a[4], b[4]) - max(a[2], b[2]); oy = min(a[5], b[5]) - max(a[3], b[3])
            if ox > 0.01 and oy > 0.01:
                probs.append(f'{a[0]} x {b[0]} ({a[1]}) overlap {ox:.2f}x{oy:.2f} mm')
    return probs


def add_stackup(path, layers, total, finish='HASL(with lead)', er=4.4):
    """Inject a symmetric stackup block into (setup). Dielectric thicknesses follow JLCPCB-style
    constructions for 2/4 layers (4L: 0.2104 mm 7628 prepreg + core) and an even split for 6+ layers.
    These are planning values: confirm against the fab's published stackup before impedance work."""
    mask, cu_o, cu_i = 0.01, 0.035, 0.0152
    L = ['(layer "F.SilkS" (type "Top Silk Screen"))', '(layer "F.Paste" (type "Top Solder Paste"))',
         f'(layer "F.Mask" (type "Top Solder Mask") (thickness {mask}))', f'(layer "F.Cu" (type "copper") (thickness {cu_o}))']
    if layers == 2:
        core = round(total - 2 * mask - 2 * cu_o, 4)
        L += [f'(layer "dielectric 1" (type "core") (thickness {core}) (material "FR4") (epsilon_r {er}) (loss_tangent 0.02))']
    else:
        n_in = layers - 2
        n_d = layers - 1
        if layers == 4:
            pp = 0.2104
            core = round(total - 2 * mask - 2 * cu_o - n_in * cu_i - 2 * pp, 4)
            diel = [('prepreg', pp), ('core', core), ('prepreg', pp)]
        else:
            t = round((total - 2 * mask - 2 * cu_o - n_in * cu_i) / n_d, 4)
            diel = [('prepreg' if k % 2 == 0 else 'core', t) for k in range(n_d)]
        for k, (typ, th) in enumerate(diel):
            L.append(f'(layer "dielectric {k + 1}" (type "{typ}") (thickness {th}) (material "FR4") (epsilon_r {er}) (loss_tangent 0.02))')
            if k < n_in:
                L.append(f'(layer "In{k + 1}.Cu" (type "copper") (thickness {cu_i}))')
    L += [f'(layer "B.Cu" (type "copper") (thickness {cu_o}))', f'(layer "B.Mask" (type "Bottom Solder Mask") (thickness {mask}))',
          '(layer "B.Paste" (type "Bottom Solder Paste"))', '(layer "B.SilkS" (type "Bottom Silk Screen"))',
          f'(copper_finish "{finish}")', '(dielectric_constraints no)']
    blk = '(stackup\n      ' + '\n      '.join(L) + '\n    )\n    '
    s = open(path).read()
    i = s.index('(setup') + len('(setup')
    s = s[:i] + '\n    ' + blk + s[i:]
    open(path, 'w').write(s)
