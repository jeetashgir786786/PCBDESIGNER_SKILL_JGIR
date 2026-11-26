"""Rip up all unlocked tracks/vias of the given nets. usage: python3 ripup.py <board> NET1,NET2"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); nets = set(sys.argv[2].split(','))
rm = [t for t in b.GetTracks() if t.GetNetname() in nets and not t.IsLocked()]
for t in rm: b.Remove(t)
pcbnew.SaveBoard(sys.argv[1], b)
print('ripped', len(rm))
