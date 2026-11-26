# RF & antenna layout

## 1. Inputs to capture
Bands, radio IC/module, antenna type (chip, PCB trace/IFA/MIFA, patch, external via U.FL/SMA), conducted power, sensitivity, regulatory region (FCC/ISED/CE-RED/MIC/SRRC), enclosure material and nearby metal, battery/display placement, certification route (pre-certified module vs chip-down).

## 2. Transmission lines
- 50 Ω grounded coplanar waveguide (GCPW) on L1 referenced to L2 GND is the default: thin L1–L2 dielectric gives narrow lines that match 0402/0201 pads.
- Field-solve with the fab's dielectric; include mask or remove mask over the line (consistent with the solver).
- Via fence along both sides of RF lines: spacing ≤ λ/10 (≤ λ/20 preferred) in the dielectric; vias close to the gap edge.
- Curved bends or mitred 45°; avoid stubs; keep RF lines short and on one layer; if a via is unavoidable, surround it with GND vias (coaxial via).
- Match pad/component footprints to the line width or taper; remove GND under large pads on L2 (cut-out) to compensate capacitance when field-solving says so.

## 3. Matching networks
- Pi or T network footprints (0402/0201) placed at the radio and at the antenna feed even if the vendor values say 0 Ω/DNP — tuning on the real board is normal.
- Calculated values ignore parasitics of the actual layout and enclosure; tune with a VNA (antenna S11 in the final enclosure) and verify radiated performance (OTA/TRP/TIS) in a chamber if required.

## 4. Antennas
- Follow the antenna/module vendor's reference layout exactly: ground plane size, clearance (no copper on any layer), feed geometry, distance to enclosure and metal.
- Antenna at a board edge/corner, away from batteries, displays, shields, inductors, cables. Keep the keepout through ALL layers.
- Module with integrated antenna: place per datasheet (usually antenna overhanging the board edge or over a copper-free keepout).
- Chip antennas need a specific ground clearance and board length; ground plane length strongly affects 2.4 GHz and sub-GHz efficiency.
- NFC coils: inductance target with tuning caps; ferrite sheet if near metal.

## 5. Shielding & isolation
- Shield-can footprints (frames or clips) with dense GND via stitching; divide RF/PA/LNA/digital compartments.
- Separate RF, PA supply decoupling (multiple values near PA pins, low-ESL), LO/crystal traces short and guarded.
- Keep digital high-speed lines and switching regulators away from RF; filter supplies into RF sections (ferrite + caps), but check bead resonance at the RF band.

## 6. Materials
- FR-4 fine up to ~6 GHz for short lines; use low-loss/RF laminates (RO4350B, RO4003C, Megtron) for long lines, filters, mmWave or phase-critical arrays; hybrid stackups keep cost down.
- Finish: ImAg/OSP/ENEPIG preferred over ENIG for low loss (nickel is lossy/magnetic), especially > 10 GHz.

## 7. Never promise
Range, sensitivity, emissions or certification pass without measurement. Recommend pre-certified modules when the user lacks RF test equipment.
