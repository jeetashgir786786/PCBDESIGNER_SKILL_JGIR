#!/usr/bin/env python3
"""Run DRC and summarise the report.

usage: python3 drc.py <board.kicad_pcb> [report.rpt] [--refill]
Prints counts per violation type and severity, unconnected nets, and exits 1 if errors or unconnected items remain.
Uses pcbnew.WriteDRCReport (works on KiCad 7+). On KiCad 8+ you can cross-check with
`kicad-cli pcb drc --schematic-parity --severity-all`."""
import sys, os, re
from collections import Counter

HDR = re.compile(r'^\[(\w+)\]: (.*)$')
SEV = re.compile(r'Severity: (\w+)')
ITEM = re.compile(r'@\(([-\d.]+) mm, ([-\d.]+) mm\): (.*)$')
NET = re.compile(r'\[([^\]]+)\]')


def parse(rpt):
    """-> list of dict(type, msg, severity, items=[(x, y, text)])"""
    out, cur = [], None
    for line in open(rpt):
        line = line.rstrip('\n')
        m = HDR.match(line)
        if m:
            cur = dict(type=m.group(1), msg=m.group(2), severity='error', items=[]); out.append(cur); continue
        if cur is None:
            continue
        m = SEV.search(line)
        if m:
            cur['severity'] = m.group(1); continue
        m = ITEM.search(line)
        if m:
            cur['items'].append((float(m.group(1)), float(m.group(2)), m.group(3)))
    return out


def summary(rpt):
    v = parse(rpt)
    by = Counter((x['type'], x['severity']) for x in v)
    unconn = [x for x in v if x['type'] == 'unconnected_items']
    nets = Counter()
    for u in unconn:
        for _, _, t in u['items'][:1]:
            m = NET.search(t)
            if m:
                nets[m.group(1)] += 1
    errors = sum(n for (t, s), n in by.items() if s == 'error' and t != 'unconnected_items')
    return dict(by=by, unconnected=len(unconn), unconnected_nets=dict(nets), errors=errors,
                warnings=sum(n for (t, s), n in by.items() if s == 'warning'), violations=v)


def fmt(s):
    parts = [f"unconnected={s['unconnected']}", f"errors={s['errors']}", f"warnings={s['warnings']}"]
    if s['by']:
        parts.append('; '.join(f'{t}/{sev}:{n}' for (t, sev), n in sorted(s['by'].items())))
    return '  '.join(parts)


def run(pcb, rpt=None, refill=True):
    import pcbnew
    b = pcbnew.LoadBoard(pcb)
    if refill:
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(pcb, b)
    if rpt is None:
        d = os.path.join(os.path.dirname(os.path.abspath(pcb)), 'docs'); os.makedirs(d, exist_ok=True)
        rpt = os.path.join(d, os.path.basename(pcb).replace('.kicad_pcb', '_DRC.rpt'))
    pcbnew.WriteDRCReport(b, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
    return rpt, summary(rpt)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.exit(__doc__)
    if args[0].endswith('.rpt'):
        s = summary(args[0]); rpt = args[0]
    else:
        rpt, s = run(args[0], args[1] if len(args) > 1 else None, refill='--no-refill' not in sys.argv)
    print(rpt)
    print(fmt(s))
    if s['unconnected_nets']:
        print('unconnected nets:', s['unconnected_nets'])
    sys.exit(1 if (s['errors'] or s['unconnected']) else 0)
