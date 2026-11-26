"""Simple placeholder 3D bodies (CadQuery -> coloured STEP) for footprints that ship without a model.
They are fit-check boxes, not vendor models: label them as such in any 3D deliverable."""
import os
import cadquery as cq


def box_from_fab(d, name, bbox, height, rgb=(0.15, 0.15, 0.15), actuator=False):
    """bbox = (x0, y0, x1, y1) in footprint coordinates (KiCad y down)."""
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, -(y0 + y1) / 2
    a = cq.Assembly()
    body = cq.Workplane('XY').box(x1 - x0, y1 - y0, height).translate((cx, cy, height / 2)) \
        .edges('|Z').fillet(min(0.4, (x1 - x0) / 4, (y1 - y0) / 4))
    a.add(body, name='body', color=cq.Color(*rgb))
    if actuator:
        r = min(1.75, (x1 - x0) / 3, (y1 - y0) / 3)
        a.add(cq.Workplane('XY').circle(r).extrude(1.0).translate((cx, cy, height)), name='act', color=cq.Color(0.25, 0.25, 0.28))
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + '.step')
    a.save(p, 'STEP')
    return p


def simple_box(d, name, w, l, h, rgb=(0.15, 0.15, 0.15)):
    return box_from_fab(d, name, (-w / 2, -l / 2, w / 2, l / 2), h, rgb)
