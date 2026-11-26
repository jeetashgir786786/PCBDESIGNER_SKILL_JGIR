"""Remove duplicate tracks/vias (same geometry) - happens when an autorouter pass is imported over kept copper.
usage: python3 dedupe.py <board.kicad_pcb>"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
seen = set(); dup = []
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        k = ('v', t.GetPosition().x, t.GetPosition().y)
    else:
        s, e = t.GetStart(), t.GetEnd()
        a, c = sorted([(s.x, s.y), (e.x, e.y)])
        k = ('t', t.GetLayer(), a, c, t.GetWidth())
    if k in seen: dup.append(t)
    else: seen.add(k)
for t in dup: b.Remove(t)
# zero-length segments
z = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetStart() == t.GetEnd()]
for t in z: b.Remove(t)
pcbnew.SaveBoard(sys.argv[1], b)
print('duplicates removed', len(dup), 'zero-length removed', len(z))
