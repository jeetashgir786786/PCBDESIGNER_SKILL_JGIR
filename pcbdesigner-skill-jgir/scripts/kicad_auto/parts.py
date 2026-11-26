"""Part-dict helpers for design specs. LCSC numbers here are common JLCPCB 'basic' parts written from memory:
they are emitted with lcsc_ok=False so the BOM marks them UNVERIFIED until checked on jlcpcb.com/parts."""
R0402 = 'Resistor_SMD:R_0402_1005Metric'
R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0402 = 'Capacitor_SMD:C_0402_1005Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
LED0603 = 'LED_SMD:LED_0603_1608Metric'

RES = {'10k': 'C25744', '100k': 'C25741', '5.1k': 'C25905', '4.7k': 'C25900', '1k': 'C11702',
       '22': 'C25092', '10': 'C25077', '2k': 'C4109', '47k': 'C25819', '0': 'C17168'}
CAP = {('100nF', C0402): 'C1525', ('1uF', C0402): 'C52923', ('10nF', C0402): 'C15195',
       ('2.2uF', C0402): 'C12530', ('10uF', C0603): 'C19702', ('22uF', C0805): 'C45783',
       ('4.7uF', C0603): 'C19666', ('22uF', C0603): 'C59461'}


def _size(fp):
    return fp.split(':')[1].split('_')[1]


def R(ref, val, a, b, group, fp=R0402, **kw):
    d = dict(ref=ref, sym='Device:R', value=val, fp=fp, lcsc=RES.get(val, '') if fp == R0402 else '', lcsc_ok=False,
             mpn=f'{val} 1% {_size(fp)}', pins={'1': a, '2': b}, group=group)
    d.update(kw); return d


def C(ref, val, a, b, group, fp=C0402, **kw):
    d = dict(ref=ref, sym='Device:C', value=val, fp=fp, lcsc=CAP.get((val, fp), ''), lcsc_ok=False,
             mpn=f'{val} X5R/X7R {_size(fp)}', pins={'1': a, '2': b}, group=group)
    d.update(kw); return d


def LED(ref, val, k, a, group, lcsc='', **kw):
    d = dict(ref=ref, sym='Device:LED', value=val, fp=LED0603, lcsc=lcsc, lcsc_ok=False, mpn=f'{val} LED 0603',
             pins={'1': k, '2': a}, group=group)
    d.update(kw); return d


def FLAG(ref, net):
    """PWR_FLAG for ERC on nets driven only by connectors/passives (schematic only)."""
    return dict(ref=ref, sym='power:PWR_FLAG', value='PWR_FLAG', fp='', pins={'1': net}, group='Power flags', virtual=True)
