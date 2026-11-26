# Power electronics layout & design

## 1. Intake
Topology, Vin range (incl. transients/surge), Vout, load range & steps, switching frequency, efficiency, transient response, thermal environment, isolation, protection, EMC class, size, cost, standards.

## 2. Design review items
- Worst-case duty cycle, peak/RMS currents, ripple, losses, component stress at Vin_min/Vin_max and T_max.
- Semiconductors: V/I/surge ratings, SOA, gate charge & drive, switching/conduction/reverse-recovery loss, avalanche, thermal resistance; derate (e.g. ≤ 80 % V for MOSFETs, ≤ 50–60 % for electrolytics/ceramics V-derating policy as agreed).
- Inductors: saturation current at temperature (> peak current with margin), RMS/thermal current, DCR, core loss at frequency, shielding.
- Capacitors: ripple current rating, ESR/ESL, DC-bias derating (MLCC), temperature, lifetime (electrolytics).
- Protection: fuse/eFuse, current limit, OVP/UVLO, reverse polarity, TVS for surge, soft-start/inrush, thermal shutdown, discharge.
- Control loop: compensation for the actual output capacitance (with DC-bias), phase margin ≥ 45°, check with load-step test or Bode measurement.

## 3. Layout rules
- **Hot loop first**: input capacitor(s) (small MLCC closest), high-side switch, low-side switch/diode form the high di/dt loop — make it the smallest physical loop, ideally all on L1 with an unbroken GND plane on L2 directly below (thin dielectric) so the loop closes vertically ("vertical loop" for half-bridges with caps on the opposite side when layout favours it).
- Switch node: minimal area, wide enough for current; no sensitive traces near or under (except GND plane); snubber (RC) across the switch close to it if needed.
- Gate drive: driver close to the FET; gate and return (source/Kelvin source) routed as a tight pair; gate resistor at the FET; minimise common-source inductance (use Kelvin source pins).
- Current sense: Kelvin connections to the shunt pads (4-wire footprint), sense traces routed as a pair to the amplifier, filter RC at the amplifier input.
- Feedback: divider at the controller FB pin, sense from the output cap or load, route away from SW node and inductor.
- Power ground and signal ground: one plane; place the controller's quiet ground (AGND) where the plane is quiet (near the output cap return), connected at one point as the datasheet shows — not a separate floating plane.
- Thermal: copper area and thermal vias under FETs/controllers; heavy copper; heatsink mounting.
- High current paths: planes or wide pours on multiple layers stitched with many vias; check current density at necks and via counts.
- Inductor: no copper (or only GND) under shielded inductors per datasheet; keep unshielded inductors away from sensitive nodes and magnetic sensors.
- Isolation: transformer/optocoupler barrier spacing per `high-voltage-safety.md`.
- GaN/SiC: sub-nanosecond edges — loop inductance < ~1–2 nH, vendor-specific layouts (EPC, GaN Systems/Infineon, TI) — follow them strictly.

## 4. Common topologies notes
- Buck: input cap ↔ FETs loop is the hot loop; output side is relatively quiet.
- Boost: output cap ↔ FET/diode loop is the hot loop.
- Buck-boost/4-switch: two hot loops.
- Flyback: primary loop (bulk cap, primary, FET, sense R) and secondary loop (secondary winding, diode, output cap) both small; snubber/clamp close to FET; Y-cap across barrier.
- Half/full bridge & motor drivers: phase loops, bootstrap caps close to driver, bulk capacitance near bridge, shunt Kelvin sensing, dead-time.
- PFC (boost/totem-pole): high dv/dt; controller sensing and bulk cap placement; creepage on HV DC bus.

## 5. Safe testing (always mention for HV/high energy)
Current-limited supply for first power-up, isolation transformer for mains, differential probes, discharge bleeders verified, PPE, one hand rule, never probe energized HV with grounded scope probes.
