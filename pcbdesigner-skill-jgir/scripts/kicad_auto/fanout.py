"""Plane fan-out: add a short locked stub + via from every SMD pad of the given plane nets so pads reach the
inner planes (Freerouting does not connect pads to zones). Collision checks against pads, other vias, rule
areas and the board edge. Run on a board WITHOUT routed tracks (it removes existing tracks).

usage: VIA_D=0.45 VIA_DR=0.2 CLR=0.15 python3 fanout.py <board.kicad_pcb> GND,VBAT"""
import sys, os, math
import pcbnew
pcb = sys.argv[1]; plane_nets = sys.argv[2].split(',')
VIA_D, VIA_DR, CLR = float(os.environ.get("VIA_D", 0.45)), float(os.environ.get("VIA_DR", 0.2)), float(os.environ.get("CLR", 0.15))
b = pcbnew.LoadBoard(pcb)
bb = b.GetBoardEdgesBoundingBox()
X0, Y0, X1, Y1 = [pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())]
pads = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        bx = p.GetBoundingBox()
        pads.append((p, (fp.GetReference(), p.GetNumber(), pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y), p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD), pcbnew.ToMM(bx.GetLeft()), pcbnew.ToMM(bx.GetTop()), pcbnew.ToMM(bx.GetRight()), pcbnew.ToMM(bx.GetBottom()),
                     p.GetNetname(), p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH), p.IsOnLayer(pcbnew.F_Cu), p.IsOnLayer(pcbnew.B_Cu)))
# keepouts / courtyard of the bottom module body: forbid vias under exposed parts is fine; avoid rule areas
rules = []
for i in range(b.GetAreaCount()):
    z = b.GetArea(i)
    if z.GetIsRuleArea():
        r = z.GetBoundingBox(); rules.append([pcbnew.ToMM(v) for v in (r.GetLeft(), r.GetTop(), r.GetRight(), r.GetBottom())])
vias = []
segs = []
nets0 = b.GetNetsByName(); nets = {str(k): nets0[k] for k in nets0.keys()}
for t in list(b.GetTracks()):
    b.Remove(t)
def box_dist(x, y, x0, y0, x1, y1):
    dx = max(x0 - x, 0, x - x1); dy = max(y0 - y, 0, y - y1); return math.hypot(dx, dy)
def seg_box_clear(ax, ay, bx_, by, box, need):
    for k in range(11):
        t = k / 10; x = ax + (bx_ - ax) * t; y = ay + (by - ay) * t
        if box_dist(x, y, *box) < need: return False
    return True
def ok(x, y, net, src_pad, sx, sy, w, src_f):
    if x < X0 + 0.8 or x > X1 - 0.8 or y < Y0 + 0.8 or y > Y1 - 0.8: return False
    for r in rules:
        if box_dist(x, y, *r) < VIA_D: return False
    for (p, fp, x0, y0, x1, y1, n, th, f, bk) in pads:
        d = box_dist(x, y, x0, y0, x1, y1)
        if p == src_pad: continue
        if n == net and d >= 0.05 and not th: continue  # same-net SMD pad: allow close but not on top
        if d < VIA_D / 2 + CLR + (0.05 if n != net else 0): return False
        if n != net and (f and src_f or bk and not src_f):
            if not seg_box_clear(sx, sy, x, y, (x0, y0, x1, y1), w / 2 + CLR): return False
    for (vx, vy, n) in vias:
        if math.hypot(x - vx, y - vy) < VIA_D + CLR: return False
    return True
added = 0; failed = []
for (p, fp, x0, y0, x1, y1, n, th, f, bk) in pads:
    ref, num, fx, fy, smd = fp
    if n not in plane_nets or th or not smd:
        continue
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = math.atan2(cy - fy, cx - fx) if (abs(cy - fy) + abs(cx - fx)) > 0.05 else 0
    hw = max(x1 - x0, y1 - y0) / 2
    w = 0.35
    placed = False
    for r in (hw + 0.55, hw + 0.8, hw + 1.1, hw + 1.5, hw + 2.0):
        for k in range(16):
            a = out + (k // 2) * (math.pi / 8) * (1 if k % 2 == 0 else -1)
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            if ok(x, y, n, p, cx, cy, w, f):
                v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
                v.SetWidth(pcbnew.FromMM(VIA_D)); v.SetDrill(pcbnew.FromMM(VIA_DR)); v.SetNet(nets[n]); v.SetLocked(True); b.Add(v)
                L = pcbnew.F_Cu if f else pcbnew.B_Cu
                t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy)))
                t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))); t.SetWidth(pcbnew.FromMM(w)); t.SetLayer(L)
                t.SetNet(nets[n]); t.SetLocked(True); b.Add(t)
                vias.append((x, y, n)); added += 1; placed = True; break
        if placed: break
    if not placed: failed.append(f'{ref}.{num}')
pcbnew.SaveBoard(pcb, b)
print('fanout vias', added, 'failed', failed)
