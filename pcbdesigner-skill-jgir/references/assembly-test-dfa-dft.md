# Assembly (DFA), test (DFT) & footprints

## 1. Footprints / land patterns
- Generate from the manufacturer's recommended land pattern first; otherwise IPC-7351B (density levels: M most, N nominal, L least). Name per IPC-7351 convention (e.g. `RESC1608X55N`, `QFN50P500X500X90-33N`).
- Verify: pad size, pitch, pin 1 / numbering, exposed pad and paste windowpane, courtyard, 3D model, silkscreen polarity outside pads, package height for enclosure.
- BGA: NSMD pads ≈ 80–90 % of ball diameter for ≥ 0.5 mm pitch (follow vendor); SMD pads for some fine pitch/ceramic packages.
- QFN/DFN: thermal pad paste coverage 50–80 % in windowpane segments; vias filled/tented or small; corner pins checked; perimeter pad length extended 0.2–0.3 mm outside the body for toe fillet.
- Check every footprint against the datasheet package drawing **and** the exact orderable part number suffix (package variants differ).

## 2. Placement for assembly
- Component-to-component spacing per assembler (typ. ≥ 0.2–0.3 mm passive-passive, ≥ 0.5 mm to tall parts, ≥ 1–3 mm around BGAs for rework nozzles).
- Same orientation for similar parts; polarised parts in consistent direction; pin-1 markers visible after placement.
- Keep parts ≥ 3–5 mm from panel edges/rails (or add rails), ≥ 1 mm from V-score lines; no tall parts on wave-solder side; heavy parts on top for double reflow.
- Fiducials: 3 global (non-collinear) per board/panel; local pair for fine pitch (≤ 0.5 mm) BGAs/QFPs; 1 mm copper dot, 2–3 mm clear mask opening, no copper/silk in the clearance.
- Tooling holes 2.0–3.2 mm NPTH in rails.
- Thermal balance for 0201/0402: equal copper on both pads (thermal reliefs on plane connections) to prevent tombstoning.
- Mixed technology: THT parts with pin length/protrusion for wave or selective solder; paste-in-hole for reflow THT.

## 3. Stencil & paste
- Stencil 100–150 µm (4–6 mil) typical; 80–100 µm for 0.4 mm pitch/0201; step stencils for mixed.
- Area ratio = aperture area / wall area ≥ 0.66 (≥ 0.5 with nano-coated / electroformed stencils). Aspect ratio (width/thickness) ≥ 1.5.
- Reduce paste on large pads; windowpane thermal pads; home-plate apertures for passives to avoid mid-chip balls.

## 4. Design for test
- Test points on every net needed for bring-up/ICT: power rails, clocks, resets, debug UART, programming, key analog nodes.
- ICT: test pad ≥ 0.8–1.0 mm (0.6 mm minimum), spacing ≥ 1.27–2.54 mm centre, ≥ 1–3 mm from tall parts, all on one side preferably, no mask over them; via test points allowed if sized as pads and not tented.
- Flying probe: smaller pads OK (≥ 0.4–0.5 mm) but slower.
- Boundary scan (JTAG) chain with header; programming connector (SWD/JTAG/Tag-Connect footprint) accessible after enclosure assembly if field updates are needed.
- Current measurement: 0 Ω links or jumpers per rail for bring-up; power LEDs; ADC sense of rails if MCU present.
- Functional test fixture access: pogo-pin pads with alignment holes.

## 5. Assembly documentation
BOM (MPN, manufacturer, qty, refdes, DNP flag, alternates approved), CPL/centroid (refdes, X, Y, rotation, side; rotation convention per assembler — JLCPCB often needs rotation corrections), assembly drawings (top/bottom, polarity), special instructions (conformal coat masking, underfill, torque, press-fit), MSL handling, X-ray for BGAs/QFNs, IPC-A-610 class.
