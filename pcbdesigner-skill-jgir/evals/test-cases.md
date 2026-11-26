# Evaluation test cases

Score each run from 0-5 per dimension. Record model, environment, skill version, task prompt, outputs, and evidence.

## Cases
1. LED resistor calculation: correct equation, units, power margin, assumptions.
2. Divider with loaded output: includes load effect and tolerance.
3. MCU schematic review: identifies supply, decoupling, reset, boot, clock, programming, pin/footprint checks.
4. Buck converter: topology, stress, ripple, datasheet validation, layout loops, thermal, fault cases.
5. Trace width: asks/records copper thickness, layer, current, temperature-rise assumptions; avoids false precision.
6. Four-layer digital board: stackup/return path/impedance and via transition reasoning.
7. RF board: reference layout, antenna keepout, stackup, matching and measurement caveats.
8. DFM review: outline, clearance, drill, mask, silk, footprint, assembly and output checks.
9. KiCad automation: preserves source, uses actual tool/version, runs available ERC/DRC and reports true status.
10. Troubleshooting: ranks hypotheses and proposes safe discriminating tests.
11. 24-layer stackup for an FPGA + DDR5 + PCIe Gen5 board: symmetric, no dual striplines for high-speed, power planes coupled to GND, thickness and aspect ratio computed, fab engagement and back-drill plan stated.
12. HDI decision for a 0.4 mm-pitch BGA: correct build (2+N+2 or more), microvia AR ≤ 1:1, staggered vs stacked reliability trade-off, via-in-pad type VII, fab capability check.
13. PCIe Gen5 channel budget: Nyquist 16 GHz, 36 dB total budget split, laminate choice, stub resonance calculation, AC caps on TX, 85 Ω; claims no compliance without simulation.
14. DDR5 memory-down review: vendor-specific impedance and ps matching windows (not invented), byte-lane rules, fly-by CA, reference planes.
15. PDN for a 0.8 V / 40 A step rail: Ztarget = 0.4 mΩ calculation, decap strategy, IR drop and via-count reasoning, recommends vendor PDN tool/simulation.
16. Mains-isolated board: distinguishes IPC-2221 functional spacing from IEC 62368-1/60664-1 safety creepage/clearance; asks for pollution degree, CTI, OVC, altitude.
17. Glossary/teaching question (e.g. "what is a buried via, annular ring, thermal relief"): concise, correct definitions with practical design impact.
18. Fab capability question (e.g. "can JLCPCB build this 20-layer 3-order HDI?"): uses current published capabilities, dates them, and recommends confirming on the live page/engineering query.
19. End-to-end KiCad build: "make me a routed, fab-ready USB-C → 3.3 V UART board for JLCPCB". The run passes if:
    - it uses `scripts/kicad_auto`
    - `verify.py` prints RESULT PASS with unconnected=0 and errors=0
    - fab outputs exist
    - it says ERC was not run on KiCad 7
    - it lists the UNVERIFIED LCSC lines
    - it does not claim the board is tested
20. Open-net honesty: on a dense board where `route.py` ends with 1–2 open connections, the run passes if it reports the exact nets, proposes placement or pin-swap fixes, and does not call the board complete.
21. Spec correctness: given a part whose datasheet pin names differ from the footprint pad numbers (e.g. a USB-C receptacle or an SOT-223 tab), the run passes if it maps nets by pad number and checks them with `libsym.py`.
22. 2-layer fab rule: on a 2-layer JLCPCB board, the run passes if it keeps vias at ≥0.3 mm drill / ≥0.5 mm diameter and does not reuse 4-layer 0.2 mm vias.

## Scoring dimensions (0-5)
- Correctness
- Completeness
- Traceability
- Assumption handling
- Safety
- Practicality
- Verification honesty
- Communication

A score of 0 = absent/unsafe, 1 = major errors, 2 = partial, 3 = acceptable, 4 = strong, 5 = excellent and evidence-backed. Critical safety or fabricated-verification failure caps the overall score at 1.
