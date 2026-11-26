"""Write simple custom footprints (.kicad_mod) for pads/holes not in the stock library."""
import os

def _pad(num, x, y, w, h, shape='roundrect', typ='smd', layers='"F.Cu" "F.Paste" "F.Mask"', drill=None):
    rr = ' (roundrect_rratio 0.25)' if shape == 'roundrect' else ''
    d = f' (drill {drill})' if drill else ''
    return f'  (pad "{num}" {typ} {shape} (at {x} {y}) (size {w} {h}){d} (layers {layers}){rr})\n'

def write_fp(libdir, name, pads, crt, descr='', silk_labels=(), model=None):
    """pads: list of dict(num,x,y,w,h[,typ,shape,drill,layers]); crt: (x0,y0,x1,y1)"""
    os.makedirs(libdir, exist_ok=True)
    s = f'(footprint "{name}" (version 20221018) (generator kicad_auto) (layer "F.Cu")\n'
    s += f'  (descr "{descr}")\n  (attr smd)\n'
    s += f'  (fp_text reference "REF**" (at 0 {crt[1]-0.8}) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))\n'
    s += f'  (fp_text value "{name}" (at 0 {crt[3]+0.8}) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))\n'
    for (t, x, y) in silk_labels:
        s += f'  (fp_text user "{t}" (at {x} {y}) (layer "F.SilkS") (effects (font (size 0.6 0.6) (thickness 0.1))))\n'
    x0, y0, x1, y1 = crt
    s += f'  (fp_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))\n'
    for p in pads:
        s += _pad(p['num'], p['x'], p['y'], p['w'], p['h'], p.get('shape', 'roundrect'), p.get('typ', 'smd'),
                  p.get('layers', '"F.Cu" "F.Paste" "F.Mask"'), p.get('drill'))
    if model:
        s += f'  (model "{model}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n'
    s += ')\n'
    open(os.path.join(libdir, name + '.kicad_mod'), 'w').write(s)

def pad_row(n, pitch, w, h, vertical=False, start=1, mask_only=False):
    pads = []
    off = (n - 1) * pitch / 2
    for i in range(n):
        c = round(-off + i * pitch, 3)
        x, y = (0, c) if vertical else (c, 0)
        lay = '"F.Cu" "F.Mask"' if mask_only else '"F.Cu" "F.Mask"'
        pads.append(dict(num=str(start + i), x=x, y=y, w=w, h=h, layers=lay))
    return pads
