# Design review & troubleshooting

## 1. Finding format
`ID | Severity | Location (sheet/refdes/net/layer/coords) | Evidence | Risk/impact | Recommendation | How to verify`
Severity: BLOCKER (won't work / unsafe / unbuildable), HIGH (likely failure, compliance fail, yield killer), MEDIUM (margin/reliability/cost), LOW (best practice), INFO.
Review order: safety & absolute max → power & grounding → connectivity/pinout → protection & faults → thermal & current → SI/PI/EMC → mechanical/DFM/DFA → test & documentation.

## 2. Schematic checklist
- [ ] Every IC: all power pins connected with the right rail; all GND/exposed pads connected; decoupling per datasheet per pin group
- [ ] Absolute-max checked for every pin in every mode (power-up sequencing, back-powering through I/O, hot-plug)
- [ ] Pin-function verification against the exact part number datasheet (alternate functions, bootstraps, strapping pins, reserved/NC pins)
- [ ] Unused pins: tied per datasheet (not floating inputs); open-drain pull-ups present and sized (I²C rise time vs bus capacitance)
- [ ] Reset, clocks (crystal load caps CL = 2(CL_spec − C_stray)), boot mode, debug/programming access
- [ ] Logic-level compatibility between domains; level shifters direction/speed; no back-feeding of unpowered domains
- [ ] Power tree: current budget with margin, regulator dissipation, inrush, sequencing, power-good, UVLO
- [ ] Protection: reverse polarity, overcurrent (fuse/eFuse), TVS/ESD on every external connection, surge level
- [ ] Connectors: pinout vs mating cable/board (mirror trap!), keying, current rating per pin
- [ ] Analog: op-amp input/output range, stability with capacitive load, reference noise/accuracy, ADC drive & anti-alias
- [ ] Footprint assigned for every symbol and verified vs datasheet & ordered package; DNP parts marked
- [ ] BOM: voltage ratings (and MLCC DC bias), tolerances, temperature grade, lifecycle (active, not NRND/EOL), second sources
- [ ] Test points, LEDs, jumpers for bring-up; net names meaningful
- [ ] ERC run and every warning resolved or justified

## 3. Layout checklist
- [ ] Stackup matches fab-engineered stackup; impedance widths per layer applied via rules
- [ ] Placement: connectors/mechanics locked; critical loops minimal; decoupling at pins; crystal close; thermal parts spread; height zones respected
- [ ] Reference planes continuous under all high-speed/sensitive nets; return vias at transitions; no routing over splits/voids
- [ ] Power: plane/pour widths and via counts vs current; necks; IR drop; hot loops; switch-node area; Kelvin sense
- [ ] High-speed: lengths/skews within spec; stubs controlled (back-drill/blind); AC caps & ESD placement; spacing for crosstalk
- [ ] RF: 50 Ω lines field-solved, via fences, antenna keepout on all layers, matching footprints
- [ ] HV: clearance/creepage per standard on all layers; slots; barrier keepouts
- [ ] Thermal: thermal vias, copper spreading, hot parts not next to sensitive ones
- [ ] DFM: fab minimums met with margin; annular rings; acid traps; slivers; copper-to-edge; copper balance; via protection types
- [ ] DFA: courtyard overlaps none; fiducials; orientation; spacing to tall parts; panel/rails; polarity/pin-1 silkscreen
- [ ] DFT: test points accessible; programming header reachable
- [ ] DRC with schematic parity clean; zones refilled; unrouted = 0
- [ ] Outputs regenerated after final DRC and checked in an independent Gerber viewer; fab/assembly drawings match

## 4. High-layer/HDI additions
See `high-layer-count.md` §7 and `hdi-microvias.md`. Additionally: drill-span files vs CAD via spans; back-drill must-not-cut layers; stacked microvia count; buried vias under microvias filled & capped; plane "swiss-cheese" under BGAs; sequential lamination count within material capability.

## 5. Troubleshooting method
1. Write down observations (measured, with instrument and setup) separately from interpretations.
2. Reproduce; find the smallest failing condition.
3. Rank hypotheses by likelihood × impact; pick tests that discriminate between them (not tests that confirm a favourite).
4. Predict the expected result of each test for each hypothesis before running it.
5. Change one variable at a time; keep a log.
6. Safety first: current-limited supplies, isolation for mains, differential probes, discharge checks, PPE.
Common bring-up failures to check first: wrong footprint/pinout (rotated/mirrored connector, SOT-23 pin order), missing GND/thermal pad solder, regulator EN/PG wiring, boot straps, crystal not oscillating (load caps/footprint), reversed polarised parts, solder bridges on fine pitch, MLCC DC-bias making rails unstable, backfeeding through I/O, USB D+/D− swapped, TX/RX crossed on UART.
Common high-speed failures: link trains at lower rate (loss/stubs/AC caps/polarity), DDR training fails (byte-lane swap rules, VREF, termination, timing skew), intermittent errors with temperature (marginal loss, CAF, cracked microvia), EMC failures (cable common-mode, slot under clock trace).
