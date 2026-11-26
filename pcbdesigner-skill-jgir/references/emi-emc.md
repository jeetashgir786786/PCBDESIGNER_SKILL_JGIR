# EMI / EMC design

Layout guidance improves the odds; only measurement (pre-compliance or accredited lab) proves compliance. Record the standard, class, and test setup.

## 1. Physics to reason with
- Radiation ∝ current × loop area × f² (differential mode) and ∝ common-mode current × cable length × f (common mode). A few µA of common-mode current on a 1 m cable can fail Class B at 100+ MHz — cables and connectors are the usual antennas.
- Fast edges create the spectrum: harmonics roll off at −20 dB/dec above 1/(π·t_on) and −40 dB/dec above 1/(π·tr). Slow edges where timing allows (series R, slew-rate settings, spread spectrum).
- Every current returns; give it the shortest, lowest-inductance path (adjacent solid plane).

## 2. Stackup & ground
- Use a solid, unbroken GND plane adjacent to every signal layer; 4L instead of 2L is the single biggest EMC upgrade.
- Do not split GND into "analog" and "digital" planes by default; partition placement instead and keep one plane. Split only with a clear reason (isolation, safety, ground-loop break) and then nothing crosses the gap except via a bridge/isolator.
- Stitch GND planes/pours with vias: spacing ≤ λ/20 at the highest frequency of concern (λ in the dielectric). Example: 1 GHz in FR-4 (λ ≈ 150 mm) → ≤ 7.5 mm; 6 GHz → ≤ 1.25 mm-ish in critical areas. Fence board edges with a GND via row (same spacing) on multilayer boards.
- 20H rule (pull power planes back 20× the P-G spacing from the GND plane edge) gives limited, debated benefit; edge via-stitching of GND and keeping high-speed traces away from edges matter more.
- Chassis ground: connect board GND to chassis at the I/O connector area, low-inductance (multiple screws/gaskets), RC or direct per strategy; a chassis guard ring on the I/O edge for shielded connectors.

## 3. Placement & routing
- Zone the board: I/O connectors along one edge, their filters/ESD next to them, then interface ICs, then the "dirty" high-speed core away from I/O. No high-speed nets near connectors or board edges unless they go to that connector.
- Clocks and fast buses: short, stripline if possible, never cross splits or run along board edges; spread-spectrum clocking reduces peak emissions by several dB.
- Switching converters: minimise hot-loop area; small switch-node copper; input filter (LC/π) for conducted emissions; shielded inductors near sensitive circuits.
- Crystals: close to the IC, guard GND pour under them on L1 with vias, no traces under them.

## 4. I/O filtering & protection (place at the connector, in this order: connector → ESD/TVS → CMC / ferrite / RC → device)
- ESD: TVS arrays with low capacitance for fast lines; return path to GND/chassis with short wide connection and multiple vias. IEC 61000-4-2 typical levels: ±8 kV contact / ±15 kV air (level 4).
- EFT/surge (IEC 61000-4-4/-5) for power and long cables: TVS + series impedance + GDT for lines exposed to outdoor surges.
- Common-mode chokes on USB/Ethernet/CAN/RS-485 if emissions/immunity require; low-capacitance designs for high speed.
- Ferrite beads on power entering/leaving; watch DC bias derating and resonance with caps (damp with ESR).
- Shield-to-chassis: 360° connection at the connector; pigtails ruin shielding above ~10 MHz.
- Unused connector pins: GND or filtered, not floating.

## 5. Standards quick view
Emissions: CISPR 32/EN 55032 (Class A industrial, Class B residential, B ≈ 10 dB tighter), FCC Part 15B, CISPR 11 (ISM), CISPR 25 (automotive). Immunity: CISPR 35/EN 55035, IEC 61000-4-2 (ESD), -4-3 (radiated), -4-4 (EFT), -4-5 (surge), -4-6 (conducted).

## 6. EMC review checklist
- [ ] Every signal has an adjacent continuous reference; no crossings of splits/voids
- [ ] Return vias at all layer changes; GND stitching density OK; edge fence on multilayer
- [ ] Clock/high-speed nets short, internal, away from edges and connectors
- [ ] Hot loops minimal; switch nodes small; input/output filters present
- [ ] I/O: ESD/TVS/CMC/filters at connectors with low-inductance returns; shield termination defined
- [ ] Crystal/oscillator area guarded; spread spectrum considered
- [ ] Cable/enclosure strategy documented; pre-compliance scan planned (near-field probes, LISN, current clamp on cables)
