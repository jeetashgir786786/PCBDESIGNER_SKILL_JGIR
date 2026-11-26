# High voltage, clearance, creepage & isolation

Functional spacing (IPC-2221) is NOT safety spacing. For anything connected to mains, > 60 V DC / 30 V rms (SELV limits vary by standard), batteries with high fault energy, or user-touchable isolated circuits, the product safety standard (IEC 62368-1, 61010-1, 60601-1, 60335-1, UL equivalents) governs, usually via IEC 60664-1 insulation coordination. State which standard and edition you used; recommend certified review.

## 1. Definitions
- **Clearance** – shortest path through air. Depends on peak working voltage, transient (impulse) voltage from the overvoltage category, altitude (> 2000 m multiplier), pollution degree.
- **Creepage** – shortest path along insulating surfaces. Depends on rms working voltage, pollution degree, material group (CTI).
- **Distance through insulation (DTI)** – solid insulation thickness (e.g. inner-layer spacing in a PCB can count as solid insulation under conditions — check the standard; often ≥ 0.4 mm for reinforced, or qualified thin-layer rules).
- **Insulation types** – Functional, Basic, Supplementary, Double (= Basic + Supplementary), Reinforced (single system equivalent to double).
- **Pollution degree** – PD1 sealed/coated; PD2 normal indoor (non-conductive pollution, occasional condensation) – default for most electronics; PD3 industrial/conductive pollution.
- **Material group (CTI)** – I ≥ 600, II 400–599, IIIa 175–399, IIIb 100–174. Standard FR-4 is usually IIIa/IIIb unless the laminate datasheet states higher CTI; high-CTI FR-4 grades reach 600 V.
- **Overvoltage category** – OVC I (protected), II (appliances on mains outlets), III (fixed installation), IV (origin of installation).

## 2. IPC-2221B Table 6-1 (functional conductor spacing, mm)
Columns: B1 internal conductors; B2 external uncoated ≤ 3050 m; B3 external uncoated > 3050 m; B4 external with permanent polymer coating (e.g. solder mask); A5 external with conformal coating over assembly; A6 external component lead/termination uncoated; A7 external component lead/termination with conformal coating.
| V peak (DC or AC peak) | B1 | B2 | B3 | B4 | A5 | A6 | A7 |
|---|---|---|---|---|---|---|---|
| 0–15 | 0.05 | 0.1 | 0.1 | 0.05 | 0.13 | 0.13 | 0.13 |
| 16–30 | 0.05 | 0.1 | 0.1 | 0.05 | 0.13 | 0.25 | 0.13 |
| 31–50 | 0.1 | 0.6 | 0.6 | 0.13 | 0.13 | 0.4 | 0.13 |
| 51–100 | 0.1 | 0.6 | 1.5 | 0.13 | 0.13 | 0.5 | 0.13 |
| 101–150 | 0.2 | 0.6 | 3.2 | 0.4 | 0.4 | 0.8 | 0.4 |
| 151–170 | 0.2 | 1.25 | 3.2 | 0.4 | 0.4 | 0.8 | 0.4 |
| 171–250 | 0.2 | 1.25 | 6.4 | 0.4 | 0.4 | 0.8 | 0.4 |
| 251–300 | 0.2 | 2.5 | 12.5 | 0.4 | 0.4 | 0.8 | 0.8 |
| 301–500 | 0.25 | 2.5 | 12.5 | 0.8 | 0.8 | 1.5 | 0.8 |
| > 500, per volt above 500 V (add to 500 V value) | 0.0025 | 0.005 | 0.025 | 0.00305 | 0.00305 | 0.00305 | 0.00305 |
Example: B1 at 600 V → 0.25 + 100 × 0.0025 = 0.50 mm. IPC-2221C (2023) revised the table layout; verify against your licensed copy before release. Use `scripts/pcb_calc.py ipc2221-spacing`.
Solder mask is not reliable safety insulation; do not count it toward creepage for safety unless the standard allows it.

## 3. Practical safety spacing (orientation only — look up the actual table)
For 230 V mains, PD2, material group IIIb, OVC II, ≤ 2000 m (IEC 62368-1 / 60664-1 style): basic insulation typically ~2.0–2.5 mm clearance/creepage; reinforced typically ~4–6.4 mm creepage and ~4 mm clearance. Medical (60601-1, 2 MOPP) needs ~8 mm creepage at 230 V. These are the reasons isolated power supplies and optocouplers have 8 mm-class footprints. Always calculate from the governing standard's tables for your working voltage, PD, CTI, altitude.

## 4. Layout techniques
- Draw an explicit **isolation barrier** on a dedicated mechanical/user layer and keepout zones on all copper layers (inner layers too — inner layers count for clearance/DTI rules).
- Route slots (milled cut-outs, ≥ 1 mm wide typically) increase creepage; they do not increase clearance through air beyond the geometry. Slots < ~1 mm (PD2; depends on standard) may be ignored for creepage.
- Keep components that bridge the barrier (optocouplers, digital isolators, transformers, Y-caps) rated for the insulation class; their footprints must not shrink the gap (check pad-to-pad across the barrier).
- No vias, planes or pours within the barrier on any layer; no silkscreen ink bridging the barrier is relevant for some standards (ink can be conductive-ish/tracking) — keep it clear.
- Round HV copper corners and avoid sharp points (corona at kV levels); use teardrops/curved traces.
- Conformal coating or potting can reduce required spacing only where the standard allows (coating qualified per IEC 60664-3 / UL 746E).
- Y-capacitors across isolation: Y1 for reinforced, Y2 for basic; total leakage current limits apply.
- Discharge resistors for bulk capacitors; high-voltage warning silkscreen; test points with shrouds.
- HV DC in humid environments: watch electrochemical migration and CAF; increase spacing, use CAF-resistant laminate and conformal coat.

## 5. High-current and battery safety
- Fuse or eFuse at every battery/source entry; size traces/planes and connectors for the fuse rating, not only the nominal current.
- Li-ion: protection IC + MOSFETs, NTC, fusible link; keep cell-tab welds and high-current paths short; creepage for pack voltage.
- TVS sized for the surge level (IEC 61000-4-5, ISO 7637-2/ISO 16750-2 load dump for automotive 12/24 V).
