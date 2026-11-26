# Materials, laminates, copper foils & surface finishes

All numbers are typical datasheet-level values for orientation. Dk/Df depend on frequency, resin content, glass style and test method (IPC-TM-650 2.5.5.x). Always use the laminate vendor's construction tables and the fab's stocked materials for final design.

## 1. Key properties
| Property | Why it matters | Typical target |
|---|---|---|
| Tg (DSC/TMA) | Above Tg, Z-CTE jumps ~4–5× | ≥150 °C general lead-free; ≥170 °C for 8+ layers, thick or multiple-reflow boards |
| Td (5 % wt loss) | Resin decomposition in reflow | ≥325 °C lead-free; ≥340 °C high-reliability |
| T260 / T288 | Time to delamination | T260 ≥30 min, T288 ≥5–15 min for high-layer boards |
| Z-CTE (50–260 °C) | Barrel cracking | ≤3.5 % total expansion; lower for thick boards |
| Dk (εr) | Impedance & delay | 3.0–4.6 |
| Df (tan δ) | Dielectric loss ∝ f·√Dk·Df | 0.001–0.02 |
| CTI (comparative tracking index) | Creepage (material group) | FR-4 often PLC 3 (175–250 V); high-CTI grades ≥600 V (group I) |
| Moisture absorption | Dk drift, popcorning | low for RF/low-loss |
| CAF resistance | Hole-to-hole reliability | needed for fine pitch, high voltage, humid use |
| Halogen-free | Regulatory | IEC 61249-2-21 |

## 2. Laminate tiers (approximate @ ~10 GHz unless noted)
| Tier | Examples | Dk | Df | Use up to (rule of thumb, depends on length) |
|---|---|---|---|---|
| Standard FR-4 (Tg 130–140) | generic, KB-6160, S1141 | 4.2–4.6 | 0.016–0.022 | ≤1–3 Gbps, general digital |
| High-Tg FR-4 | S1000-2M, IT-180A, 370HR, NP-175F | 3.9–4.4 | 0.014–0.020 | multilayer lead-free, ≤5–8 Gbps short |
| Mid-loss | FR408HR (Dk ~3.65, Df ~0.009), Megtron 4, IT-170GRA, S1000-2 variants | 3.6–3.9 | 0.007–0.010 | 8–16 Gbps (PCIe 3/4, 10G) |
| Low-loss | Megtron 6 (R-5775), I-Speed, IT-968, TU-872SLK, EM-888 | 3.3–3.7 | 0.003–0.006 | 25–32 Gbps NRZ (PCIe 5, 25G), 56G short |
| Very/ultra-low loss | Megtron 7 (R-5785), Tachyon 100G, TU-933, Megtron 8 (R-5795) | 3.0–3.4 | 0.0012–0.0025 | 56/112G PAM4, PCIe 6/7, 800G |
| RF hydrocarbon-ceramic | Rogers RO4003C (3.38/0.0027), RO4350B (3.48 process, 3.66 design / 0.0037) | 3.3–3.7 | 0.002–0.004 | RF to ~30 GHz, FR-4 process compatible |
| PTFE | RO3003 (3.00/0.001), RT/duroid 5880 (2.20/0.0009), Taconic | 2.2–3.0 | ≤0.0015 | mmWave, radar, antennas (harder to process) |
| Polyimide (flex/rigid) | DuPont Pyralux AP, Panasonic Felios | 3.2–3.5 | 0.002–0.01 | flex, high temperature |
| Metal core (IMS) | Al/Cu base + thermally conductive dielectric (1–8 W/m·K) | — | — | LED, power |
Published reference points: Megtron 6 ≈ Dk 3.6 / Df 0.002–0.004 and Megtron 8 ≈ Dk 3.3 / Df ≈0.0018 at 10 GHz (vendor/fab literature); Panasonic states Megtron 8 gives ~30 % lower transmission loss than Megtron 7.

### Hybrid stackups
Use expensive low-loss material only on layers carrying fast/RF signals (and their reference dielectrics); FR-4 / high-Tg elsewhere. On a 24–30 layer AI/server board, often only 4–8 layers carry 112G lanes. Confirm with fab: compatible lamination cycle, CTE, drilling/desmear chemistry (PTFE needs plasma), and Dk per layer.

## 3. Glass styles (E-glass unless stated)
| Style | Approx. pressed thickness | Notes |
|---|---|---|
| 106 | ~50 µm (2 mil) | open weave, high resin; laser-drillable |
| 1067 | ~50 µm | spread version of 106; better for laser & skew |
| 1035 | ~30 µm | very thin spread glass |
| 1078 / 1086 | ~75–85 µm | spread; preferred for high-speed |
| 1080 | ~65–85 µm | common thin prepreg |
| 2113 / 2116 | ~100–125 µm | medium |
| 3313 | ~95–100 µm | spread-ish, good for impedance |
| 1506 / 7628 | ~150–200 µm | heavy, coarse weave — worst skew, highest Dk; cheap |
- Low-Dk glass (NE-glass, L-glass, "low-Dk glass" options in Megtron 7/8 N variants) lowers Dk and skew; ultra-low-Df glass ("U" variants) lowers loss. Supply of some specialty glass (T-glass, low-CTE) was constrained in 2025–2026 — check availability early.
- Glass-weave skew mitigation, in order of effectiveness/cost: spread/flat glass; 2 plies instead of 1; low-Dk glass; route at an angle (10–15°) or zig-zag relative to the weave, or rotate the image on the panel (10°, costs panel utilisation); keep both legs of a pair tightly coupled; avoid long straight runs parallel to the weave; length-match per segment. Measured example in literature: routing along the weave gave ~1.7 ps/in (1035) to ~5 ps/in (1078) skew vs ~0.2 ps/in when angled.

## 4. Copper foil
| Type | Rz (treated side, approx.) | Use |
|---|---|---|
| STD ED | 6–10 µm | general |
| RTF (reverse-treated) | 3–5 µm | mid-loss boards |
| VLP | ~3–4 µm | low-loss |
| HVLP / HVLP2–4 | ≤1.5–2 µm | 25G+ / 112G |
| RA (rolled annealed) | smooth, ductile | dynamic flex |
- Roughness loss matters once skin depth (2.1 µm @1 GHz, 0.66 µm @10 GHz) is smaller than roughness; at 25 GHz standard foil can add ~1 dB/in vs HVLP (stripline, fab literature). At 28 Gbps, foil choice can matter as much as the laminate Df.
- Oxide/oxide-alternative bonding treatment roughens inner layers again — ask the fab for low-roughness bonding chemistry on high-speed layers.
- Model with the Huray (cannonball) or Hammerstad model using vendor Rz/Rq.

## 5. IPC-4101 slash sheets
Specify the laminate by IPC-4101 slash sheet on the fab drawing ("IPC-4101/126 or equivalent") rather than by brand only, unless SI requires a specific product. Common lead-free high-reliability callouts are /99, /101, /124, /126, /129 (Tg ≥150–170 °C, Td ≥ 325–340 °C, filled resins). Check exact requirements in the current IPC-4101 revision before quoting a slash number.

## 6. Surface finishes
| Finish | Pros | Cons / notes | Std |
|---|---|---|---|
| HASL (SnPb) | cheap, robust solderability | not flat (bad for ≤0.5 mm pitch/BGA), not RoHS | — |
| LF-HASL (SnCuNi) | cheap, RoHS | uneven, thermal shock to board; many fabs refuse for 6+ layers or ≤0.4 mm boards | — |
| ENIG | flat, good shelf life, wire-bondable (Al) | black-pad risk, Ni is lossy/magnetic at GHz, cost | IPC-4552B |
| ENEPIG | flat, Au & Al wire bond, no black pad | cost | IPC-4556 |
| Immersion silver | flat, low loss (good for RF) | tarnish, creep corrosion in sulphur environments | IPC-4553A |
| Immersion tin | flat, press-fit friendly | tin whiskers, limited reflows | IPC-4554 |
| OSP | flat, cheapest, lowest loss | short shelf life, limited reflows, ICT probing harder | — |
| Hard (electrolytic) gold | wear-resistant edge fingers, contacts | expensive, bevel + tie bars needed | — |
Choose ENIG/ENEPIG or ImAg for fine-pitch BGA; OSP/ImAg for lowest RF loss; hard gold for card-edge connectors (typ. 0.76 µm / 30 µin Au over Ni, 20–45° bevel).

## 7. Solder mask & legend
- LPI mask, typical 10–25 µm over copper; Dk ~3.3–4; reduces outer-layer impedance a few ohms — include in solver.
- Green has the best resolution (smallest dams); black/white need larger webs.
- Remove mask over RF microstrip/antenna areas only if the design accounts for it (and finish chosen accordingly).
- Legend: min line ≥0.15 mm, text height ≥0.8–1.0 mm for most fabs; never on pads.
