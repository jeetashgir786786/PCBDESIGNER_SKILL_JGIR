"""Convert a coloured STEP (KiCad export) into a GLB mesh scene (one mesh per colour) with OCP + trimesh."""
import sys, numpy as np, trimesh
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.Quantity import Quantity_Color
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from OCP.IFSelect import IFSelect_RetDone

def read(path):
    doc = TDocStd_Document(TCollection_ExtendedString('doc'))
    r = STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True)
    assert r.ReadFile(path) == IFSelect_RetDone
    r.Transfer(doc)
    return doc

def color_of(ct, lab, shape):
    c = Quantity_Color()
    for t in (XCAFDoc_ColorType.XCAFDoc_ColorSurf, XCAFDoc_ColorType.XCAFDoc_ColorGen):
        ok = False
        try: ok = ct.GetColor(shape, t, c)
        except Exception: pass
        if not ok:
            try: ok = ct.GetColor_s(lab, t, c)
            except Exception: ok = False
        if ok:
            return (c.Red(), c.Green(), c.Blue())
    return None

def convert(step, out, defl=0.05, scale=1.0, offset=(0, 0, 0)):
    doc = read(step)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    buckets = {}
    def add_shape(shape, col):
        BRepMesh_IncrementalMesh(shape, defl, False, 0.5, True)
        exp = TopExp_Explorer(shape, TopAbs_FACE)
        while exp.More():
            f = TopoDS.Face_s(exp.Current())
            fc = col
            c = Quantity_Color()
            if ct.GetColor(f, XCAFDoc_ColorType.XCAFDoc_ColorSurf, c):
                fc = (c.Red(), c.Green(), c.Blue())
            loc = TopLoc_Location()
            tri = BRep_Tool.Triangulation_s(f, loc)
            if tri is not None:
                tr = loc.Transformation()
                n = tri.NbNodes()
                pts = np.array([[*(lambda p: (p.X(), p.Y(), p.Z()))(tri.Node(i).Transformed(tr))] for i in range(1, n + 1)])
                tris = np.array([list(tri.Triangle(i).Get()) for i in range(1, tri.NbTriangles() + 1)]) - 1
                if f.Orientation() == TopAbs_REVERSED:
                    tris = tris[:, [0, 2, 1]]
                key = tuple(round(v, 3) for v in (fc or (0.6, 0.6, 0.6)))
                buckets.setdefault(key, []).append((pts, tris))
            exp.Next()
    from OCP.TopTools import TopTools_IndexedMapOfShape
    from OCP.TopExp import TopExp
    def add_shape_styled(shape, loc, col, sub):
        BRepMesh_IncrementalMesh(shape, defl, False, 0.5, True)
        # map face -> colour from styled subshapes (faces, shells, solids)
        fmaps = []
        for ss, c in sub.items():
            m = TopTools_IndexedMapOfShape()
            TopExp.MapShapes_s(ss, TopAbs_FACE, m)
            fmaps.append((m, c))
        trf = loc.Transformation()
        exp = TopExp_Explorer(shape, TopAbs_FACE)
        while exp.More():
            f = TopoDS.Face_s(exp.Current())
            fc = col
            for m, c in fmaps:
                if m.Contains(f):
                    fc = c; break
            l2 = TopLoc_Location()
            tri = BRep_Tool.Triangulation_s(f, l2)
            if tri is not None:
                tr = l2.Transformation().Multiplied(trf) if False else trf.Multiplied(l2.Transformation())
                n = tri.NbNodes()
                pts = np.array([[*(lambda p: (p.X(), p.Y(), p.Z()))(tri.Node(i).Transformed(tr))] for i in range(1, n + 1)])
                tris = np.array([list(tri.Triangle(i).Get()) for i in range(1, tri.NbTriangles() + 1)]) - 1
                if f.Orientation() == TopAbs_REVERSED:
                    tris = tris[:, [0, 2, 1]]
                key = tuple(round(v, 2) for v in (fc or (0.6, 0.6, 0.6)))
                buckets.setdefault(key, []).append((pts, tris))
            exp.Next()
    def walk(lab, loc, inh):
        shape = st.GetShape_s(lab)
        col = color_of(ct, lab, shape) or inh
        if st.IsAssembly_s(lab):
            comps = TDF_LabelSequence(); st.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                cl = comps.Value(i)
                cloc = st.GetLocation_s(cl)
                ref = TDF_Label()
                st.GetReferredShape_s(cl, ref)
                ccol = color_of(ct, cl, st.GetShape_s(cl)) or col
                walk(ref, loc.Multiplied(cloc), ccol)
        else:
            if st.IsReference_s(lab):
                ref = TDF_Label(); st.GetReferredShape_s(lab, ref); walk(ref, loc, col); return
            s = shape.Moved(loc)
            # subshape colours
            add_shape(s, col)
    from OCP.XCAFPrs import XCAFPrs_DocumentExplorer, XCAFPrs_DocumentExplorerFlags_OnlyLeafNodes, XCAFPrs, XCAFPrs_IndexedDataMapOfShapeStyle
    from OCP.XCAFDoc import XCAFDoc_ShapeTool
    ex = XCAFPrs_DocumentExplorer(doc, XCAFPrs_DocumentExplorerFlags_OnlyLeafNodes)
    while ex.More():
        node = ex.Current()
        sty = node.Style
        col = None
        if sty.IsSetColorSurf():
            c = sty.GetColorSurf(); col = (c.Red(), c.Green(), c.Blue())
        shape = XCAFDoc_ShapeTool.GetShape_s(node.RefLabel)
        # per-subshape styles
        smap = XCAFPrs_IndexedDataMapOfShapeStyle()
        try:
            XCAFPrs.CollectStyleSettings_s(node.RefLabel, TopLoc_Location(), smap)
        except Exception:
            smap = None
        sub = {}
        if smap is not None:
            for i in range(1, smap.Extent() + 1):
                ss = smap.FindKey(i); st2 = smap.FindFromIndex(i)
                if st2.IsSetColorSurf():
                    c = st2.GetColorSurf(); sub[ss] = (c.Red(), c.Green(), c.Blue())
        add_shape_styled(shape, node.Location, col, sub)
        ex.Next()
    scene = trimesh.Scene()
    for k, parts in buckets.items():
        vs, fs, off = [], [], 0
        for p, t in parts:
            vs.append(p); fs.append(t + off); off += len(p)
        m = trimesh.Trimesh(np.vstack(vs) * scale + np.array(offset), np.vstack(fs), process=False)
        rgba = [int(255 * c) for c in k] + [255]
        m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=rgba, metallicFactor=0.3 if sum(k) > 2.2 else 0.05, roughnessFactor=0.55))
        scene.add_geometry(m, node_name=f'c_{len(scene.geometry)}')
    scene.export(out)
    return scene

if __name__ == '__main__':
    s = convert(sys.argv[1], sys.argv[2])
    print('meshes', len(s.geometry), 'bounds', s.bounds.round(2).tolist())
