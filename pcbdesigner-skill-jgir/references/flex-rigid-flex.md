# Flex & rigid-flex design

Standards: IPC-2223 (rev E) design, IPC-6013 (rev E) performance, IPC-4202/4203/4204 materials.

## 1. Constructions
- Single-sided, double-sided, multilayer flex; rigid-flex (rigid sections with flex layers continuing through); bookbinder (staggered lengths for many-layer bends); air-gap (unbonded flex layers in the bend).
- Materials: polyimide core (adhesiveless preferred – better reliability, thinner), coverlay (PI + adhesive) instead of solder mask, LPI flexible mask for fine pitch, stiffeners (FR-4, PI, stainless steel, aluminium), PSA tapes, EMI shielding films (silver film) bonded to GND.
- Copper: RA (rolled annealed) for dynamic flex – grain along the bend direction; ED acceptable for static.

## 2. Bend radius (IPC-2223 rule-of-thumb multiples of total flex thickness)
| Application | Layers in bend | Minimum radius |
|---|---|---|
| Static (flex-to-install, < ~100 cycles) | 1–2 | 6–10× |
| Static | 3+ | 12–20× (or more) |
| Dynamic (thousands–millions of cycles) | 1 (preferred), 2 max | 100× (up to ~150× for double-sided) |
Better: compute from IPC-2223 equations using allowed copper elongation (≈16 % single-crease RA, ~10 % flex-to-install, ~0.3 % dynamic per IPC-2223B guidance). Put copper on the neutral axis for dynamic bends (single layer, symmetric coverlay).

## 3. Layout rules in flex zones
- Traces perpendicular to the bend line; no vias, pads, or width changes in the bend zone; stagger traces on opposite layers (I-beam effect is bad).
- Curved traces, no sharp corners; teardrops on all pads/vias; anchoring spurs/"rabbit ears" on pads; coverlay openings slightly smaller than pads (pad captured) where possible.
- Planes in flex: cross-hatched (e.g. 45°, 50–70 % fill) for flexibility; account for its effect on impedance (hatched reference raises Z, field-solve).
- Keep components ≥ 1–2 mm (more for dynamic) from rigid-flex transition; transition zone gets no vias; use strain relief (bead of epoxy/adhesive) at transition.
- Stiffeners under connectors/components; ZIF connectors need specified thickness (often 0.3 mm total at the contact area) and stiffener.
- Controlled impedance on flex: thin dielectrics → narrow lines; hatched references; get the fab's flex stackup.
- Panel utilisation and cost: flex outlines nest poorly; simplify shape.
- FPC tails for JLCPCB-style flex: check gold finger thickness/stiffener and min bend options from the fab page.

## 4. Rigid-flex specifics
- Flex layers usually in the centre of the rigid stackup; adhesiveless PI; coverlay only in flex areas ("bikini" coverlay) to avoid acrylic adhesive in rigid section (Z-CTE problems).
- Plated holes through acrylic adhesive are a reliability risk — avoid in Class 3.
- Specify bend locations, bend direction, number of cycles, and installed shape on the drawing (provide a 3D/MCAD model).
