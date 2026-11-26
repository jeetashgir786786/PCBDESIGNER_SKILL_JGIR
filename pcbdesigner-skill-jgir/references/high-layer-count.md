# High-layer-count design (18–32+ layers)

Load together with `stackup-design.md`, `hdi-microvias.md`, `signal-integrity.md`, `power-integrity.md` and `high-speed-interfaces.md` for servers, FPGA/ASIC carriers, AI/GPU baseboards, network switches, ATE and backplanes.

## 1. Engineering sequence (do not reorder)
1. **Requirements freeze** – interfaces & data rates, BGA list (pitch, ball count, ball map), rails (V, I_max, ΔI step, ripple %), board outline/thickness limits (card-edge 1.57 mm? chassis?), connectors (press-fit?), thermal design power, IPC class, volume, fab region.
2. **Fab partner first** – choose a fab qualified for the layer count, thickness, aspect ratio, back-drill, HDI order, and laminate. Get their design-rule sheet and laminate library *before* the stackup. Budget fabs that list "32 layers" may offer only through-hole or 1–3-order HDI; true any-layer, 4+N+4, ≥20:1 AR, ±5 % impedance and back-drill ≤6 mil residual stub belong to advanced/server-class fabs.
3. **Pin-map & breakout study** – per BGA: count signal rows, choose via technology (through-via dog-bone vs VIPPO vs microvia), determine escape layers. Do a trial fan-out of the worst BGA before locking layer count.
4. **Stackup v0** – assign layers to interface classes (fastest SerDes → GND/GND striplines nearest the SerDes devices' side), planes to rail groups; select materials per layer (hybrid if possible); compute thickness and aspect ratio; send to fab for engineering.
5. **Channel budget** – for every SerDes channel: loss budget allocation (package, PCB, connectors, cable), reach per laminate (dB/in at Nyquist), via/back-drill plan, AC-cap placement, crosstalk spacing. Pre-layout simulate the worst channel (field-solver stackup + via models).
6. **PDN budget** – Ztarget per rail, VRM placement, plane allocation, decap strategy, IR-drop simulation for >20 A rails, current per via.
7. **Constraint set** – net classes, diff pairs, impedance rules per layer, spacing (intra-pair, pair-to-pair, to other classes), length/delay matching in time units, via rules per class, back-drill nets, keepouts, reference-plane rules, max uncoupled length, max vias per net.
8. **Placement** – connectors/mechanics → big BGAs & SerDes partners (minimise channel length) → VRMs next to loads → memory → decoupling (back side under BGAs) → everything else. Placement review gate.
9. **Fan-out & routing** – fan-out all BGAs, critical channels routed and reviewed first, then memory, then the rest. Plane shapes drawn deliberately, not auto-poured last minute.
10. **Post-layout SI/PI** – extract S-parameters of worst channels, compliance (COM/eye), PDN impedance and IR drop, crosstalk scan, return-path/plane-crossing check.
11. **DFM** – fab DFM report on ODB++/IPC-2581, back-drill file review, copper balance, NFP removal policy, impedance coupons, CAF spacing.

## 2. Board thickness and aspect ratio
- Thickness ≈ Σ dielectrics + Σ copper. 24L with 3–4 mil dielectrics and ½/1 oz copper ≈ 2.4–3.2 mm; 32L ≈ 3.2–4.5 mm.
- Aspect ratio = thickness / finished drill. Mainstream ≤10:1; advanced 12–16:1; backplane-class 20:1+ (top fabs ≥30:1).
- Examples: 3.0 mm with 0.25 mm drill = 12:1; with 0.20 mm = 15:1. A 0.15 mm through-via in a 2 mm board (13:1) is already aggressive.
- Card-edge constraints: PCIe CEM add-in cards are 1.57 mm nominal at the gold fingers → high layer counts need thin dielectrics (2–3 mil) or a thicker body with a milled-down edge (expensive).
- Heavy boards (>3 mm, >24L) have huge thermal mass: tell the assembler; expect long soak profiles, BGA warpage control, possibly vapour-phase reflow.

## 3. Via strategy for 24+ layers
| Need | Solution |
|---|---|
| ≥0.8 mm BGA, many layers | Through vias in dog-bone or VIPPO; back-drill SerDes |
| 0.65 mm BGA | VIPPO through vias (0.2 mm drill) or 1-order HDI |
| ≤0.5 mm BGA | HDI 2+N+2 or more (microvia-in-pad, stacked/staggered) |
| Long SerDes channels ≥25 Gbps | Back-drill every via stub to ≤8–10 mil (≤6 mil for 56/112G) or use blind/buried spans |
| Dense routing between two inner layers | Buried vias (sub-lamination) |
Back-drill design rules (confirm with fab):
- Back-drill diameter = original drill + 0.2–0.25 mm (8–10 mil).
- Keep other copper ≥ 8–10 mil from the back-drill hole edge on all drilled-through layers (anti-pad enlarged on those layers).
- Specify "must-not-cut" layer (the last connected layer) and maximum residual stub (e.g. 8 mil). Typical depth accuracy ±2–4 mil.
- Do not back-drill through a layer where the net connects; do not back-drill press-fit holes on the press-fit side.
- Provide back-drill as separate drill files or via the IPC-2581/ODB++ drill spans.
- Rule of thumb for acceptable stub length: keep the first stub resonance f_res = c/(4·L·√Dk_eff) above ~3× Nyquist; a historic guide is stub ≤ ~0.3 in / Gbps-based scaling (e.g. ≤ 12 mil at 25 Gbps) — simulate.

## 4. Assigning interfaces to layers
- Fastest SerDes (25G+): GND/GND striplines adjacent to the side where the SerDes BGA is placed, so the via is short (top-side device → upper striplines; back-drill the rest). For devices on both sides, use upper layers for top devices and lower layers for bottom devices.
- Keep each layer's purpose homogeneous: e.g. L3 = TX lanes, L8 = RX lanes (TX/RX separation reduces NEXT); DDR byte lanes on 2–3 layers with equal via spans per byte.
- Same-layer routing for all members of a matched group (DDR byte lane, diff pair) wherever possible; if layer changes, all members change together.
- Low-speed and power islands on the semi-premium layers (stripline referenced to a P plane).

## 5. Power delivery on large boards
- 0.7–1.0 V cores at 100–1000 A: VRM phases placed around the ASIC, multiple 2 oz planes in parallel for the core rail, many vias per BGA power ball (VIPPO), back-side decoupling directly under the BGA.
- Current per via (rule of thumb, 1 oz plating 25 µm, 0.25 mm drill): ~1–1.5 A for ~10 °C rise; spread core current across hundreds of vias. Verify with IR-drop simulation; aim for <1–2 % DC drop and current density <~ 10–20 A/mm² in vias (simulate; depends on cooling).
- Split planes only where needed; each split plane still needs an adjacent solid GND for the signals referencing it.
- Use remote sense lines from the VRM to the BGA's sense balls, routed as a differential pair away from noisy areas.

## 6. Reliability for thick, high-layer boards
- Use high-Tg (≥170 °C), high-Td (≥340 °C), low Z-CTE material (e.g. IPC-4101 /126, /129, /130 or low-loss equivalents) for lead-free multiple reflows.
- CAF: keep hole-wall to hole-wall ≥ 0.4–0.5 mm on different nets where possible (fab/material dependent); use CAF-resistant laminate; avoid aligning holes along the glass warp direction in dense arrays.
- Copper balance across layers (thieving on sparse signal layers), symmetric stackup, and uniform distribution of plane copper to limit warpage — BGA co-planarity matters.
- Plating: Class 3 requires 25 µm average barrel copper; high-AR holes need proven plating (pulse plating). Ask for IST/thermal-shock coupon results for new constructions.
- Non-functional pad removal: helps SI and drilling; some reliability specs require keeping NFPs on high-AR vias — agree with fab.
- Sequential lamination cycles stress the material: budget ≤3–4 cycles for mainstream laminates; more requires material qualified for it.

## 7. High-layer-count review checklist
- [ ] Fab chosen and their rules/laminates imported; stackup returned by fab with impedance predictions
- [ ] Symmetric stackup, no dual striplines for high-speed, power planes tightly coupled to GND
- [ ] Aspect ratio of smallest through-drill within fab limit; card-edge thickness OK
- [ ] Every BGA fan-out completed and reviewed; escape layer count verified
- [ ] SerDes layer assignment minimises stub; back-drill list complete; must-not-cut layers specified
- [ ] Channel loss budget per interface computed and simulated for worst case
- [ ] Reference continuity: no high-speed crossing of plane splits/voids; return vias within ~1–2 mm of every signal via transition (closer for 25G+)
- [ ] Anti-pad sizes optimised (oval anti-pads for diff via pairs); NFPs removed on SerDes vias
- [ ] PDN: Ztarget met per rail (simulated), IR drop < budget, via current per rail checked
- [ ] CAF spacing, copper balance, thieving approved by fab
- [ ] Impedance and back-drill coupons specified; IPC class and acceptance criteria on the fab drawing
- [ ] Outputs: ODB++ or IPC-2581 (preferred) plus Gerber X2, separate drill files per span and back-drill, IPC-D-356 netlist
