# PCB Glossary (A–Z by domain)

Use this file when a user asks "what is X", when writing documentation for a client, or to make sure terms are used precisely in reviews. Definitions are concise; deeper treatment lives in the linked reference file.

## 1. Board structure & layers
- **Substrate / base material** – The insulating laminate the copper sits on. Usually epoxy-glass (FR-4) but also polyimide, PTFE, hydrocarbon-ceramic, BT, aluminium/copper metal core. → materials-laminates.md
- **FR-4** – Flame-retardant (UL94 V-0) woven E-glass + epoxy laminate. "FR-4" is a grade name, not one material: Tg 130–180 °C, Dk 3.8–4.8, Df 0.008–0.025 depending on resin and glass.
- **Core** – A fully cured laminate with copper foil on one or both sides, bought from the laminate vendor (e.g. 0.1 mm, 0.2 mm, 0.36 mm, 0.71 mm, 1.2 mm cores).
- **Prepreg (PP)** – Glass cloth pre-impregnated with partly cured (B-stage) resin; bonds cores together during lamination and fills between copper features. Named by glass style (106, 1080, 2116, 3313, 7628…) and resin content (RC%).
- **Copper foil** – ED (electro-deposited) or RA (rolled-annealed). Weights: ⅓ oz (12 µm), ½ oz (17–18 µm), 1 oz (35 µm), 2 oz (70 µm). Profiles: STD, RTF, VLP, HVLP (smoothest = lowest loss).
- **Layer / copper layer** – A plane of copper features. Named L1 (top) … Ln (bottom). Signal, plane, mixed.
- **Trace / track** – A copper conductor carrying a signal or current.
- **Plane** – A (mostly) solid copper layer at one potential (GND or a power rail) providing return paths, low PDN inductance and shielding.
- **Split plane** – A plane divided into several islands for different rails. Never route high-speed signals across a split.
- **Copper pour / fill / zone** – A copper area poured around features on a signal layer, usually tied to GND.
- **Stackup** – The ordered list of copper and dielectric layers with thicknesses, materials, copper weights and impedance targets. → stackup-design.md
- **Symmetry / balance** – Mirror-image stackup about the centre line (copper weights, dielectric thickness, copper density) to prevent bow & twist.
- **Copper balance / thieving** – Adding non-functional copper (dots/hatch) to equalise copper density per layer for plating and lamination uniformity.
- **Solder mask (solder resist)** – Polymer coating (LPI) protecting copper and preventing solder bridges. Has its own Dk (~3.3–4.0) which lowers outer-layer impedance by ~1–3 Ω.
- **Solder mask defined (SMD) / non-solder-mask-defined (NSMD) pad** – Mask opening smaller than copper (SMD) or larger (NSMD). NSMD is the default for BGAs ≥0.5 mm pitch.
- **Mask expansion / swell** – Clearance between pad copper and mask opening (typ. 0.05 mm / 2 mil per side).
- **Mask web / dam / sliver** – Strip of mask between two openings. Typical minimum 0.1 mm (green), larger for black/white.
- **Silkscreen / legend** – Printed text and outlines (refdes, polarity, pin 1, logos).
- **Peelable mask** – Temporary mask protecting areas (gold fingers, test pads) during wave solder.
- **Carbon ink** – Printed conductive carbon for keypad contacts/jumpers.
- **Coverlay** – Polyimide + adhesive film used instead of solder mask on flex circuits.
- **Stiffener** – FR-4, polyimide or stainless plate bonded to a flex area to support connectors/components.

## 2. Holes, vias & connections
- **Pad / land** – Exposed copper for soldering a component terminal.
- **PTH (plated through-hole)** – Drilled hole plated with copper through all layers (component or via).
- **NPTH** – Non-plated hole (mounting, tooling, alignment).
- **Via** – Plated hole whose only job is a layer-to-layer connection.
- **Through via** – Goes L1 to Ln.
- **Blind via** – From an outer layer to an inner layer, not through the board.
- **Buried via** – Connects inner layers only; invisible from outside.
- **Microvia** – Laser-drilled blind structure with aspect ratio ≤1:1 (IPC-T-50 definition), typically 75–150 µm diameter spanning one dielectric (≤~0.25 mm total depth). → hdi-microvias.md
- **Stacked microvias** – Microvias directly on top of each other (copper-filled). Space-efficient but the reliability-critical structure in IPC-6012F.
- **Staggered microvias** – Offset microvias connected by a short trace/pad. Generally more reliable than stacked.
- **Skip via** – Laser via spanning two dielectrics (L1→L3) without a pad on L2.
- **Via-in-pad (VIP / VIPPO / POFV)** – Via placed in an SMT pad, resin- or copper-filled and plated over (planarised) so solder isn't wicked away.
- **Annular ring** – Copper ring around a drilled hole = (pad Ø − drill Ø)/2. Class 2 allows 90° breakout on external layers; Class 3 needs ≥50 µm external.
- **Breakout / tangency** – When the drilled hole touches or exits the pad edge due to registration error.
- **Teardrop** – Fillet between track and pad/via to resist breakout and cracking.
- **Anti-pad (clearance)** – Opening in a plane around a via/hole it does not connect to.
- **Non-functional pad (NFP)** – Pad on an inner layer where the via has no connection. Often removed to improve SI and drilling; sometimes kept for reliability.
- **Thermal relief** – Spoked connection between a pad and a plane to limit heat sinking during soldering.
- **Direct connect / solid connect** – Pad fully merged into the plane (for current/thermal; harder to hand solder).
- **Aspect ratio (AR)** – Board (or span) thickness ÷ finished drill diameter. Mainstream ≤10:1, advanced 12–16:1, backplane fabs 20–30:1.
- **Back-drill (controlled-depth drill, CDD)** – Second, larger drill from the back removing the unused via stub. Leaves a residual stub (typ. 4–10 mil).
- **Via stub** – Unused portion of a via beyond the layer where the signal exits; resonates at f ≈ c/(4·L·√Dk_eff).
- **Via fence / stitching** – Rows of GND vias tying planes together, shielding RF lines or board edges.
- **Castellated holes (half-holes)** – Plated holes cut through at the board edge for module soldering.
- **Press-fit hole** – Tightly toleranced PTH for solderless compliant-pin connectors.
- **Tented / plugged / filled / capped via** – Via protection types per IPC-4761 (Type I–VII). → manufacturing.md
- **Slot** – Routed elongated hole (plated or not).
- **Countersink / counterbore** – Conical / flat-bottomed recess for screw heads.
- **Cavity board** – Recessed area in a multilayer to sink components.

## 3. Layout, rules & data
- **Schematic** – Logical circuit diagram.
- **Netlist** – List of nets and connected pins exchanged between schematic and layout.
- **Net / net class** – A connected group of pins; classes group nets sharing rules (width, clearance, via, impedance).
- **Footprint / land pattern** – The pad geometry and courtyard for a package (IPC-7351B / IPC-7352 naming).
- **Courtyard** – Keepout boundary around a part for placement spacing.
- **Fiducial** – Copper target (1 mm dot, 2–3 mm mask opening) for pick-and-place vision. Board level (3) and local (fine-pitch).
- **Keepout / rule area** – Region where copper, vias, tracks or parts are forbidden.
- **Clearance** – Shortest distance through air between conductors (electrical clearance).
- **Creepage** – Shortest distance along an insulating surface between conductors. → high-voltage-safety.md
- **Trace width / space (L/S)** – Narrowest manufacturable line and gap, e.g. 3/3 mil, 4/4 mil.
- **DRC** – Design Rule Check: geometry vs. rules.
- **ERC** – Electrical Rule Check: schematic connectivity/pin types.
- **DFM / DFA / DFT** – Design for Manufacturing / Assembly / Test.
- **BOM** – Bill of Materials.
- **CPL / PnP / centroid / XY file** – Component placement positions and rotations.
- **Gerber (RS-274X / X2)** – Layer image format; X2 adds attributes (layer function, net, pad type). Gerber X3 adds component info.
- **Excellon / NC drill** – Drill hit file (separate PTH/NPTH; separate files per span for blind/buried/back-drill).
- **ODB++ / IPC-2581** – Single-file intelligent manufacturing data (stackup, netlist, BOM, drill spans). Preferred for 8+ layers, HDI and back-drill.
- **IPC-D-356 netlist** – Netlist used by the fab for bare-board electrical test.
- **Fab drawing** – Drawing with outline, dimensions, stackup, drill table, notes (class, material, finish, impedance).
- **Assembly drawing** – Placement, polarity, special instructions.
- **Panel / array** – Multiple boards in a production panel with rails, fiducials, tooling holes; separated by V-score or tab-routing (mouse bites).
- **Gerber origin / aux origin** – Reference point for outputs.

## 4. Signal integrity
- **Transmission line** – An interconnect whose length is significant relative to the signal rise time (≳ 1/6 of the rise-time length).
- **Characteristic impedance (Z0)** – V/I ratio of a wave on a uniform line; set by width, dielectric height, Dk, copper thickness.
- **Microstrip** – Trace on an outer layer over one reference plane. **Embedded microstrip** – under mask/prepreg.
- **Stripline** – Trace between two planes (symmetric or asymmetric/offset).
- **Coplanar waveguide (CPWG / GCPW)** – Trace with coplanar ground on both sides plus a ground plane below; common for RF.
- **Differential pair** – Two complementary traces; differential impedance Zdiff, odd/even mode, common mode.
- **Intra-pair skew / inter-pair skew** – Timing difference within a pair / between pairs.
- **Propagation delay (tpd)** – ≈ 85 ps/in × √Dk_eff (≈ 170–180 ps/in stripline in FR-4).
- **Rise time (tr) / knee frequency** – f_knee ≈ 0.35/tr (10–90 %) or 0.5/tr; sets the bandwidth that matters.
- **Nyquist frequency** – Baud rate / 2 (e.g. PCIe Gen5 32 GT/s NRZ → 16 GHz; Gen6 64 GT/s PAM4 → 16 GHz).
- **NRZ / PAM4** – 2-level / 4-level signalling (PAM4 has ~9.5 dB less SNR per eye).
- **Insertion loss (IL, SDD21)** – Signal attenuation through a channel (dB), from dielectric (Df), conductor (skin effect + roughness) and radiation.
- **Return loss (RL, SDD11)** – Reflected energy due to impedance discontinuities.
- **Crosstalk (NEXT/FEXT)** – Coupling between nets; near-end and far-end.
- **Skin effect / skin depth** – Current crowding at the conductor surface; δ ≈ 2.1 µm at 1 GHz in copper, ∝ 1/√f.
- **Surface roughness** – Copper tooth profile (Rz); increases loss once δ ≲ roughness.
- **Fiber-weave effect / glass-weave skew** – Local Dk variation between glass bundles and resin causing skew in diff pairs.
- **Reflection / ringing / overshoot** – Effects of impedance mismatch.
- **Termination** – Series, parallel, Thevenin, AC, on-die (ODT) termination to control reflections.
- **Return path** – The path the return current takes, directly under the signal at high frequency.
- **Reference plane change** – When a signal changes layer and therefore reference; needs a nearby stitching via (same net) or stitching cap (different nets).
- **Eye diagram, jitter, BER, COM** – Link-level metrics; COM (Channel Operating Margin) is used by IEEE 802.3 and PCIe.
- **S-parameters (Touchstone .sNp)** – Frequency-domain channel models.
- **IBIS / IBIS-AMI** – Behavioural I/O and SerDes equaliser models for simulation.
- **CTLE / FFE / DFE** – Continuous-time linear / feed-forward / decision-feedback equalisers.
- **Length tuning / serpentine / trombone** – Adding length to match delay.
- **Fly-by topology** – DDR3/4/5 CA/CLK routed in a daisy chain past each DRAM with end termination; write-levelling compensates.
- **T-topology / clamshell** – Branching memory topology / DRAMs on both sides.

## 5. Power integrity
- **PDN (Power Delivery Network)** – VRM → bulk caps → planes → MLCCs → package → die.
- **Target impedance (Ztarget)** – ΔV_allowed / ΔI_transient; the PDN impedance must stay below it across the relevant band.
- **Decoupling / bypass capacitor** – Local charge reservoir; effectiveness limited by mounting inductance.
- **ESR / ESL / SRF** – Equivalent series resistance / inductance / self-resonant frequency.
- **Anti-resonance** – Parallel resonance peak between capacitors of different values or caps and plane capacitance.
- **Plane capacitance** – C = ε0·εr·A/d; ≈ 300–450 pF/in² (≈ 45–70 pF/cm²) for a 2–3 mil FR-4 dielectric (Dk ≈ 4). "Embedded capacitance" materials use ≤1 mil high-Dk cores.
- **IR drop / DC drop** – Static voltage drop through planes, vias and connectors.
- **Remote sense / Kelvin sense** – Separate sense lines to regulate at the load.
- **VRM** – Voltage regulator module.
- **Ground bounce / SSN** – Noise from simultaneous switching through shared inductance.

## 6. EMC
- **EMI / EMC / ESD / EFT / surge** – Emissions, compatibility, discharge, fast transients, surges (IEC 61000-4-2/-4/-5).
- **Common-mode current** – Current flowing in the same direction on all conductors of a cable; the main radiated-emission source.
- **Stitching capacitor** – Capacitor bridging two reference planes to give return current a path.
- **Chassis / earth / signal ground** – Distinct grounding concepts; connect deliberately.
- **Faraday cage / shield can / gasket** – Metallic enclosures/shields.
- **Ferrite bead** – Lossy inductor for HF filtering (watch DC-bias saturation).
- **TVS / ESD diode** – Transient voltage suppressor.
- **Guard ring / guard trace** – Driven or grounded copper surrounding sensitive nodes.

## 7. Thermal & mechanical
- **Tg (glass transition)** – Temperature above which the resin softens and Z-CTE rises sharply.
- **Td (decomposition)** – 5 % weight-loss temperature. Lead-free assembly needs Td ≳ 325–340 °C.
- **T260 / T288** – Time to delamination at 260/288 °C.
- **CTE (x/y/z)** – Coefficient of thermal expansion; Z-axis CTE above Tg drives barrel cracks.
- **θJA / θJC / ΨJT** – Thermal resistances/characterisation parameters.
- **Thermal via** – Via array conducting heat from a pad to inner planes or the other side.
- **Copper coin / inlay** – Solid copper slug pressed into the board for extreme heat flux.
- **Heavy copper** – ≥3 oz finished copper.
- **Bow & twist** – Warp; IPC limit 0.75 % for SMT boards.
- **CAF (conductive anodic filament)** – Copper filament growth along glass fibres between biased holes; mitigated by CAF-resistant resin, hole-wall spacing.
- **Delamination / measling / crazing** – Lamination/resin-glass separation defects.
- **Pad cratering** – Resin fracture under a BGA pad.

## 8. Fabrication & assembly
- **Sequential lamination** – Building the stackup in several press cycles to create blind/buried/microvias.
- **Etch factor / trapezoidal trace** – Etched trace is narrower at top than bottom.
- **Registration** – Layer-to-layer alignment accuracy (±2–3 mil typical).
- **Plating (panel/pattern)** – Copper electroplating; via barrel min 20 µm avg (Class 2), 25 µm (Class 3).
- **Surface finish** – HASL, LF-HASL, ENIG, ENEPIG, ImAg, ImSn, OSP, hard gold, EPIG.
- **Black pad** – ENIG nickel corrosion defect causing brittle joints.
- **Electrical test (flying probe / bed-of-nails)** – Bare-board open/short test against IPC-D-356.
- **Microsection / cross-section** – Destructive inspection of plating and layers.
- **IST / thermal shock coupons** – Reliability test coupons (IPC-TM-650 2.6.26 IST).
- **Impedance coupon (TDR coupon)** – Test lines in the panel rail measured by TDR.
- **Stencil / aperture / area ratio** – Solder paste printing; area ratio ≥0.66 for good release.
- **Reflow profile / TAL / peak** – Time above liquidus, peak temperature (SAC305 peak ~240–250 °C).
- **Voiding** – Gas voids in solder joints (thermal pads, BGAs); X-ray inspected.
- **Tombstoning** – Passive standing up due to unbalanced wetting.
- **Head-in-pillow** – BGA ball not coalescing with paste due to warpage.
- **Conformal coating** – Protective polymer (acrylic, silicone, urethane, parylene).
- **Underfill** – Epoxy under BGAs/CSPs for mechanical reliability.
- **Class 1 / 2 / 3** – IPC product classes: general / dedicated service / high-reliability.
