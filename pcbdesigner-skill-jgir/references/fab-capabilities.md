# Fab capability snapshots

Snapshot compiled Nov 2026 from fab websites. Capabilities and prices change frequently — re-check the fab's live capability page and order form before committing a design. Treat these as planning values, not guarantees.

## JLCPCB (jlcpcb.com/capabilities)
- Layers 1–32 (standard production); controlled impedance offered on 4–32 layers; impedance ±10 % standard (±5 % on request).
- Thickness 0.4–4.5 mm; standard 0.4/0.6/0.8/1.0/1.2/1.6/2.0 mm; ≥ 2.5 mm for 12+ layers; tolerance ±10 % (≥ 1 mm).
- Copper: outer multilayer 1 or 2 oz; inner 0.5 (default), 1, 2 oz.
- Trace/space: 2-layer 4/4 mil; multilayer 3.5/3.5 mil (3 mil in BGA fan-out); 2 oz ~6 mil.
- Drill: min 0.15 mm (0.10 mm only for ≤ 1 mm boards with ENIG/OSP); via 0.15/0.25 mm min (0.2 mm hole preferred); via-to-via 0.2 mm; pad-to-pad hole spacing 0.45 mm.
- Annular ring (multilayer, 1 oz): 0.20 mm recommended, 0.15 mm absolute minimum.
- Via-in-pad (epoxy or copper paste filled and capped) 0.15–0.55 mm, default for 6+ layers.
- Mask bridge 0.10 mm (green etc.), 0.13 mm black/white; silkscreen ≥ 0.15 mm line, ≥ 1.0 mm text.
- Edge clearance ≥ 0.2 mm routed, ≥ 0.4 mm V-cut.
- HASL not available for 6+ layers or ≤ 0.4 mm boards; ENIG/OSP instead.
- Prepreg Dk (FR-4): 7628 ≈ 4.4, 3313 ≈ 4.1, 2116 ≈ 4.16; HDI base S1000-2M / NP-175F (Tg 170).
- **HDI (launched Sep 2026):** 4–24 layers, 1st–3rd order (stacked & staggered; skip via built as stacked), laser via 0.075–0.15 mm, pad = via + 6 mil (≥ 3 mil ring), laser AR ≤ 1:1, mechanical buried/through AR ≤ 16:1, buried via 0.15–0.55 mm (0.10 extreme for ≤ 1 mm span), 3/3 mil (2.7/2.7 extreme), via-to-via 5 mil same net / 9.5 mil different net, laser via ≥ 0.35 mm from edge, thickness 0.5–3.0 mm, copper-filled laser vias, impedance ±10 % (≥ 50 Ω) / ±5 Ω (< 50 Ω).
- Use JLCPCB's published stackups (impedance calculator) — design to their exact prepreg/core combination.

## PCBWay (pcbway.com/capabilities, advanced & HDI pages)
- Standard: 1–14 layers; advanced up to 64 layers listed (evaluation above ~30); HDI up to 60 layers listed with builds 1+N+1 … 6+N+6 (≥ 6 orders need evaluation), any-layer examples shown.
- Min L/S: 2/2 mil locally (advanced); HDI 0.065/0.065 mm; finished copper 1/3–8 oz; thickness 0.1–8.0 mm (evaluation outside 0.2–6.5 mm).
- Plug via 0.15 mm (CNC) / 0.1 mm (laser).
- Materials: FR-4, high-Tg, halogen-free, PTFE/Rogers, ceramic, polyimide; rigid-flex up to 16 layers.

## Generic advanced / server-class fabs (TTM, Unimicron, Tripod, WUS, Victory Giant, Sanmina, etc.)
- 30–60+ layers, AR 20–30:1+, back-drill with ±2–4 mil depth control and ≤ 6 mil residual stubs, ±5–7 % impedance, Megtron 7/8 & Tachyon processing, any-layer HDI, coins/inlays.
- Example published backplane tiers (Sanmina): max layers 36 / 60 / > 60; thickness up to 0.225″ / 0.400″ / > 0.400″; AR 20:1 / 30:1 / > 30:1; impedance ±10 / 7 / 5 %.

## How to use
1. Pick the fab before the stackup.
2. Encode their limits as DRC rules (KiCad: Board Setup → Design Rules + custom rules file).
3. Use their stackup/impedance tool or request an engineered stackup.
4. Stay one notch above their minimums where you can (yield & cost).
5. For anything beyond their standard page (HDI order > 1, back-drill, any-layer, ±5 %), get written confirmation (engineering query) before routing.
