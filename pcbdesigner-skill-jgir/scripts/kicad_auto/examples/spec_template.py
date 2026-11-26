"""Design-spec template for build.py. Copy, rename, fill in. Every field below is read by build.py.

Conventions
- Coordinates are mm relative to BOARD['origin'] (board centre); KiCad y points DOWN.
- place=(x, y, rotation_deg, 'F'|'B'). Bottom parts are flipped first, then rotated.
- pins maps PAD NUMBERS (as in the footprint) to net names. Pins not listed get a no-connect flag.
  Check pad numbers against the footprint, not the datasheet pin names (libsym.py Lib:Symbol prints them).
- Symbols: 'Lib:Name' from the KiCad libraries, or '<LIB>:<name>' for CUSTOM_SYMBOLS.
- Footprints: 'Lib:Name' from the KiCad libraries, or '<LIB>:<name>' written by custom_footprints().
- lcsc_ok=True only after you have checked the part number and stock on jlcpcb.com/parts.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from parts import R, C, LED, FLAG, C0603, C0805        # passive helpers (R0402/C0402 defaults)
from sch_gen import custom_symbol                       # for parts with no KiCad library symbol
import fpgen                                            # for simple custom pad footprints

NAME = 'My_Board'                 # file names
TITLE = 'My board - one line description'
COMPANY = ''
REV = 'A'
LIB = 'proj'                      # project library nickname (symbols + footprints + 3D shapes)
PAPER = 'A3'                      # A4 / A3 / A2 / A1 (bigger designs need A2)
NOTES = ['free text printed on the schematic']

CUSTOM_SYMBOLS = {
    # 'MY_IC': custom_symbol('MY_IC', left=[('1', 'VIN', 'power_in'), ('2', 'EN', 'input')],
    #                        right=[('5', 'VOUT', 'power_out')], bottom=[('3', 'GND', 'power_in')],
    #                        fp='Package_TO_SOT_SMD:SOT-23-5', desc='...'),
}


def custom_footprints(libdir):
    """Optional. Example: two battery solder pads."""
    # fpgen.write_fp(libdir, 'BatPads', [dict(num='1', x=-3, y=0, w=2, h=3), dict(num='2', x=3, y=0, w=2, h=3)],
    #                (-4.25, -1.75, 4.25, 1.75), 'battery pads', silk_labels=[('+', -3, -2.4)])
    pass


def parts():
    P = []; a = P.append  # noqa: F841  (used by the commented examples below)
    # a(dict(ref='U1', sym='Regulator_Linear:AMS1117-3.3', value='AMS1117-3.3', fp='Package_TO_SOT_SMD:SOT-223-3_TabPin2',
    #        lcsc='C6186', lcsc_ok=False, mpn='AMS1117-3.3', pins={'1': 'GND', '2': '3V3', '3': 'VIN'},
    #        group='Power', place=(0, 0, 0, 'F')))
    # a(C('C1', '10uF', 'VIN', 'GND', 'Power', C0603, place=(-4, 0, 90, 'F')))
    # optional keys: dnp=True, nobom=True, hand=True (BOM 'hand solder', left out of CPL), strip_vias=True,
    #                virtual=True (schematic only, e.g. FLAG('#FLG1', 'VIN'))
    return P


BOARD = dict(
    layers=2,                              # 2, 4, 6 ...
    thickness=1.6,                         # mm
    fab='jlcpcb',                          # rule preset in fab_rules.py (jlcpcb / pcbway)
    finish='HASL(with lead)',              # or 'ENIG'
    outline=dict(w=40, h=30, r=2),         # rounded rectangle; or dict(poly=[(x, y), ...])
    origin=(100, 100),
    zones=[dict(net='GND', layer='F.Cu'), dict(net='GND', layer='B.Cu')],
    # 4-layer: add dict(net='GND', layer='In1.Cu'), dict(net='3V3', layer='In2.Cu')  -> route.py fans these out
    keepouts=[],                           # dict(pts=[(x, y), ...], layers=['F.Cu', 'B.Cu'])  e.g. antenna area
    classes=[dict(name='Default', clearance=0.2, track=0.2),
             dict(name='Power', clearance=0.2, track=0.4)],   # via size defaults per layer count (fab_rules.DEFAULT_VIA)
    patterns=[('Power', 'VIN'), ('Power', '3V3')],             # netclass assignment by net-name pattern (wildcards ok)
    rules_override={},                     # e.g. dict(min_copper_edge_clearance=0.5)
    model_subst={},                        # {footprint_name: ('file.step' in <LIB>.3dshapes, z_rot)}
    box_models={},                         # {footprint_name: (height, (r, g, b), has_actuator)} placeholder bodies
)
