"""Import a Freerouting .ses (wires + vias) into a KiCad board (KiCad 7 python lacks a board-arg SES importer)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
from sexp import parse, find
def imp(board, ses, nets=None):
    S = parse(open(ses).read())[0]
    routes = find(S, 'routes')[0]
    res = find(routes, 'resolution')[0]; div = float(res[2])
    scale = {'um': 1e-3, 'mm': 1.0, 'mil': 0.0254, 'inch': 25.4}[res[1]] / div
    lay = {board.GetLayerName(l): l for l in range(pcbnew.PCB_LAYER_ID_COUNT) if board.IsLayerEnabled(l)}
    vias = {}
    for ps in find(find(routes, 'library_out')[0], 'padstack') if find(routes, 'library_out') else []:
        nm = ps[1].strip('"'); shp = find(ps, 'shape')[0][1]
        dia = float(shp[2]) * scale
        import re; m = re.search(r'(\d+):(\d+)_um', nm)
        drill = float(m.group(2)) / 1000 if m else 0.3
        vias[nm] = (dia, drill)
    nets = nets if nets is not None else board.GetNetsByName()
    nt = nv = 0
    for net in find(find(routes, 'network_out')[0], 'net'):
        name = net[1].strip('"')
        ni = nets[name] if name in nets else None
        for w in find(net, 'wire'):
            p = find(w, 'path')[0]
            L = lay[p[1].strip('"')]; wd = float(p[2]) * scale
            pts = [(float(p[i]) * scale, -float(p[i + 1]) * scale) for i in range(3, len(p) - 1, 2)]
            for a, b in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a[0]), pcbnew.FromMM(a[1])))
                t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(b[0]), pcbnew.FromMM(b[1])))
                t.SetWidth(pcbnew.FromMM(wd)); t.SetLayer(L)
                if ni: t.SetNet(ni)
                board.Add(t); nt += 1
        for v in find(net, 'via'):
            nm = v[1].strip('"'); dia, drill = vias.get(nm, (0.6, 0.3))
            vv = pcbnew.PCB_VIA(board)
            vv.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(float(v[2]) * scale), pcbnew.FromMM(-float(v[3]) * scale)))
            vv.SetWidth(pcbnew.FromMM(dia)); vv.SetDrill(pcbnew.FromMM(drill)); vv.SetViaType(pcbnew.VIATYPE_THROUGH)
            vv.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            if ni: vv.SetNet(ni)
            board.Add(vv); nv += 1
    return nt, nv
if __name__ == '__main__':
    b = pcbnew.LoadBoard(sys.argv[1])
    for t in list(b.GetTracks()): b.Remove(t)
    print('tracks, vias', imp(b, sys.argv[2]))
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(sys.argv[1], b)
    pcbnew.WriteDRCReport(b, sys.argv[3], pcbnew.EDA_UNITS_MILLIMETRES, True)
