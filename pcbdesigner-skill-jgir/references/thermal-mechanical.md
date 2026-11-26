# Thermal & mechanical design

## 1. Thermal workflow
1. Power budget per component per operating mode (worst-case ambient, worst-case load, efficiency at temperature).
2. Identify heat paths: junction → case → pad/thermal vias → planes → board → air/enclosure/heatsink.
3. First-order estimate: T_j = T_a + P·θ_JA (only valid for the JEDEC board θ_JA was measured on — usually a 4L 76×114 mm board; real boards differ). Better: T_j = T_board + P·Ψ_JB or a thermal resistance network with your copper.
4. If margin is < ~15–20 °C to max T_j (or derating limit), do thermal simulation (FloTHERM, Icepak, SimScale, KiCad doesn't do this) or build and measure (thermocouple/IR camera with emissivity correction).

## 2. PCB thermal techniques
- Copper area on multiple layers connected by thermal-via arrays under exposed pads: 0.25–0.3 mm drills at 1.0–1.2 mm pitch, filled/capped (VIPPO) or tented to stop solder wicking.
- Thermal resistance of one via (rough): R ≈ L / (k_Cu · π · d · t); 1.6 mm board, 0.3 mm drill, 25 µm plating → ≈ 1.6e-3 / (390 · π · 0.3e-3 · 25e-6) ≈ 175 K/W per via; 20 vias in parallel ≈ 9 K/W (filled vias lower it further).
- Heavy copper (2–4 oz) planes for spreading; copper coins/inlays for > ~10 W/cm² hotspots; metal-core (IMS) boards for LEDs and power.
- Heatsinks with TIM; thermal pads/gap fillers to enclosure; airflow direction relative to tall parts.
- Keep heat-sensitive parts (electrolytics, crystals, sensors, Li-ion) away from hot spots; electrolytic life halves per +10 °C.
- Current-carrying conductors: size by IPC-2152 (planes nearby help), check both temperature rise and voltage drop; see `calculations.md`.

## 3. Mechanical
- Outline, mounting holes (NPTH or plated with keepout ring for screw head + washer, typ. M3 → 3.2 mm hole, ≥ 6–7 mm keepout), stand-off heights, connector positions and mating direction from MCAD (exchange STEP/IDF/IDX).
- Component height zones top/bottom; keepouts under heatsinks, shields, enclosure ribs, battery.
- Board thickness options (0.8/1.0/1.2/1.6/2.0 mm standard); card-edge thickness 1.57 mm.
- Vibration/shock: mass of large parts (inductors, capacitors, connectors) — glue/staking, mounting near supports; BGA corner glue/underfill for drop.
- Flex in assembly: keep MLCCs away from board edges/mounting holes/V-scores and orient parallel to the bending axis (crack risk); use soft-termination MLCCs near stress points.
- Panel & depanel stresses: no parts within 1–3 mm of break lines.
- Connectors: through-hole or SMT with hold-down tabs for mechanical strength; cable bend radius and strain relief.
