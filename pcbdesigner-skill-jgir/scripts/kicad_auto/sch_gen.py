"""Generate a KiCad 7 schematic (.kicad_sch) from a simple design description.
Each pin that carries a net gets a local net label at its end; unused pins get a
no-connect flag. Symbols come from the stock KiCad libraries or from custom
definitions (embedded and also written to a project symbol library)."""
import uuid, math, os, sys, copy
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump
import libsym

def U():
    return str(uuid.uuid4())

G = 2.54

def snap(v, g=1.27):
    return round(round(v / g) * g, 4)

# ---------------------------------------------------------------- custom symbols
def custom_symbol(name, left, right, top=(), bottom=(), ref='U', value=None, width=None, fp='', desc=''):
    """left/right/top/bottom: lists of (num, name, type) or None for a gap."""
    n = max(len(left), len(right), 1)
    w = width or max(15.24, G * (2 + max([len(p[1]) for p in list(left) + list(right) if p] + [4]) // 2.2))
    w = snap(w, 2*G)
    h = G * (n + 1)
    nt = max(len(top), len(bottom))
    w = max(w, G * (nt + 1))
    x0, x1 = -w / 2, w / 2
    y0, y1 = h / 2, -h / 2
    lines = []
    lines.append(f'(symbol "{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)')
    lines.append(f'(property "Reference" "{ref}" (at {x0} {y0 + 1.27} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))')
    lines.append(f'(property "Value" "{value or name}" (at {x0} {y1 - 1.27} 0) (effects (font (size 1.27 1.27)) (justify left top)))')
    lines.append(f'(property "Footprint" "{fp}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'(property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'(property "ki_description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'(symbol "{name}_0_1" (rectangle (start {x0} {y0}) (end {x1} {y1}) (stroke (width 0.254) (type default)) (fill (type background))))')
    pl = [f'(symbol "{name}_1_1"']
    def pin(num, nm, typ, x, y, ang):
        pl.append(f'(pin {typ} line (at {x} {y} {ang}) (length 2.54) (name "{nm}" (effects (font (size 1.016 1.016)))) (number "{num}" (effects (font (size 1.016 1.016)))))')
    for i, p in enumerate(left):
        if p: pin(p[0], p[1], p[2], snap(x0 - G, G), snap(y0 - G * (i + 1)), 0)
    for i, p in enumerate(right):
        if p: pin(p[0], p[1], p[2], snap(x1 + G, G), snap(y0 - G * (i + 1)), 180)
    for i, p in enumerate(top):
        if p: pin(p[0], p[1], p[2], snap(x0 + G * (i + 1), G), snap(y0 + G, G), 270)
    for i, p in enumerate(bottom):
        if p: pin(p[0], p[1], p[2], snap(x0 + G * (i + 1), G), snap(y1 - G, G), 90)
    pl.append(')')
    lines.append(' '.join(pl))
    lines.append(')')
    return parse(' '.join(lines))[0]

# ---------------------------------------------------------------- helpers
def sym_bbox(sym):
    xs, ys = [], []
    for p in libsym.pins(sym):
        xs.append(p['x']); ys.append(p['y'])
    def walk(x):
        for it in x:
            if isinstance(it, list) and it:
                if it[0] in ('start', 'end', 'xy', 'center', 'mid') and len(it) >= 3:
                    try:
                        xs.append(float(it[1])); ys.append(float(it[2]))
                    except ValueError:
                        pass
                walk(it)
    walk(sym)
    if not xs:
        return (-2.54, -2.54, 2.54, 2.54)
    return (min(xs), min(ys), max(xs), max(ys))

def rename_embedded(sym, libid):
    s = copy.deepcopy(sym)
    s[1] = f'"{libid}"'
    return s

def build_schematic(design, path, title, custom=None, paper='A2', notes=(), lib='proj', company='', rev='A', date=None):
    """design: list of part dicts (ref, sym 'Lib:Name', value, fp, pins{num:net}, group, lcsc, mpn, dnp).
    Symbols whose library is `lib` come from `custom` (sch_gen.custom_symbol objects)."""
    import datetime
    date = date or datetime.date.today().isoformat()
    custom = custom or {}
    root = U()
    proj = os.path.splitext(os.path.basename(path))[0]
    libsyms = {}
    out = []
    # resolve symbols
    for p in design:
        lid = p['sym']
        if lid not in libsyms:
            lib_, nm = lid.split(':')
            if lib_ == lib:
                libsyms[lid] = custom[nm]
            else:
                libsyms[lid] = libsym.get_symbol(lib_, nm)
    # --- placement: by group, column flow
    groups = []
    for p in design:
        g = p.get('group', 'Misc')
        if g not in groups: groups.append(g)
    PW = {'A4': (297, 210), 'A3': (420, 297), 'A2': (594, 420), 'A1': (841, 594)}[paper]
    margin = 20
    x_cursor, y_cursor, col_w = margin, margin + 15, 0
    placed = {}
    texts = []
    for g in groups:
        members = [p for p in design if p.get('group', 'Misc') == g]
        # block header
        blk = []
        for p in members:
            bb = sym_bbox(libsyms[p['sym']])
            w = (bb[2] - bb[0]) + 30  # label room
            h = (bb[3] - bb[1]) + 10
            blk.append((p, bb, w, h))
        bw = max(b[2] for b in blk)
        bh = sum(b[3] for b in blk) + 8
        # if block is tall and has many small parts, use 2 sub-columns
        ncols = 1
        if bh > 180 and len(blk) > 6:
            ncols = 2
        if ncols == 2:
            half = math.ceil(len(blk) / 2)
            colsets = [blk[:half], blk[half:]]
            bh = max(sum(b[3] for b in cs) for cs in colsets) + 8
            bwt = sum(max(b[2] for b in cs) for cs in colsets)
        else:
            colsets = [blk]; bwt = bw
        if y_cursor + bh > PW[1] - margin:
            x_cursor += col_w + 12; y_cursor = margin + 15; col_w = 0
        texts.append((g, x_cursor, y_cursor - 4))
        cx = x_cursor
        for cs in colsets:
            cy = y_cursor + 4
            cw = max(b[2] for b in cs)
            for (p, bb, w, h) in cs:
                ox = snap(cx + 15 - bb[0], G)
                oy = snap(cy + bb[3] + 3, G)  # symbol y up -> schematic y down
                placed[p['ref']] = (ox, oy)
                cy += h
            cx += cw
        col_w = max(col_w, bwt)
        y_cursor += bh + 10
    # --- emit
    out.append(f'(kicad_sch (version 20230121) (generator eeschema) (uuid {root}) (paper "{paper}")')
    out.append(f'(title_block (title "{title}") (date "{date}") (rev "{rev}") (company "{company}") (comment 1 "Generated design - PRELIMINARY, verify before fabrication"))')
    out.append('(lib_symbols')
    for lid, s in libsyms.items():
        out.append(dump(rename_embedded(s, lid)))
    out.append(')')
    for (g, x, y) in texts:
        out.append(f'(text "{g}" (at {x} {y} 0) (effects (font (size 2.5 2.5) bold) (justify left bottom)) (uuid {U()}))')
    for i, n in enumerate(notes):
        out.append(f'(text "{n}" (at {margin} {PW[1]-margin-8+i*0} 0) (effects (font (size 1.8 1.8)) (justify left bottom)) (uuid {U()}))')
    pinmap = {}
    for p in design:
        sym = libsyms[p['sym']]
        ox, oy = placed[p['ref']]
        su = U(); p['uuid'] = su
        bb = sym_bbox(sym)
        props = [('Reference', p['ref'], ox + bb[2] + 1.27, oy + bb[1] - 1.27 + (bb[3]-bb[1]) / 2 - 1.27, False),
                 ('Value', p['value'], ox + bb[2] + 1.27, oy + bb[1] + (bb[3]-bb[1]) / 2 + 1.27, False),
                 ('Footprint', p['fp'], ox, oy, True),
                 ('Datasheet', p.get('ds', '~'), ox, oy, True)]
        for k in ('LCSC', 'MPN'):
            if p.get(k.lower()):
                props.append((k, p[k.lower()], ox, oy, True))
        pr = ' '.join(f'(property "{k}" "{v}" (at {snap(x)} {snap(y)} 0) (effects (font (size 1.27 1.27)) (justify left){" hide" if h else ""}))' for k, v, x, y, h in props)
        pins = libsym.pins(sym)
        pu = ' '.join(f'(pin "{q["num"]}" (uuid {U()}))' for q in pins)
        dnp = 'yes' if p.get('dnp') else 'no'
        out.append(f'(symbol (lib_id "{p["sym"]}") (at {ox} {oy} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {dnp}) (fields_autoplaced) (uuid {su}) {pr} {pu} (instances (project "{proj}" (path "/{root}" (reference "{p["ref"]}") (unit 1)))))')
        # labels / no-connects
        used = set()
        for q in pins:
            px, py = snap(ox + q['x']), snap(oy - q['y'])
            net = p['pins'].get(q['num'])
            if q['num'] in used and net:
                pass
            if net:
                ang = {0: 180, 180: 0, 90: 270, 270: 90}[int(q['ang']) % 360]
                just = {0: 'left', 180: 'right', 90: 'left', 270: 'right'}[ang]
                out.append(f'(label "{net}" (at {px} {py} {ang}) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid {U()}))')
                pinmap.setdefault(net, []).append((p['ref'], q['num']))
            else:
                if q['type'] in ('no_connect',):
                    continue
                out.append(f'(no_connect (at {px} {py}) (uuid {U()}))')
    out.append(f'(sheet_instances (path "/" (page "1")))')
    out.append(')')
    open(path, 'w').write('\n'.join(out))
    return pinmap, root

def write_symlib(custom, path):
    with open(path, 'w') as f:
        f.write('(kicad_symbol_lib (version 20220914) (generator kicad_auto)\n')
        for k, s in custom.items():
            f.write(dump(s) + '\n')
        f.write(')\n')
