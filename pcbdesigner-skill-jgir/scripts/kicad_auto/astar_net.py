"""Grid A* finisher for the last few connections an autorouter leaves open.
Obstacles = other-net copper inflated by clearance + board edge + rule areas + NPTH; zones are ignored
(refill afterwards). Commits tracks/vias with the given width/via size, then saves.

usage: RES=0.05 W=0.15 CLR=0.15 VIA_D=0.45 VIA_DR=0.2 python3 astar_net.py <board> NET1,NET2 [F.Cu,In2.Cu,B.Cu]
RES = grid (mm); smaller finds tighter gaps but is slower. Default layers: all signal copper layers."""
import sys, os, heapq, math
import numpy as np
from PIL import Image, ImageDraw
import pcbnew

pcb = sys.argv[1]
layers_allowed = sys.argv[3].split(',') if len(sys.argv) > 3 else None
HCLR = float(os.environ.get("HCLR", 0.25)); H2H = float(os.environ.get("H2H", 0.25))  # hole clearance, hole-to-hole
RES = float(os.environ.get("RES", 0.05)); W = float(os.environ.get("W", 0.15)); CLR = float(os.environ.get("CLR", 0.15)); VIA_D = float(os.environ.get("VIA_D", 0.45)); VIA_DR = float(os.environ.get("VIA_DR", 0.2))
b = pcbnew.LoadBoard(pcb)
ALL = ['F.Cu'] + [f'In{k}.Cu' for k in range(1, 31)] + ['B.Cu']
LID = {n: b.GetLayerID(n) for n in ALL if b.GetLayerID(n) >= 0 and b.IsLayerEnabled(b.GetLayerID(n))}
LAY = [l for l in (layers_allowed or list(LID)) if l in LID]
bb = b.GetBoardEdgesBoundingBox()
X0, Y0 = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop())
NX = int(pcbnew.ToMM(bb.GetWidth()) / RES) + 1; NY = int(pcbnew.ToMM(bb.GetHeight()) / RES) + 1
def g(x, y): return int(round((x - X0) / RES)), int(round((y - Y0) / RES))
def w(i, j): return float(X0 + int(i) * RES), float(Y0 + int(j) * RES)

NETS = sys.argv[2].split(',')
items = []  # (net, layerset, polyset)
def add_item(net, obj):
    for ln in LAY:
        L = LID[ln]
        if not obj.IsOnLayer(L): continue
        items.append((net, ln, obj))
for fp in b.GetFootprints():
    for p in fp.Pads(): add_item(p.GetNetname(), p)
for t in b.GetTracks(): add_item(t.GetNetname(), t)

def poly_pts(ps):
    out = []
    for k in range(ps.OutlineCount()):
        o = ps.Outline(k)
        out.append([((pcbnew.ToMM(o.CPoint(i).x) - X0) / RES, (pcbnew.ToMM(o.CPoint(i).y) - Y0) / RES) for i in range(o.PointCount())])
    return out


def draw_obj(d, obj, L, inflate):
    """rasterise one copper object (inflated) in grid coords"""
    if obj.Type() in (pcbnew.PCB_TRACE_T, pcbnew.PCB_ARC_T):
        s, e = obj.GetStart(), obj.GetEnd()
        r = pcbnew.ToMM(obj.GetWidth()) / 2 + inflate
        p0 = ((pcbnew.ToMM(s.x) - X0) / RES, (pcbnew.ToMM(s.y) - Y0) / RES); p1 = ((pcbnew.ToMM(e.x) - X0) / RES, (pcbnew.ToMM(e.y) - Y0) / RES)
        d.line([p0, p1], fill=1, width=max(1, int(round(2 * r / RES))))
        for p in (p0, p1): d.ellipse([p[0] - r / RES, p[1] - r / RES, p[0] + r / RES, p[1] + r / RES], fill=1)
        return
    if obj.Type() == pcbnew.PCB_VIA_T:
        c = obj.GetPosition(); r = pcbnew.ToMM(obj.GetWidth()) / 2 + inflate
        p = ((pcbnew.ToMM(c.x) - X0) / RES, (pcbnew.ToMM(c.y) - Y0) / RES)
        d.ellipse([p[0] - r / RES, p[1] - r / RES, p[0] + r / RES, p[1] + r / RES], fill=1); return
    ps = pcbnew.SHAPE_POLY_SET()
    obj.TransformShapeToPolygon(ps, L, pcbnew.FromMM(inflate), pcbnew.FromMM(0.01))
    for pts in poly_pts(ps):
        if len(pts) > 2: d.polygon(pts, fill=1)

def raster(net_exclude, inflate):
    maps = {}
    for ln in LAY:
        im = Image.new('1', (NX, NY), 0); d = ImageDraw.Draw(im)
        for (net, l2, obj) in items:
            if l2 != ln or (net == net_exclude and net != ''): continue
            draw_obj(d, obj, LID[ln], inflate)
        # NPTH / drilled holes block all layers
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    c = p.GetPosition(); r = pcbnew.ToMM(p.GetDrillSize().x) / 2 + inflate - CLR + max(CLR, HCLR)
                    cx, cy = (pcbnew.ToMM(c.x) - X0) / RES, (pcbnew.ToMM(c.y) - Y0) / RES
                    d.ellipse([cx - r / RES, cy - r / RES, cx + r / RES, cy + r / RES], fill=1)
        a = np.array(im, dtype=bool)
        e = int(math.ceil((float(os.environ.get('EDGE', 0.3)) + W / 2) / RES))  # board edge clearance
        a[:e, :] = a[-e:, :] = True; a[:, :e] = a[:, -e:] = True
        maps[ln] = a
    # rule areas (keepouts)
    for i in range(b.GetAreaCount()):
        z = b.GetArea(i)
        if z.GetIsRuleArea():
            r = z.GetBoundingBox()
            i0, j0 = g(pcbnew.ToMM(r.GetLeft()) - inflate, pcbnew.ToMM(r.GetTop()) - inflate)
            i1, j1 = g(pcbnew.ToMM(r.GetRight()) + inflate, pcbnew.ToMM(r.GetBottom()) + inflate)
            for ln in LAY:
                maps[ln][max(j0, 0):max(j1, 0), max(i0, 0):max(i1, 0)] = True
    return maps

def target_mask(net, ln):
    im = Image.new('1', (NX, NY), 0); d = ImageDraw.Draw(im)
    for (n, l2, obj) in items:
        if n != net or l2 != ln: continue
        draw_obj(d, obj, LID[ln], 0)
    return np.array(im, dtype=bool)

def obj_mask(x, y, ln, net):
    """mask of the specific copper object under point (x,y) on layer"""
    best = None
    for (n, l2, obj) in items:
        if n != net or l2 != ln: continue
        if obj.HitTest(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)), pcbnew.FromMM(0.02)):
            best = obj; break
    if best is None: return None
    im = Image.new('1', (NX, NY), 0); d = ImageDraw.Draw(im)
    draw_obj(d, best, LID[ln], 0)
    return np.array(im, dtype=bool)

TOUCH = int(os.environ.get('TOUCH', 4))  # min overlapping cells to treat a pad as connected
NB = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
LCOST = {l: (1.0 if l in ('F.Cu', 'B.Cu') else 2.5) for l in LAY}
VIACOST = 30

def holes_map():
    """cells where a new via's drill would violate hole-to-hole spacing (all nets, incl. its own)"""
    im = Image.new('1', (NX, NY), 0); d = ImageDraw.Draw(im)
    def disc(c, dr):
        r = dr / 2 + VIA_DR / 2 + H2H + max(0.02, RES)
        x, y = (pcbnew.ToMM(c.x) - X0) / RES, (pcbnew.ToMM(c.y) - Y0) / RES
        d.ellipse([x - r / RES, y - r / RES, x + r / RES, y + r / RES], fill=1)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                disc(p.GetPosition(), pcbnew.ToMM(min(p.GetDrillSize().x, p.GetDrillSize().y)))
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            disc(t.GetPosition(), pcbnew.ToMM(t.GetDrillValue()))
    return np.array(im, dtype=bool)


def geom_ok(path, net):
    """exact check with KiCad's own hit-testing: every new via and track sample keeps CLR to other-net copper"""
    others = [(ln, o) for (n, ln, o) in items if n != net]
    eps = 0.001
    def free(x, y, ln, r):
        pt = pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
        for (l2, o) in others:
            if (ln is None or l2 == ln) and o.HitTest(pt, pcbnew.FromMM(r + CLR - eps)):
                return False
        return True
    for k in range(1, len(path)):
        a, c = path[k - 1], path[k]
        if a[2] != c[2]:                                     # via at a
            x, y = w(a[0], a[1])
            if not free(x, y, None, VIA_D / 2):
                return False
            continue
        (x0, y0), (x1, y1) = w(a[0], a[1]), w(c[0], c[1])
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / (RES / 2)))
        for q in range(n + 1):
            if not free(x0 + (x1 - x0) * q / n, y0 + (y1 - y0) * q / n, a[2], W / 2):
                return False
    return True


def _vias_ok(path):
    """reject paths whose own vias sit closer than the hole-to-hole rule"""
    v = [path[k] for k in range(1, len(path)) if path[k][2] != path[k - 1][2]]
    for a in range(len(v)):
        for c in range(a + 1, len(v)):
            if math.hypot(v[a][0] - v[c][0], v[a][1] - v[c][1]) * RES < VIA_DR + H2H + 0.02:
                return False
    return True


def _clear(a, b, obs, goal):
    """straight run a->b on one layer stays out of the inflated obstacle map (goal copper allowed)"""
    ln = a[2]; n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
    for k in range(n + 1):
        x = a[0] + (b[0] - a[0]) * k / n; y = a[1] + (b[1] - a[1]) * k / n
        for i in {math.floor(x), math.ceil(x)}:          # conservative: every cell the true point can touch
            for j in {math.floor(y), math.ceil(y)}:
                if obs[ln][j, i] and not (ln in goal and goal[ln][j, i]):
                    return False
    return True


def smooth(path, obs, goal):
    """string-pulling: replace grid staircases by the longest obstacle-free straight runs (per layer)"""
    out = [path[0]]; k = 0
    while k < len(path) - 1:
        best = k + 1
        for m in range(len(path) - 1, k, -1):
            if path[m][2] == path[k][2] and all(p[2] == path[k][2] for p in path[k:m + 1]) and _clear(path[k], path[m], obs, goal):
                best = m; break
        out.append(path[best]); k = best
    return out


def astar(net, start_cells, goal, extra=0.0):
    obs = raster(net, CLR + W / 2 + max(0.02, RES) + extra)
    vobs = raster(net, CLR + VIA_D / 2 + max(0.02, RES) + extra)
    via_ok = np.ones((NY, NX), dtype=bool)
    for ln in LAY: via_ok &= ~vobs[ln]
    via_ok &= ~holes_map()
    gl = [np.argwhere(goal[ln]) for ln in goal if goal[ln].any()]
    allg = np.vstack(gl); gy, gx = allg[:, 0].mean(), allg[:, 1].mean()
    def h(i, j): return 0.6 * math.hypot(i - gx, j - gy)
    openq = []; best = {}; prev = {}
    for s in start_cells:
        best[s] = 0; heapq.heappush(openq, (h(s[0], s[1]), 0, s))
    n = 0
    while openq:
        f, cst, s = heapq.heappop(openq); n += 1
        if n > 3000000: return None
        if cst > best.get(s, 1e18): continue
        i, j, ln = s
        if ln in goal and goal[ln][j, i]:
            path = [s]
            while path[-1] in prev: path.append(prev[path[-1]])
            return smooth(path[::-1], obs, goal)
        for di, dj, dc in NB:
            ni, nj = i + di, j + dj
            if not (0 <= ni < NX and 0 <= nj < NY): continue
            if obs[ln][nj, ni] and not (ln in goal and goal[ln][nj, ni]): continue
            ns = (ni, nj, ln); nc = cst + dc * LCOST[ln]
            if nc < best.get(ns, 1e18):
                best[ns] = nc; prev[ns] = s; heapq.heappush(openq, (nc + h(ni, nj), nc, ns))
        if via_ok[j, i]:
            for l2 in LAY:
                if l2 == ln or obs[l2][j, i]: continue
                ns = (i, j, l2); nc = cst + VIACOST
                if nc < best.get(ns, 1e18):
                    best[ns] = nc; prev[ns] = s; heapq.heappush(openq, (nc + h(i, j), nc, ns))
    return None

def objmask(obj, ln):
    im = Image.new('1', (NX, NY), 0); d = ImageDraw.Draw(im); draw_obj(d, obj, LID[ln], 0)
    return np.array(im, dtype=bool)

nets0 = b.GetNetsByName(); nets = {str(k): nets0[k] for k in nets0.keys()}
def commit(path, net):
    out = []; seg_start = path[0]; prevd = None
    for k in range(1, len(path)):
        p0, p1 = path[k - 1], path[k]
        if p1[2] != p0[2]:
            if (seg_start[0], seg_start[1]) != (p0[0], p0[1]): out.append(('t', seg_start, p0))
            out.append(('v', p0)); seg_start = p1; prevd = None; continue
        d = (p1[0] - p0[0], p1[1] - p0[1])
        if prevd is not None and d != prevd: out.append(('t', seg_start, p0)); seg_start = p0
        prevd = d
    if (seg_start[0], seg_start[1]) != (path[-1][0], path[-1][1]): out.append(('t', seg_start, path[-1]))
    for it in out:
        if it[0] == 't':
            s0, s1 = it[1], it[2]
            t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(*[pcbnew.FromMM(v) for v in w(s0[0], s0[1])]))
            t.SetEnd(pcbnew.VECTOR2I(*[pcbnew.FromMM(v) for v in w(s1[0], s1[1])])); t.SetWidth(pcbnew.FromMM(W))
            t.SetLayer(LID[s0[2]]); t.SetNet(nets[net]); b.Add(t); add_item(net, t)
        else:
            p0 = it[1]
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(*[pcbnew.FromMM(q) for q in w(p0[0], p0[1])]))
            v.SetWidth(pcbnew.FromMM(VIA_D)); v.SetDrill(pcbnew.FromMM(VIA_DR)); v.SetNet(nets[net]); b.Add(v); add_item(net, v)
    return len(out)

fails = 0
for net in NETS:
    pads = [(p, ln) for (n, ln, p) in items if n == net and p.Type() == pcbnew.PCB_PAD_T]
    # group pads into physical pads (one entry per pad object, list layers)
    objs = {}
    for p, ln in pads: objs.setdefault(id(p), [p, []])[1].append(ln)
    plist = list(objs.values())
    # existing copper of this net forms the initial connected set together with the first pad
    conn = {ln: np.zeros((NY, NX), dtype=bool) for ln in LAY}
    for (n, ln, o) in items:
        if n == net and o.Type() != pcbnew.PCB_PAD_T: conn[ln] |= objmask(o, ln)
    p0, l0 = plist[0]
    for ln in l0: conn[ln] |= objmask(p0, ln)
    # iteratively connect pads not already touching conn
    remaining = plist[1:]
    while remaining:
        # pick the pad closest to the connected set centroid
        def touching(pp):
            p, ls = pp
            return any((objmask(p, ln) & conn[ln]).sum() >= TOUCH for ln in ls)
        newr = []
        for pp in remaining:
            if touching(pp):
                for ln in pp[1]: conn[ln] |= objmask(pp[0], ln)
            else: newr.append(pp)
        remaining = newr
        if not remaining: break
        pp = remaining.pop(0)
        p, ls = pp
        starts = []
        for ln in ls:
            m = objmask(p, ln)
            for (j, i) in np.argwhere(m)[::2]: starts.append((int(i), int(j), ln))
        path = None
        for extra in (0.0, RES, 2 * RES):                     # widen the raster margin if the exact check fails
            path = astar(net, starts, conn, extra)
            if path and not _vias_ok(path):
                print('  rejected path with stacked vias', net); path = None
            if path and not geom_ok(path, net):
                print(f'  path too close to other copper at margin +{extra:.3f} mm, retrying', net); path = None
                continue
            break
        if not path:
            print('FAILED', net, p.GetNumber(), [round(pcbnew.ToMM(v),2) for v in (p.GetPosition().x, p.GetPosition().y)], 'starts', len(starts), 'conn', {k: int(v.sum()) for k, v in conn.items()}); fails += 1
            for ln in ls: conn[ln] |= objmask(p, ln)
            continue
        commit(path, net)
        for a_, b_ in zip(path, path[1:]):          # mark the committed runs (path holds only vertices now)
            if a_[2] != b_[2]: continue
            n_ = int(max(abs(b_[0] - a_[0]), abs(b_[1] - a_[1]))) + 1
            for k_ in range(n_ + 1):
                i = int(round(a_[0] + (b_[0] - a_[0]) * k_ / n_)); j = int(round(a_[1] + (b_[1] - a_[1]) * k_ / n_))
                conn[a_[2]][max(j-1,0):j+2, max(i-1,0):i+2] = True
        for ln in ls: conn[ln] |= objmask(p, ln)
    print('net done', net)
print('fails', fails)
pcbnew.SaveBoard(pcb, b)
