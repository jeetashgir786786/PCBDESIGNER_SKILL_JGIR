# PCB fabrication, DFM & release package

Fab capability numbers: see `fab-capabilities.md`. Via protection, HDI: `hdi-microvias.md`. Assembly: `assembly-test-dfa-dft.md`.

## 1. Before layout: get the fab's rules
Layer count, thickness range & tolerance, copper weights, min L/S per copper weight and layer, min drill & pad, annular ring, hole-to-hole, hole-to-copper, aspect ratio, blind/buried/microvia/back-drill support, via-in-pad, impedance tolerance, materials stocked, finishes, mask/legend minimums, edge clearance, panel rules, max dimensions, IPC class supported. Load them as DRC rules from day one.

## 2. Typical DFM values (tiers)
| Feature | Standard (low cost) | Advanced | Leading-edge |
|---|---|---|---|
| Line/space outer (1 oz base ½ oz + plating) | 4/4 mil (0.1 mm) | 3/3 mil | 2/2 mil |
| Line/space inner (½ oz) | 3.5/3.5 mil | 3/3 | 2/2 (mSAP ≤ 1.2 mil) |
| Mechanical drill (finished) | 0.2–0.3 mm | 0.15 mm | 0.10 mm (thin boards) |
| Via pad | drill + 0.2–0.25 mm | drill + 0.15 mm | drill + 0.1 mm |
| Annular ring | ≥ 0.15 mm (6 mil) | ≥ 0.1 mm | ≥ 0.075 mm |
| Aspect ratio (through) | ≤ 8–10:1 | 12–16:1 | 20–30:1 |
| Hole-to-hole (edge) | ≥ 0.25 mm | ≥ 0.2 mm | ≥ 0.15 mm |
| Hole-to-copper (inner) | ≥ 0.25 mm | ≥ 0.2 mm | ≥ 0.15 mm |
| Copper to board edge (routed) | ≥ 0.3 mm | ≥ 0.2 mm | ≥ 0.15 mm |
| Copper to V-score | ≥ 0.4–0.5 mm | | |
| Mask web (green) | ≥ 0.1 mm | ≥ 0.075 mm | |
| Mask expansion | 0.05 mm | 0.025–0.05 mm | 0 (SMD-defined) |
| Silkscreen line / text height | ≥ 0.15 / 1.0 mm | ≥ 0.1 / 0.8 mm | |
| Impedance tolerance | ±10 % | ±7–8 % | ±5 % |

## 3. Via protection (IPC-4761)
| Type | Name | Use |
|---|---|---|
| I-a/I-b | Tented (dry film) one/both sides | Cheap; can trap chemistry; not recommended one-sided with some finishes |
| II-a/II-b | Tented and covered (+LPI) | Slightly better |
| III-a/III-b | Plugged (non-conductive paste) | ICT vacuum, prevents solder flow |
| IV-a/IV-b | Plugged and covered | Better protection |
| V | Filled (fully, no cap) | |
| VI-a/VI-b | Filled and covered (mask) | Good general-purpose protection (NCAB default when unspecified) |
| VII | Filled and capped (plated over) | Required for via-in-pad / VIPPO and stacked on buried vias |
Specify the type on the fab drawing per via class (e.g. "BGA VIP: IPC-4761 Type VII, non-conductive fill; all other vias Type VI-b").

## 4. DFM checklist
- Board outline closed, single contour, on the correct layer; internal cut-outs defined; slot widths ≥ fab min; inside corner radius ≥ router bit radius (typ. 0.4–0.5 mm unless specified sharp).
- Copper-to-edge clearance on all layers, inner planes pulled back (≥ 0.3–0.5 mm) unless edge plating/castellation intended.
- Acid traps, slivers (< min width copper or mask), starved thermals, isolated copper islands (remove or stitch), unconnected via stubs.
- Annular ring after worst-case registration; teardrops on small rings.
- Drill table: finished vs drilled size (fab adds ~0.1 mm), plated/non-plated separation, slot definitions, back-drill & blind/buried spans as separate files.
- Copper balance per layer and between mirror layers; thieving in large empty areas (outside impedance-critical zones).
- Solder mask: openings on all pads, webs between fine-pitch pads (or gang relief where impossible), via tenting/plugging consistent with IPC-4761 callout, mask clearance on fiducials.
- Silkscreen: not on pads/exposed copper, readable size, polarity marks, board name/rev/date, UL/CE marks if needed.
- Panelisation: rails 5–10 mm with fiducials & tooling holes, V-score only for straight edges (no overhanging parts within ~1 mm), tab-routing with mouse bites (5 × 0.5 mm holes typical), break-away clearances.
- Impedance coupons and notes; thickness measurement point defined (over copper or over laminate?).
- Material callout: laminate (IPC-4101 slash or product), Tg, finish, mask colour, legend colour, copper weights, class, bow & twist limit, RoHS, UL marking.

## 5. Output package (release)
1. Gerber X2 (preferred) or RS-274X: every copper layer, mask top/bottom, paste top/bottom, silkscreen top/bottom, outline/profile, mechanical/fab drawing layer.
2. Excellon drill: PTH and NPTH separate; per span for blind/buried; back-drill files; drill map.
3. ODB++ or IPC-2581 (strongly preferred for ≥ 8 layers, HDI, back-drill, impedance) — the fab can import stackup, nets and spans without interpretation errors.
4. IPC-D-356 netlist for electrical test.
5. Fab drawing (PDF): outline dimensions & tolerances, stackup table, impedance table, drill table, via protection types, notes (class, material, finish, colour, thickness, test, marking).
6. Assembly: BOM, CPL, assembly drawings, 3D STEP.
7. Source project archive (CAD files, libraries) and README with revision, tool versions, outstanding issues.
Always open the Gerbers/drills in an independent viewer (KiCad GerbView, gerbv, Tracespace, fab's online viewer) and compare with the layout before ordering.

## 6. Standard fab drawing notes (edit to suit)
1. Fabricate per IPC-6012 Class 2 (or 3), acceptability per IPC-A-600.
2. Material: IPC-4101/126 (Tg ≥ 170 °C, Td ≥ 340 °C) or as specified per layer in the stackup table; UL 94 V-0.
3. Finished thickness X.XX mm ± 10 % measured over outer copper.
4. Copper: inner ½ oz/1 oz, outer 1 oz finished minimum.
5. Surface finish ENIG per IPC-4552B.
6. Solder mask LPI green both sides, per IPC-SM-840 Class T/H; legend white, non-conductive epoxy ink.
7. Controlled impedance per table ±10 %; fabricator may adjust trace widths ±X mil and dielectric thicknesses to meet impedance — submit stackup for approval.
8. Via protection per IPC-4761 types listed.
9. Bow & twist ≤ 0.75 %.
10. 100 % electrical test against IPC-D-356 netlist.
11. Back-drill per drill files; max residual stub X mil; must-not-cut layers listed.
12. Fabricator's UL mark, date code and lot code on bottom legend layer, location TBD by fab.
