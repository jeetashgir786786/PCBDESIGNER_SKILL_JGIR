# Stackup design: 2 to 32+ layers

Load for any multilayer board, any controlled-impedance work, and always before placement on 6+ layers. For 18+ layers also load `high-layer-count.md`; for microvias load `hdi-microvias.md`; for material choice load `materials-laminates.md`.

The stackup is decided BEFORE placement and routing. It fixes impedance geometry, return paths, PDN capacitance, via spans, board thickness, cost and lead time.

## 1. Rules that hold at every layer count
1. Every signal layer is adjacent to a solid reference plane. Inner high-speed layers sit between two planes (stripline).
2. Avoid two adjacent signal layers ("dual stripline"). If unavoidable (cost), route them orthogonally, make the S–S dielectric ≥3× the S–plane dielectric, and never put high-speed buses on both.
3. Prefer GND as the reference for high-speed layers. A power plane can be a reference only if it is AC-tied to GND by close, low-inductance capacitance (thin dielectric + stitching caps at every layer transition).
4. Pair power planes tightly with GND (≤3–4 mil / 75–100 µm dielectric) for plane capacitance and low spreading inductance.
5. Keep the stackup symmetric about the centre: mirror-image copper weights, dielectric thicknesses, plane/signal positions, and similar copper density. Asymmetry causes bow & twist (IPC limit 0.75 % for SMT).
6. Outer layers: components, short fan-out, low-speed, and microstrip only when necessary. Outer layers carry plating (≈ +25–35 µm), so geometry tolerance is worse than inner layers.
7. Use the fab's real materials and pressed thicknesses. Never design impedance from generic Dk; get the fab's stackup proposal, or their laminate list, and solve in a 2D field solver.
8. Specify: total thickness ± tolerance, layer order, copper weights (base + finished), dielectric type, glass style and resin content (if impedance-critical), Dk/Df at the frequency of interest, impedance targets per layer with reference planes, and via spans (through, blind, buried, back-drill).
9. Odd copper-layer counts (5, 7…) are possible but usually cost the same as the next even count and break symmetry — avoid.
10. Plane splits: one plane can carry several rails as islands, but no high-speed signal may cross a split on the adjacent layer.

## 2. Choosing the layer count
Drivers (take the maximum):
- **BGA escape**: count signal rows that must escape (see §5).
- **Routing density**: sum of required channel capacity / per-layer capacity.
- **Number of rails** that need planes or large pours (each high-current/low-noise rail ≈ one plane or a large island).
- **Interfaces**: each class of high-speed interface prefers its own GND-referenced stripline layer(s).
- **EMC**: products failing emissions on 4L often pass on 6L with GND-referenced routing.
- **Cost**: in volume, cost rises ~20–40 % per two added layers; a 2→4 jump often reduces total cost (smaller board, fewer EMC iterations).

Quick guide:
| Design | Typical |
|---|---|
| Simple MCU, LED, power stage, no fast edges | 2L (with GND pour) |
| MCU + USB FS/HS, Ethernet 100M, switching regulators | 4L |
| ESP32/nRF/STM32 with RF + several rails, QSPI, USB HS | 4–6L |
| DDR3/DDR4 single channel, 0.8 mm BGA SoC | 6–8L |
| FPGA/SoC 0.8–1.0 mm BGA, 400–900 balls, DDR4, PCIe Gen3/4 | 10–14L |
| Large FPGA/ASIC 1000–2500 balls, DDR4/5, many SerDes | 16–22L |
| Switch/GPU/AI baseboards, 3000–5000+ ball BGAs, 56/112G SerDes | 24–32L (often HDI + back-drill) |
| Backplanes, ATE load boards | 30–60L, 4–8 mm thick |

## 3. Reference stackups
Notation: `S` signal, `G` ground plane, `P` power plane (can be split), `S/G` signal layer with GND pour. Thickness values are typical for a 1.6 mm board and must be replaced by the fab's actual stackup.

### 2 layers (1.6 mm)
`S | core 1.5 mm | S/G` — keep the bottom as unbroken GND as much as possible; route most signals on top; short return paths. Controlled impedance on 1.6 mm two-layer needs very wide traces (~2.8–3 mm for 50 Ω microstrip) — use coplanar waveguide with ground (CPWG) instead.

### 4 layers
- **A (general, recommended):** `S | pp 0.1–0.2 | G | core ~1.1 | P | pp 0.1–0.2 | S`. L1 references G2; L4 references P3 → stitch caps near L4 high-speed routing, or keep high-speed on L1 only.
- **B (best SI/EMC):** `S+P pour | G | G | S+P pour` — both outer layers reference GND; route power as wide pours on signal layers.
- Thin outer prepreg (0.1 mm, JLC-style "JLC04161H-7628" vs "-2116" variants) gives narrower 50/90/100 Ω geometry.

### 6 layers
- **A (most common):** `S1 | G2 | S3 | P4 | G5 | S6`. S3 is offset stripline (G2/P4). Put the fastest signals on S1 (ref G2) or S3 if P4 is well decoupled.
- **B (high-speed heavy):** `S1 | G2 | S3 | G4 | P5 | S6`. S3 is a true GND/GND stripline. S6 references P5 (low-speed only there).
- **C (EMC-critical, few parts):** `G1 | S2 | P3 | G4 | S5 | G6` — outer ground shields; hard to place parts; rare.

### 8 layers
- **Recommended:** `S1 | G2 | S3 | G4 | P5 | S6 | G7 | S8`. S3 between G2/G4; S6 between P5/G7; P5–G4 tight pair.
- **Alternative (more planes):** `S1 | G2 | S3 | P4 | G5 | S6 | G7 | S8` with P4–G5 at ≤3 mil.

### 10 layers
`S1 | G2 | S3 | G4 | P5 | P6 | G7 | S8 | G9 | S10` — four true striplines would need 12L; here S3 and S8 are GND/GND striplines, P5/P6 are two power planes in the middle each coupled to an adjacent GND.

### 12 layers
`S1 | G2 | S3 | G4 | S5 | P6 | G7 | S8 | G9 | S10 | G11 | S12` (mirror-symmetric in plane/signal positions). Clean GND/GND striplines: S3, S8, S10. S5 references G4/P6.

### 14 layers
`S1 | G2 | S3 | G4 | S5 | G6 | P7 | P8 | G9 | S10 | G11 | S12 | G13 | S14` — 6 signal, 8 plane; every inner signal layer is a GND/GND stripline; two power planes in the centre each tightly coupled to GND.

### 16 layers
`S1 | G2 | S3 | G4 | S5 | G6 | S7 | P8 | P9 | S10 | G11 | S12 | G13 | S14 | G15 | S16` — 8 signal (6 inner), 8 plane. S7/S10 reference a power plane on one side — use them for medium-speed or keep the P8/P9 rails heavily decoupled.

### 20 layers
`S1 | G2 | S3 | G4 | S5 | G6 | S7 | G8 | S9 | P10 | P11 | S12 | G13 | S14 | G15 | S16 | G17 | S18 | G19 | S20` — 10 signal / 10 plane. For large ASICs, trade two signal layers for two more power planes (P/G pairs) — see high-layer-count.md.

### 24 layers (balanced, 10 signal / 14 plane, no dual striplines)
```
L1  S   top: components, BGA fan-out, short microstrip
L2  G
L3  S   ★ GND/GND stripline (fastest SerDes)
L4  G
L5  S   stripline G4/P6
L6  P   rail A (e.g. VCORE) – tight to G7
L7  G
L8  S   ★ GND/GND stripline
L9  G
L10 S   ★ GND/GND stripline
L11 G
L12 P   rail B – tight to G11
L13 P   rail C – tight to G14
L14 G
L15 S   ★ GND/GND stripline
L16 G
L17 S   ★ GND/GND stripline
L18 G
L19 P   rail D – tight to G18
L20 S   stripline P19/G21
L21 G
L22 S   ★ GND/GND stripline
L23 G
L24 S   bottom: decoupling caps, fan-out
```
Six premium stripline layers (★), two semi-premium (S5, S20), two outer. Typical finished thickness 2.4–3.2 mm with ~3–4 mil dielectrics and 0.5 oz inner signal / 1 oz planes. Through-via drill 0.25–0.30 mm → aspect ratio 10–13:1. Back-drill SerDes vias that exit on upper layers. Variants: replace S5/S20 by P/G for more rails (8 signal / 16 plane), or add HDI build-up (2+20+2) for ≤0.65 mm BGA pitch.

### 26–32 layers
Extend the 24L pattern by inserting `S | G` pairs symmetrically (one above and one below the centre). Keep: ≤1 signal layer between planes, power planes clustered near the centre tightly coupled to GND, highest-speed layers close to the side where the SerDes devices are placed (shorter via, shorter stub, or back-drill). 28–32L boards are typically 3.0–5.0 mm thick; confirm the fab's aspect-ratio limit for your smallest drill.

## 4. Dielectric and copper selection
- Signal layers: ½ oz (17–18 µm) inner copper allows narrower lines and thinner dielectrics; 1 oz for current-carrying inner signal layers.
- Planes: 1 oz typical; 2 oz for high-current rails (needs more prepreg resin to fill; check fab).
- Impedance-critical prepregs: use 2+ plies or spread glass (1067/1078/1086/1035) to limit glass-weave skew; specify resin content.
- Thin cores (≤0.1 mm, 2–4 mil) for P/G pairs; use ≥0.1 mm for signal-reference spacing when 85–100 Ω diff pairs must stay ≥3.5–4 mil wide (loss).
- Dk varies with resin content: a 1080 prepreg at RC 65 % may be Dk 3.9 while 7628 at RC 43 % is 4.6 for the same "FR-4". Use the fab's per-construction Dk.
- Hybrid stackups: low-loss material (e.g. Megtron 6/7, Tachyon, I-Speed, RO4350B) only on the layers carrying fast/RF signals, FR-4/high-Tg on the rest. Check CTE/lamination compatibility with the fab.

## 5. BGA escape → layer count estimate
For a full-array BGA with N rows from edge to centre (per side):
- Outer layer (L1): escapes rows 1–2 (row 1 direct, row 2 between row-1 pads if pitch allows one trace).
- Each inner routing layer escapes about `k` more rows, where `k` = number of traces that fit between two adjacent vias (1 for 0.8 mm pitch with 0.2/0.45 mm vias and 3.5 mil lines; 2 for 1.0 mm pitch with 4/4 mil). Through-via dog-bones block channels on every layer; microvias/via-in-pad free them.
- Signal layers needed ≈ 1 + ceil((N_signal_rows − 2) / k). Power/GND balls in the centre reduce N_signal_rows; power balls escape on planes, not signal layers.
- Then add planes: each signal layer needs a reference; add one P/G pair per major rail group.
Example: 1.0 mm pitch, 33×33 BGA (N ≈ 16 rows/side), centre 8×8 is power/GND → ~12 signal rows, k = 2 → 1 + ceil(10/2) = 6 signal layers → with references and 3 power planes → 14–16L. Verify against the vendor's PCB design guide (Xilinx UG583/UG863, Intel/Altera, NXP, TI), which usually gives a recommended layer count.

## 6. Impedance targets (typical; confirm with the interface spec / vendor)
| Use | Target |
|---|---|
| General single-ended, RF | 50 Ω |
| DDR4/DDR5 DQ/CA (vendor dependent) | 34–50 Ω SE, 70–90 Ω diff (CK/DQS) |
| USB 2.0 / USB 3.x / USB4 | 90 Ω diff (USB4/TBT often 85 Ω) |
| PCIe Gen3+ | 85 Ω diff (100 Ω also tolerated in older guides) |
| Ethernet MDI, HDMI, DisplayPort, LVDS, MIPI D-PHY, SATA | 100 Ω diff (SATA 85–100) |
| 25/56/112G Ethernet SerDes | 90–100 Ω diff (per device guide, often 92–100) |
Fab tolerance: ±10 % standard, ±7 % advanced, ±5 % premium (expensive; needs coupon + TDR).

## 7. Stackup documentation template
```
Board: <name> rev <x>   Layers: <n>   Finished thickness: <t> ± <tol>   Class: IPC-6012 Class <2/3>
Material: <laminate/prepreg family, Tg, Td>   Finish: <ENIG/...>   Mask/legend: <...>
| Layer | Type | Cu base/finished | Dielectric after (type, glass, RC%, thickness, Dk/Df @ f) |
| Impedance table: net class | layer | ref planes | type (SE/diff) | width/space | target ± tol |
| Drill spans: through | blind Lx–Ly | buried Lx–Ly | back-drill from <side> to Lz, max stub <mil> |
| Via fill: IPC-4761 type <VII for VIP> |
```
Send this to the fab and ask them to return their engineered stackup with predicted impedance and final widths before routing starts.
