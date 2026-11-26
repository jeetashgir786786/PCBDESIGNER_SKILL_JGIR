# HDI, microvias & via-in-pad

Governing documents: IPC-2226A (HDI design), IPC-2221B/C (generic), IPC-6012F & IPC-6016 (performance), IPC-4104 (HDI materials), IPC-A-600 (acceptability), IPC-T-50 (definitions), IPC-4761 (via protection).

## 1. Definitions
- **Microvia** (IPC-T-50M): blind structure, aspect ratio ≤1:1, total depth ≤0.25 mm from capture land to target land. Typical laser diameter 75–150 µm (3–6 mil) through 50–100 µm dielectric. Typical realised AR 0.6–0.8:1 (e.g. 4 mil dielectric with 5 mil hole).
- Microvia AR = (dielectric thickness + target copper if counted) / hole diameter — keep ≤0.8:1 for production margin, ≤1:1 absolute.
- **Capture land** – pad on the layer where the laser enters. **Target land** – pad on the layer where it stops.
- **Build-up layer** – thin dielectric + copper laminated onto a core in sequential lamination cycles.
- Notation **i+N+i**: i build-up layers each side of an N-layer core (1+N+1, 2+N+2, 3+N+3). "Order" = number of build-up lamination cycles per side. **ELIC / any-layer**: every layer interconnected by stacked copper-filled microvias.

## 2. IPC-2226 construction types
| Type | Description |
|---|---|
| I | 1[C]0 or 1[C]1 – one microvia layer on one/both sides of a core with plated through-holes; no buried vias |
| II | 1[C]0 or 1[C]1 – like Type I but core contains buried vias |
| III | ≥2[C]≥0 – two or more microvia layers on at least one side; core may have buried vias (most common modern HDI) |
| IV | ≥1[P]≥0 – microvia layers over a passive (non-electrical) core, e.g. metal/constraining core |
| V | Coreless, built from layer pairs |
| VI | Alternate constructions (e.g. conductive-paste / ALIVH-like any-layer) |

## 3. When HDI is required
| BGA pitch | Typical approach |
|---|---|
| ≥1.0 mm | Through-via dog-bone; HDI only for density |
| 0.8 mm | Through-via dog-bone (0.2–0.25 mm drill, 0.45 mm pad, 1 trace at ~3.5–4 mil) or VIPPO |
| 0.65 mm | VIPPO through vias, or 1+N+1 microvia-in-pad |
| 0.5 mm | Microvia-in-pad, 1+N+1 for small ball counts; 2+N+2 for large arrays |
| 0.4 mm | 2+N+2 or 3+N+3 with stacked/staggered microvias, 2.5–3 mil lines |
| ≤0.35 mm (WLCSP) | Any-layer / mSAP (semi-additive) 25–30 µm lines |
Rule: if no trace fits between two pads of the outer rows with fab-capable L/S, you need via-in-pad; if inner rows cannot escape with available through-via channels, you need more build-up layers.

## 4. Design rules (typical; replace with the fab's sheet)
| Feature | Mainstream HDI | Advanced |
|---|---|---|
| Laser via drill | 100 µm (4 mil) | 75 µm (3 mil) |
| Capture/target pad | drill + 125–150 µm (e.g. 0.25 mm pad for 0.10 mm via) | drill + 100 µm |
| Build-up dielectric | 60–100 µm (1067/1078/1080/106 spread glass or RCC) | 40–50 µm |
| Line/space build-up | 75/75 µm (3/3 mil) | 50/50 µm; mSAP 25–30 µm |
| Microvia fill | Copper-filled (required for stacking and via-in-pad), dimple ≤ 15–25 µm | |
| Stacked layers | ≤2–3 stacked; staggered preferred | any-layer |
| Buried core via | 0.15–0.25 mm mech. drill, resin-filled & capped if microvia lands on it | |
Example published capability (JLCPCB HDI, Nov 2026): 4–24 layers, 1st–3rd order, laser via 0.075–0.15 mm (pad = via + 6 mil, ≥3 mil ring), laser AR ≤1:1, mechanical AR ≤16:1, 3/3 mil (2.7/2.7 extreme), via-to-via same net ≥5 mil / different net ≥9.5 mil, S1000-2M / NP-175F Tg170, 0.5–3.0 mm thick, copper-filled laser vias (≤25.4 µm recess). Verify current values before design.

## 5. Reliability (IPC-6012F context)
- Stacked microvias have a known failure mode: separation at the interface between the microvia bottom and the target pad (weak interface) after multiple reflows, often latent (passes electrical test, fails in field). IPC-6012F and IPC-TM-650 2.6.27 reflow simulation + IST testing address this.
- Prefer **staggered** microvias; if stacking is necessary, limit to 2 high, ensure copper-filled, ask for reflow-simulation/IST data on the construction, and avoid stacking directly on a buried mechanical via unless it is resin-filled and copper-capped (IPC-4761 Type VII).
- Skip vias (L1→L3) save a lamination but have AR and plating challenges; confirm fab support.
- Number of sequential laminations is limited by material (resin degradation). Choose HDI-qualified, high-Td laminates.

## 6. Via-in-pad (VIPPO / POFV)
- Through or blind via inside an SMT pad, filled (non-conductive epoxy usually; conductive for thermal), planarised and copper-capped = IPC-4761 Type VII.
- Required to stop solder wicking and voids in BGA/QFN pads. Unfilled vias in pads cause solder starvation and voids — never leave open vias in BGA pads.
- Thermal pads: a filled-and-capped via array is ideal; if cost-constrained, use tented vias at the pad edge, or small (0.2–0.3 mm) open vias with the fab's approval and paste windowpane.
- Many fabs now include via-in-pad by default for 6+ layers (e.g. JLCPCB uses epoxy/copper-paste filled-and-capped vias 0.15–0.55 mm). Still state it on the fab drawing.

## 7. HDI layout practice
- Plan via spans as "layer pairs" in CAD (L1–L2, L2–L3, L3–L22 buried, …) matching the fab's build.
- Route the dense BGA escape on build-up layers; use the core for long routes and planes.
- Make the first build-up layer below the BGA a GND reference where possible (L2 = GND for L1 fan-out) — or route on L2 with L3 as reference.
- Thin build-up dielectrics mean narrow 50 Ω lines; recompute impedance per layer.
- Laser vias in RF/SerDes paths have small parasitics — HDI improves SI (no stubs) as well as density.
- Teardrops on microvia capture pads for small annular rings.
- Avoid microvias at the very edge of thermal pads where solder volume matters; fill/cap them.
- Ask the fab for the copper-fill dimple/bump spec and planarity for via-in-pad under 0.4 mm BGAs.
