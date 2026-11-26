"""STEP (components+board) -> GLB, plus copper pad/track overlay taken from the .kicad_pcb (KiCad 7 STEP has no copper)."""
import sys, os, trimesh
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from step2glb import convert
from shapely.geometry import Polygon

GOLD = [212, 175, 55, 255]
COPPER = [184, 115, 51, 255]
SILK = [245, 245, 245, 255]

def poly_from_set(ps):
    out = []
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        pts = [(pcbnew.ToMM(o.CPoint(j).x), -pcbnew.ToMM(o.CPoint(j).y)) for j in range(o.PointCount())]
        if len(pts) >= 3:
            holes = []
            for h in range(ps.HoleCount(i)):
                ho = ps.Hole(i, h)
                holes.append([(pcbnew.ToMM(ho.CPoint(j).x), -pcbnew.ToMM(ho.CPoint(j).y)) for j in range(ho.PointCount())])
            p = Polygon(pts, holes)
            if p.is_valid and p.area > 1e-4:
                out.append(p)
    return out

def overlay(pcb_path, thickness):
    b = pcbnew.LoadBoard(pcb_path)
    meshes = {'gold': [], 'copper': []}
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            for layer, z0 in ((pcbnew.F_Cu, thickness), (pcbnew.B_Cu, -0.04)):
                if not pad.IsOnLayer(layer) or pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    continue
                ps = pcbnew.SHAPE_POLY_SET()
                pad.TransformShapeToPolygon(ps, layer, 0, pcbnew.FromMM(0.005))
                for p in poly_from_set(ps):
                    m = trimesh.creation.extrude_polygon(p, 0.04); m.apply_translation([0, 0, z0]); meshes['gold'].append(m)
    for t in b.GetTracks():
        for layer, z0 in ((pcbnew.F_Cu, thickness), (pcbnew.B_Cu, -0.04)):
            if t.GetLayer() != layer and not (t.Type() == pcbnew.PCB_VIA_T):
                continue
            from shapely.geometry import LineString, Point
            if t.Type() == pcbnew.PCB_VIA_T:
                c = t.GetPosition(); geo = [Point(pcbnew.ToMM(c.x), -pcbnew.ToMM(c.y)).buffer(pcbnew.ToMM(t.GetWidth()) / 2, 12)]
            else:
                s_, e_ = t.GetStart(), t.GetEnd()
                geo = [LineString([(pcbnew.ToMM(s_.x), -pcbnew.ToMM(s_.y)), (pcbnew.ToMM(e_.x), -pcbnew.ToMM(e_.y))]).buffer(pcbnew.ToMM(t.GetWidth()) / 2, 6)]
            for p in geo:
                m = trimesh.creation.extrude_polygon(p, 0.035); m.apply_translation([0, 0, z0]); meshes['copper'].append(m)
    out = []
    for k, col in (('gold', GOLD), ('copper', COPPER)):
        if meshes[k]:
            m = trimesh.util.concatenate(meshes[k])
            m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
                baseColorFactor=col, metallicFactor=0.8, roughnessFactor=0.35))
            out.append((k, m))
    return out

def build(step, pcb, glb, thickness=1.0):
    sc = convert(step, glb)
    for k, m in overlay(pcb, thickness):
        sc.add_geometry(m, node_name=k)
    sc.export(glb)
    return sc

if __name__ == '__main__':
    sc = build(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 1.0)
    print('ok', len(sc.geometry), sc.bounds.round(2).tolist())
