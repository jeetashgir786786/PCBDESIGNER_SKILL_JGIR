# Signal integrity & high-speed layout

Apply when edge rates, data rates, trace lengths or interface specs make transmission-line behaviour relevant. Interface-specific numbers are in `high-speed-interfaces.md`; stackup in `stackup-design.md`; scripts in `scripts/pcb_calc.py`.

## 1. Is it "high speed"? (decide with rise time, not clock frequency)
- Propagation delay: tpd ≈ 84.7 ps/in × √Dk_eff (≈ 3.33 ps/mm × √Dk_eff). FR-4 stripline (Dk ≈ 4) ≈ 170 ps/in (6.7 ps/mm); microstrip ≈ 140–150 ps/in.
- Knee frequency: f_knee ≈ 0.5 / tr (10–90 %). Bandwidth of interest ≈ 0.35/tr to 0.5/tr. A 1 ns edge matters to ~500 MHz even if the clock is 10 MHz.
- Critical length: treat as a transmission line when length > tr / (6·tpd) (conservative) – e.g. tr = 1 ns, 170 ps/in → ~1 in. Above tr/(2·tpd) reflections are certain without termination.
- SerDes: work at Nyquist = baud/2 (NRZ: Gbps/2; PAM4: Gbps/4) and check to ~1.5× Nyquist.

## 2. Impedance (approximate formulas; final values from a field solver + fab)
IPC-2141 closed forms (±5–10 %, valid ranges limited):
- Microstrip: Z0 ≈ 87/√(εr+1.41) · ln(5.98h / (0.8w + t)), for 0.1 < w/h < 2, εr < 15.
- Symmetric stripline: Z0 ≈ 60/√εr · ln(4b / (0.67π(0.8w + t))), b = plane-to-plane spacing, w/b < 0.35, t/b < 0.25.
- Edge-coupled differential: microstrip Zdiff ≈ 2Z0(1 − 0.48·e^(−0.96 s/h)); stripline Zdiff ≈ 2Z0(1 − 0.347·e^(−2.9 s/b)).
Real-world effects the formulas miss: trapezoidal etch (top narrower by ~0.5–1 mil per oz), solder mask on microstrip (−1…−3 Ω), resin-rich prepreg Dk near the trace, frequency-dependent Dk, copper roughness (raises effective Dk/inductance), plating on outer layers. Use a 2D solver (Polar Si9000, Saturn PCB, KiCad calculator for rough, Altium/Cadence/HyperLynx solvers, open-source tools like openEMS/atlc) with the fab's Dk per construction.
- Width–loss trade-off: wider traces (≥4–5 mil) lower conductor loss; get them with thicker dielectrics, not by lowering Z0.
- Keep the same impedance through the whole path: pad, breakout, trace, via, connector. Neck-down in BGA fields only for short lengths (≤ 3–5 mm) and recompute.

## 3. Loss
- Dielectric loss (rough): α_d [dB/in] ≈ 2.3 · f[GHz] · Df · √Dk.
- Conductor loss, smooth copper (rough): α_c [dB/in] ≈ 36 · √f[GHz] / (w[mil] · Z0[Ω]); multiply by a roughness factor 1.2–2+ for standard foil at multi-GHz.
- Typical stripline insertion loss at 8 GHz per inch: FR-4 ~0.6–0.7 dB, Megtron 6 class ~0.2 dB (TI SNLA426 table values for its geometry). Always compute a channel budget: package + breakout + vias + trace + AC caps + connector + other card, with margin (≥1–3 dB).
- Temperature and humidity raise loss of FR-4-class materials notably; low-loss materials are more stable — budget for worst case.

## 4. Return paths & reference planes
- At high frequency the return current flows on the reference plane directly under the trace. Any gap, slot, split, anti-pad cluster or plane edge under a trace forces a detour → radiation, crosstalk, impedance step.
- Never route across plane splits. If a signal must change from a GND reference to a PWR reference, place a stitching capacitor (e.g. 10–100 nF, low-ESL) right next to the transition; better redesign.
- Every signal via that changes reference layers gets a GND return via within ~1 mm (25G+: within 0.5–0.8 mm, symmetric pair of GND vias around a differential via pair).
- Keep high-speed traces ≥ 3–5H (and ≥ 40 mil for fast edges) from plane edges/board edges; maintain the reference plane at least 3H beyond the trace on both sides.
- Anti-pad voids from rows of vias (BGA fields, connectors) can merge into slots — check plane continuity under every critical route ("swiss cheese" check).

## 5. Crosstalk
- Spacing: edge-to-edge ≥ 2W (the "3W" centre rule) for general signals; ≥ 3H for sensitive/aggressor; vendor rules often express it as multiples of H (e.g. AMD DDR5: 2H within CAC group, 5H to other signals).
- Stripline has almost no FEXT; microstrip FEXT grows with coupled length — keep fast parallel runs on outer layers short.
- Separate TX and RX SerDes lanes by layer or spacing; separate clock nets.
- Guard traces only help if stitched to GND every ≤ λ/10 at the highest frequency of interest; otherwise use spacing.
- Orthogonal routing between adjacent signal layers when dual striplines are used.

## 6. Differential pairs
- Route tightly coupled (s ≈ w to 2w) unless the vendor says loosely coupled; keep coupling constant; symmetric breakouts.
- Intra-pair skew: match at the source of mismatch (bend compensation near the bend/pin), total within interface spec (typ. ≤ 5 mil / ~1 ps for 10G+; ≤ 50 mil for USB 2.0).
- Avoid splitting the pair around obstacles; if unavoidable, keep the uncoupled length minimal (< 0.1–0.2 in for 10G+).
- Bends: 45° or arcs; for 25G+ prefer arcs; compensate the inner/outer length difference near each bend.
- Inter-pair (lane-to-lane) skew usually loose for SerDes with deskew; strict for source-synchronous (HDMI TMDS, LVDS, MIPI).
- Via transitions for pairs: two signal vias + two (or four) GND vias symmetric, oval/shared anti-pad, no stubs (back-drill or blind via), keep via pitch to match impedance (field-solve or 3D-model the via).

## 7. Vias and stubs
- Via stub resonance: f_res ≈ c / (4 · L_stub · √Dk_eff) → f[GHz] ≈ 11.8 / (4 · L[in] · √Dk). Keep f_res ≥ 3× Nyquist (simulate for 25G+).
- Back-drill when the stub length would resonate in-band (a common guide: back-drill stubs > 15 mil at PCIe Gen4+; ≤ 6–10 mil residual for 25G–112G). Or route on layers near the bottom when entering from the top (long via used, short stub), or use blind/buried spans.
- Remove non-functional pads on high-speed vias (reduces capacitance).
- Via capacitance and inductance: tune anti-pad diameter to reach the target impedance (larger anti-pad → higher Z).
- Minimise vias on critical nets (≤ 2 per channel side ideally).

## 8. Length / delay matching
- Match in time (ps), not length, when layers have different Dk or mix microstrip/stripline. Include package flight times (pin-delay files) when the vendor says so.
- Only match what the interface requires; unnecessary serpentines add loss and coupling.
- Serpentine rules: segment spacing ≥ 3–4W (≥ 4H for edges ≤ 100 ps); minimum segment length ≥ 1.5–3W; keep serpentines out of BGA fields and away from other nets; prefer many small bumps over a few tall ones for diff pairs.
- Fly-by (DDR CA/CLK): match each group to its clock per segment; DQ/DQS matched within the byte lane only; write-levelling handles CLK–DQS across DRAMs.

## 9. Termination & topology
- Point-to-point CMOS: series termination at the source (Rs ≈ Z0 − Rdriver, often 22–33 Ω) placed within ~tr/(6·tpd) of the driver.
- Multi-drop: parallel/Thevenin at the far end, or fly-by with end termination to VTT.
- SerDes: on-die termination; AC caps (0201/0402) placed per spec (often near TX or near connector), with GND voids under cap pads on the adjacent plane to compensate pad capacitance (field-solve; typical void = pad + small margin on L2 only).
- Clocks: one load per trace preferred; use fan-out buffers.

## 10. Fiber-weave skew & material
See `materials-laminates.md` §3. For ≥ 10 Gbps diff pairs on long runs: spread glass, 2-ply prepreg, angle or zig-zag routing, or image rotation.

## 11. Simulation & verification flow
1. Stackup in solver → per-layer width/space for targets.
2. Pre-layout: what-if channel with IBIS-AMI/S-params (length, material, via, stubs).
3. Constraints into CAD (net classes, diff pairs, impedance per layer, matching groups).
4. Post-layout: extract critical nets (2.5D/3D for vias/connectors), check IL/RL/NEXT/FEXT masks or COM/eye; DDR timing & eye.
5. Report: what was simulated, with which models and tool versions; what was not.
Never state a channel "meets spec" without simulation or measurement.
