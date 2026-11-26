# Standards map (what to cite, when)

Revisions verified Nov 2026 where noted; check the Global Electronics Association (IPC) store / ANSI webstore for the current revision before citing on a drawing. Never quote a standard's table values as if they were verified unless you have the document; mark them "per IPC-xxxx (verify revision)".

## IPC design standards
| Standard | Scope |
|---|---|
| IPC-2221 (rev C, 2023) | Generic PCB design: spacing (Table 6-1), conductor sizing (legacy), holes, annular ring, materials |
| IPC-2222 | Rigid organic boards (sectional) |
| IPC-2223 (rev E) | Flex & rigid-flex design (bend radius, coverlay, transitions) |
| IPC-2226A (2017) | HDI design: construction types I–VI, microvia rules |
| IPC-2152 | Current-carrying capacity (replaces IPC-2221 charts) |
| IPC-2141A | Controlled-impedance design guide |
| IPC-2251 | High-speed circuit design guide |
| IPC-2231 | DFX guidelines |
| IPC-2581 (rev C) | Intelligent manufacturing data exchange |
| IPC-2610 series | Documentation (fab/assembly drawings) |
| IPC-7351B / IPC-7352 | Land pattern / footprint generic requirements and naming |
| IPC-7093 / IPC-7095 | Bottom-termination components (QFN) / BGA design & assembly |
| IPC-4761 | Via protection types I–VII |
| IPC-9592 | Power conversion devices (incl. spacing) |
| IPC-D-356 | Bare-board test netlist |

## IPC materials
IPC-4101 (rigid base materials, slash sheets), IPC-4103 (high-speed/high-frequency base materials), IPC-4104 (HDI dielectrics), IPC-4202/4203/4204 (flex materials), IPC-4552 (ENIG), IPC-4553 (ImAg), IPC-4554 (ImSn), IPC-4556 (ENEPIG), IPC-4562 (copper foil).

## IPC performance & acceptability
| Standard | Scope |
|---|---|
| IPC-6011 | Generic performance |
| IPC-6012 (rev F, Oct 2023; amendment 2025; space/military addendum 6012FS) | Rigid boards qualification — incl. microvia reliability, back-drill |
| IPC-6013 (rev E) | Flex/rigid-flex performance |
| IPC-6016 | HDI performance |
| IPC-6018 | High-frequency (microwave) boards |
| IPC-A-600 (rev M, 2025) | Acceptability of printed boards (visual/microsection) |
| IPC-A-610 (rev J) | Acceptability of electronic assemblies |
| J-STD-001 (rev J) | Soldering requirements |
| J-STD-020 / J-STD-033 | Moisture sensitivity levels / handling |
| IPC-7711/7721 (rev D) | Rework & repair |
| IPC-9701 | Solder joint reliability testing |
| IPC-TM-650 | Test methods (2.5.5.x Dk/Df, 2.6.26 IST, 2.6.27 reflow simulation, 2.4.22 bow & twist) |

## Classes
- **Class 1** – general consumer, cosmetic defects allowed.
- **Class 2** – dedicated service (most industrial/commercial). Default unless told otherwise.
- **Class 3** – high reliability (medical life support, aerospace, military). Stricter annular ring (≥50 µm external), plating ≥25 µm avg, fewer allowable defects. Addenda: 6012FS (space/military), automotive addendum.

## Safety & EMC (product-level; PCB implements them)
| Standard | Scope |
|---|---|
| IEC 62368-1 | ICT/AV equipment safety (replaced IEC 60950/60065) – clearance/creepage tables, insulation types |
| IEC 60664-1 | Insulation coordination: clearance/creepage by pollution degree, overvoltage category, CTI material group |
| IEC 61010-1 | Lab/measurement equipment safety |
| IEC 60601-1 | Medical electrical equipment (MOOP/MOPP) |
| IEC 60335-1 | Household appliances |
| UL 796 / UL 94 | PCB recognition / flammability |
| CISPR 32 / EN 55032 | Multimedia equipment emissions (Class A/B) |
| CISPR 35 / EN 55035 | Immunity |
| CISPR 25 | Automotive component emissions |
| IEC 61000-4-2/-3/-4/-5/-6 | ESD / radiated immunity / EFT / surge / conducted immunity |
| FCC Part 15 B/C | US unintentional / intentional radiators |
| ISO 26262, AEC-Q100/Q200 | Automotive functional safety / component qualification |
| RoHS (EU 2011/65 + 2015/863), REACH, WEEE | Materials compliance |

## Interface specifications (layout requirements)
PCI-SIG CEM & Base specs (PCIe), USB-IF (USB 2/3/4, Type-C), JEDEC JESD79-4/-5 (DDR4/DDR5), JESD209 (LPDDR), IEEE 802.3 (Ethernet), HDMI/VESA DisplayPort, MIPI D-PHY/C-PHY, OIF-CEI (SerDes). Vendor layout guides (Intel/Altera, AMD/Xilinx UG583/UG863, NXP, TI, Microchip, Nordic, Espressif) override generic guidance for their parts.
