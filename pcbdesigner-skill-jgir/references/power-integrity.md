# Power integrity (PDN) design

## 1. Target impedance
Ztarget = ΔV_allowed / ΔI_transient = (Vrail × ripple fraction) / ΔI.
- ΔI: use the vendor's step current; if unknown, a common assumption is 50 % of max current.
- Ripple fraction: the AC part of the tolerance (e.g. ±3 % total = 1 % DC regulation + 2 % AC).
- Example (AMD UG863 style): 0.80 V, 2 % AC, 40 A step → Ztarget = 0.016 / 40 = 0.4 mΩ.
- The PDN impedance seen from the die must stay ≤ Ztarget from DC up to the frequency where on-package/on-die capacitance takes over (often ~50–100 MHz for board-level decoupling; vendor PDN tools specify F_eff).
- Frequency bands: VRM (DC–~100 kHz) → bulk electrolytic/polymer (~kHz–1 MHz) → MLCC 1–22 µF (~0.1–10 MHz) → MLCC 10–100 nF + plane capacitance (~10–100+ MHz) → package/die.
- Use the vendor PDN tool (Intel/Altera PDN tool, AMD PDN spreadsheet/"PDM", TI/NXP guides) or a PI simulator; don't guess capacitor counts for high-current cores.

## 2. Capacitor selection & placement
- Mounting inductance dominates above SRF: loop = pad → trace → via → plane → back. Minimise: wide short connections, vias at pad ends or via-in-pad, multiple vias per pad for big caps, cap on the side closest to the plane it serves.
- Smaller packages (0201/0402) have lower ESL; reverse-geometry (0204) or 3-terminal/X2Y parts lower it further.
- MLCC DC-bias derating: a 10 µF 0402 X5R 6.3 V may give < 3 µF at 3.3 V. Use the vendor's DC-bias curves (Murata SimSurfing, TDK, Samsung tools).
- Many values cause anti-resonance peaks between them; use enough of each to keep the peak below Ztarget, or use controlled-ESR parts / polymer caps to damp.
- BGA decoupling: smallest caps directly under the BGA on the back side, sharing the power/GND ball vias (VIPPO).
- Bulk capacitance near the VRM output and at the load if the VRM is far.

## 3. Planes
- Plane capacitance: C ≈ 0.2249 pF/in × εr × A[in²] / d[in] (≈ 0.0885 pF/cm × εr × A[cm²]/d[cm]). 3 mil FR-4 → ~300 pF/in²; 1 mil high-Dk embedded capacitance cores → several nF/in².
- Thin P–G dielectric (≤ 3–4 mil) lowers spreading inductance and helps high-frequency decoupling.
- Plane resonances (cavity modes) occur when plane dimension ≈ λ/2; stitch caps/vias and lossy dielectric damp them.
- Avoid narrow necks in power planes (current crowding, IR drop, inductance). Check the neck width under BGAs where anti-pads perforate the plane.

## 4. DC (IR) drop & current capacity
- DC drop budget: typically ≤ 1–2 % of rail for cores; check with plane resistance R = ρ·L/(W·t) (copper ρ ≈ 1.72 µΩ·cm at 20 °C, +0.39 %/°C).
- 1 oz copper sheet resistance ≈ 0.49 mΩ/□ (35 µm); 2 oz ≈ 0.25 mΩ/□.
- Via current: compute barrel cross-section = π × drill × plating thickness; apply IPC-2152 (or IPC-2221 as a conservative estimate). A 0.25 mm via with 25 µm plating carries roughly 1–1.5 A for a ~10 °C rise in free air; use many vias in parallel and IR-drop simulation for high currents.
- Use remote sense lines (Kelvin) at the load for high-current, low-voltage rails.
- Connector pins & press-fit: derate per manufacturer; spread current across pins.

## 5. Power-tree & sequencing (schematic-level PI)
- Power tree diagram: source → each regulator → loads; currents, efficiency, dissipation, start-up order, power-good chains.
- Inrush and soft-start; hot-swap/eFuse at input; reverse polarity; TVS sized for surge.
- Analog/RF rails: LDO after switcher or ferrite + cap π-filter, with low-noise reference grounding (shared GND plane, careful placement — no ground splits).

## 6. Switching regulator layout (summary; see power-electronics.md)
- Hot loop (input cap ↔ high-side ↔ low-side switch) smallest possible, ideally on one layer with the return directly underneath on L2 GND (≤ 4 mil away).
- Switch node: just big enough for current; minimise area (it radiates); keep away from sensitive traces; no copper under it on adjacent layers except GND.
- Feedback divider at the IC, sense from the output cap/load point, away from SW node.

## 7. PI checklist
- [ ] Ztarget computed per rail with source of ripple/step data
- [ ] Decap plan per vendor tool or PI simulation; DC-bias derating applied
- [ ] Capacitor mounting inductance minimised; vias per cap; placement close to power pins
- [ ] Planes allocated; P/G spacing thin; necks checked
- [ ] IR drop < budget (simulated for > 10 A rails); via counts per rail sufficient
- [ ] Remote sense routed; VRM compensation reviewed for actual output capacitance
- [ ] Start-up/shut-down sequencing and power-good logic reviewed
