"""Example design spec: USB-C to 3.3 V UART bridge (CH340C + AMS1117-3.3), 36 x 26 mm, JLCPCB PCBA.
Build:  python3 build.py examples/usb_uart_spec.py /tmp/usb_uart
Set LAYERS=4 in the environment to get a 4-layer variant (In1 = GND plane, In2 = 3V3 plane)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from parts import R, C, LED, C0603

NAME = 'USB_UART_Bridge'
TITLE = 'USB-C to 3.3 V UART bridge (CH340C)'
COMPANY = 'kicad_auto example'
LIB = 'proj'
PAPER = 'A3'
NOTES = ['CH340C runs from 3V3 (V3 tied to VCC) so TXD/RXD/DTR/CTS are 3.3 V logic']
LAYERS = int(os.environ.get('LAYERS', 2))


def parts():
    P = []; a = P.append
    a(dict(ref='J1', sym='Connector:USB_C_Receptacle_USB2.0_16P', value='USB-C', group='USB',
           fp='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12', lcsc='C165948', mpn='HRO TYPE-C-31-M-12',
           pins={'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS',
                 'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DN', 'B7': 'USB_DN', 'S1': 'GND'},
           place=(-14.6, 0, 270, 'F')))
    a(R('R1', '5.1k', 'CC1', 'GND', 'USB', place=(-7.6, -2.6, 0, 'F')))
    a(R('R2', '5.1k', 'CC2', 'GND', 'USB', place=(-7.6, 2.6, 0, 'F')))
    a(dict(ref='U2', sym='Regulator_Linear:AMS1117-3.3', value='AMS1117-3.3', group='3V3 LDO',
           fp='Package_TO_SOT_SMD:SOT-223-3_TabPin2', lcsc='C6186', mpn='AMS1117-3.3',
           pins={'1': 'GND', '2': '3V3', '3': 'VBUS'}, place=(-2.5, 8.5, 0, 'F')))
    a(C('C2', '10uF', 'VBUS', 'GND', '3V3 LDO', C0603, place=(-8.3, 9.0, 90, 'F')))
    a(C('C3', '10uF', '3V3', 'GND', '3V3 LDO', C0603, place=(2.8, 8.5, 90, 'F')))
    a(dict(ref='U1', sym='Interface_USB:CH340C', value='CH340C', group='USB-UART',
           fp='Package_SO:SOIC-16_3.9x9.9mm_P1.27mm', lcsc='C84681', mpn='WCH CH340C',
           pins={'1': 'GND', '2': 'TXD', '3': 'RXD', '4': '3V3', '5': 'USB_DP', '6': 'USB_DN',
                 '9': 'CTS', '13': 'DTR', '16': '3V3'},
           place=(4.0, -2.5, 0, 'F')))
    a(C('C1', '100nF', '3V3', 'GND', 'USB-UART', place=(9.3, -6.2, 90, 'F')))
    a(C('C4', '100nF', '3V3', 'GND', 'USB-UART', place=(-1.2, -4.2, 90, 'F')))
    a(R('R3', '1k', '3V3', 'LED_A', 'Status', place=(8.5, 6.0, 0, 'F')))
    a(LED('D1', 'GREEN', 'GND', 'LED_A', 'Status', place=(8.5, 8.5, 0, 'F')))
    a(dict(ref='J2', sym='Connector_Generic:Conn_01x06', value='UART 3V3', group='UART header',
           fp='Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical', mpn='2.54 mm 1x6 header (hand solder)',
           hand=True, pins={'1': 'GND', '2': 'CTS', '3': '3V3', '4': 'TXD', '5': 'RXD', '6': 'DTR'},
           place=(14.5, -6.35, 0, 'F')))
    return P


_full = None   # None = whole board outline
BOARD = dict(
    layers=LAYERS, thickness=1.6, fab='jlcpcb', finish='HASL(with lead)',
    outline=dict(w=36, h=26, r=1.5), origin=(100, 100),
    zones=[dict(net='GND', layer='F.Cu'), dict(net='GND', layer='B.Cu')] +
          ([dict(net='GND', layer='In1.Cu'), dict(net='3V3', layer='In2.Cu')] if LAYERS == 4 else []),
    classes=[dict(name='Default', clearance=0.2, track=0.2), dict(name='Power', clearance=0.2, track=0.4)],
    patterns=[('Power', 'VBUS'), ('Power', '3V3')],
    # KiCad 7 ships no 3D model for this USB-C footprint: generate a fit-check box from its F.Fab outline
    box_models={'USB_C_Receptacle_HRO_TYPE-C-31-M-12': (3.2, (0.78, 0.78, 0.8), False)},
)
