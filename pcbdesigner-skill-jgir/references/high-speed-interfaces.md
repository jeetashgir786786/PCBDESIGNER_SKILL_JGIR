# High-speed interface layout cheat sheet

Values are typical guidance compiled from specs and vendor layout guides. **The chip vendor's layout guide and the interface spec always win.** Record the source of every number you apply in a design.

## 1. Summary table
| Interface | Rate / Nyquist | Impedance | Intra-pair skew (typ.) | Other key rules |
|---|---|---|---|---|
| USB 2.0 HS | 480 Mb/s | 90 Ω diff ±15 % | ≤ ~50 mil (1.25 mm) | Keep short; ESD diode at connector with low C (<1 pF); CMC optional |
| USB 3.2 Gen1/Gen2 | 5/10 Gb/s (2.5/5 GHz) | 90 Ω (85–90) ±10 % | ≤ 5 mil | TX AC caps 75–265 nF (100–220 nF typical) near TX; RX caps inside device/cable; low-C ESD (<0.3–0.5 pF) |
| USB4 / Thunderbolt | 20–40 Gb/s/lane (USB4 v2 80 Gb/s PAM3) | 85 Ω (vendor) | ≤ 2–5 mil | Retimer guides govern; low-loss material for long runs |
| PCIe Gen3 | 8 GT/s, 4 GHz | 85 Ω ±15 % (100 Ω tolerated) | ≤ 5 mil | Total channel IL ~22 dB @ 4 GHz; TX AC caps 176–265 nF (220 nF) |
| PCIe Gen4 | 16 GT/s, 8 GHz | 85 Ω | ≤ 5 mil | ~28 dB @ 8 GHz; back-drill stubs > ~15 mil |
| PCIe Gen5 | 32 GT/s NRZ, 16 GHz | 85 Ω ±10 % | ≤ 2–5 mil | 36 dB bump-to-bump @ 16 GHz; low-loss laminate for system boards; retimers common |
| PCIe Gen6 | 64 GT/s PAM4, 16 GHz | 85 Ω | tight | ~32 dB @ 16 GHz (tighter than Gen5 because of PAM4 SNR); FEC; ultra-low-loss, back-drill/blind vias |
| PCIe Gen7 | 128 GT/s PAM4, 32 GHz | 85 Ω | tight | ~36 dB @ 32 GHz; Megtron 7/8 class, HVLP, minimal stubs |
| SATA 3 | 6 Gb/s | 85–100 Ω | ≤ 5–10 mil | AC caps 10 nF |
| 1000BASE-T MDI | 125 MBd PAM5 | 100 Ω diff | ≤ 50 mil | Magnetics close to RJ45; PHY close to magnetics; no plane under magnetics–RJ45 isolation gap (Bob Smith termination per PHY guide); 1500 Vrms isolation |
| RGMII | 125 MHz DDR | 50 Ω SE | match data to clock ± ~50 mil | 2 ns clock skew via PHY/MAC internal delay or trace; series R 22–33 Ω |
| SGMII / 10GBASE-KR / 25G | 1.25–25 Gb/s | 100 Ω | ≤ 5 mil | AC-coupled 100 nF |
| HDMI 2.0/2.1 | up to 6 Gb/s / 12 Gb/s FRL | 100 Ω ±10 % | ≤ 5 mil; inter-pair per spec | Low-C ESD; continuous reference to connector |
| DisplayPort | up to 20 Gb/s (UHBR20) | 85–100 Ω (per spec/vendor) | ≤ 5 mil | AC caps 75–200 nF |
| MIPI D-PHY | up to ~4.5 Gb/s/lane | 100 Ω diff, 50 Ω SE | ≤ 5 mil; lane-to-clock per vendor | All lanes same layer/length group |
| MIPI C-PHY | trios | 50 Ω SE per wire | trio matching | Equal length in trio |
| LVDS | up to ~1 Gb/s | 100 Ω | ≤ 5–10 mil | 100 Ω termination at receiver |
| JESD204B/C | up to 16/32 Gb/s | 100 Ω | ≤ 5 mil | SYSREF/device clock timing per ADC guide |
| 56/112G PAM4 SerDes | 28/56 GHz Nyquist (≈26.6/53 GHz) | 90–100 Ω (device) | ≤ 1–2 mil | COM-based compliance; back-drill ≤ 6–8 mil; Megtron 7/8, Tachyon class; HVLP; via 3D modelling |
| QSPI / OSPI flash | 100–200 MHz | 50 Ω SE | match data to clock (~±100–200 mil) | Series R at source; short |
| SD / eMMC | up to 200 MHz (HS200/HS400) | 50 Ω SE | match per vendor | Pull-ups per spec; strobe line for HS400 |
| RF 50 Ω lines | — | 50 Ω SE/CPWG | — | See rf-layout.md |

## 2. DDR memory
General:
- Topology: point-to-point for DQ/DQS/DM; fly-by daisy chain for CA/CMD/CTRL/CLK with VTT termination at the end (DDR3/4); DDR5 has two independent 32/40-bit sub-channels per DIMM, on-die termination for CA, and DFE in the DRAM.
- Impedance (vendor-specific!): DQ/CA single-ended 34–50 Ω (examples: AMD Versal UG863 DDR5 40 Ω ±10 % SE and 75 Ω diff CK/DQS; Intel Agilex DDR5 memory-down stripline 45 Ω; JLCPCB guide cites 40–45 Ω SE / ~80 Ω diff).
- Lengths (examples, not universal): AMD UG863 DDR5 max 10,000 mil for CA, 5,000 mil for DQ (component), 4,000 mil (DIMM); Intel DDR5 memory-down DQ max ~4.5 in.
- Spacing (example AMD DDR5): 2H between CA signals (1H under the SoC, 1.5H under the DRAM), 5H between CA and other signals.
- Matching: DQ ↔ DQS within each byte lane (in ps, including package delays). No matching across byte lanes. CA ↔ CLK per DRAM segment. Diff P/N within ~1 ps. Use the vendor's ps windows (e.g. Intel LPDDR4 DQ–DQS −68…+43 ps). TI recommends targeting ≤20 % of the allowed skew in the layout tool, then confirming by simulation.
- Keep each byte lane on one layer with identical via count; reference to GND (or VDDQ if the vendor allows), never across splits.
- VREF (DDR3/4): low-noise divider + decoupling at each DRAM, 20–25 mil traces away from aggressors. VTT: low-impedance island near the end of fly-by with its own decoupling; sink/source regulator.
- Decoupling per DRAM per vendor (typical: several 0.1–1 µF 0201/0402 under/next to each package + bulk).
- Simulate (IBIS) for anything above DDR3-1600; DDR5 needs channel simulation with DFE.

## 3. PCIe specifics
- AC coupling capacitors on TX side only (per spec), 0201/0402, symmetric placement, both caps of a pair side-by-side; GND void under cap pads on the adjacent plane (single layer) to reduce capacitive dip.
- Polarity inversion is allowed within a pair (P/N swap), lane reversal allowed per link width — use these to avoid crossovers and vias.
- REFCLK: 100 MHz HCSL, 85/100 Ω diff, keep away from TX/RX lanes; spread-spectrum compatibility per system.
- Edge-finger (CEM) boards: 1.57 mm nominal thickness at fingers; hard gold, bevel; follow CEM breakout guidelines (GND void under fingers per vendor).
- Retimer/redriver guides (TI SNLA426, Astera, Parade) give per-section loss budgets — use them.
- Example split (Astera, Gen5): 36 dB total bump-to-bump divided across root package, CEM connector, add-in card and system board; an add-in card typically gets ~9 dB, leaving the base board roughly half after package and connector.

## 4. USB Type-C
- CC1/CC2 lines to the PD/CC controller with ESD; SBU lines; VBUS current path sized for the negotiated current (up to 5 A with EPR 48 V on PD 3.1) with TVS rated appropriately.
- SuperSpeed pairs: swap/mux handled by a redriver/mux; keep the flip-mux close to the connector; consistent pair polarity.
- Shield to chassis via RC or direct per EMC strategy; GND pins solid to plane with multiple vias.

## 5. Ethernet
- PHY–magnetics: 100 Ω diff pairs, short; magnetics–RJ45: 100 Ω, short, no ground plane under the high-voltage side (keep 1500 V isolation clearance; typical void ≥ 2 mm/80 mil), chassis ground ring around RJ45 if shielded.
- Bob Smith termination (75 Ω + 1000 pF/2 kV) only where the PHY vendor recommends it.
- Integrated-magnetics RJ45 (MagJack) simplifies layout; follow its datasheet footprint/keepouts.
- Industrial: add surge/ESD protection per IEC 61000-4-5 level.

## 6. Rules for any high-speed interface (checklist)
- [ ] Target impedance per layer from fab stackup; diff/SE widths entered as net-class rules
- [ ] Reference: continuous GND under the full route; return vias at every layer change
- [ ] Loss budget computed for the worst-case length and material, with margin
- [ ] Stub control: back-drill/blind via/layer choice; NFPs removed
- [ ] AC caps, ESD, CMCs placed per vendor order (connector → ESD → CMC → caps → device, typical) with minimal stubs (pads in-line)
- [ ] Skew matched at the mismatch source; inter-pair skew per spec
- [ ] Crosstalk spacing; TX/RX separation
- [ ] Connector footprint & breakout per connector vendor (often provides an optimised launch)
- [ ] Simulated or vendor-checked; status reported honestly
