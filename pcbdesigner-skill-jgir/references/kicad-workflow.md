# KiCad workflow (KiCad 9/10)

Current stable line as of Nov 2026: KiCad 10.0.x (10.0.0 released Mar 2026; bug-fix releases through 10.0.8 in Oct 2026). KiCad 10 added design variants, graphical DRC rule editor, revamped length/skew tuning, schematic hop-overs, pin/gate swap with back-annotation, STEP-only 3D library. Always run `kicad-cli version` and `--help` for the installed version; CLI options change between releases.

## 1. Project integrity
- Keep the project folder intact (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `.kicad_dru`, `fp-lib-table`, `sym-lib-table`, project libraries). Make a timestamped backup / git commit before automated edits.
- Prefer project-local libraries for released designs (embed or copy symbols/footprints/3D models) so the design rebuilds anywhere.
- Edit files with the official CLI, the IPC API (kicad-python, introduced in KiCad 9; SWIG `pcbnew` Python bindings are deprecated) or a proper S-expression parser — never regex-edit structured files.
- Never claim a file opens, passes ERC/DRC or matches the schematic unless you ran the tool and read the report.

## 2. Setup sequence for a new board
1. **Board Setup → Physical Stackup**: copper layer count, thicknesses, materials, Dk/Df, finish, mask — enter the fab's stackup. Enable impedance-controlled flag.
2. **Board Setup → Design Rules → Constraints**: min track, clearance, via (diameter, hole), microvia, hole-to-hole, copper-to-edge, annular ring — from the fab sheet. Enable blind/buried & microvias if HDI.
3. **Net classes**: width, clearance, via size, diff-pair width/gap per class (Power, HV, USB_90, PCIE_85, DDR_DQ, RF_50…). Assign by pattern (e.g. `/USB_*`).
4. **Custom rules** (`.kicad_dru` or KiCad 10 graphical editor) for layer-specific impedance widths, BGA neck-down, HV creepage, length/skew groups.
5. **Pre-defined sizes** for tracks/vias/diff pairs matching the solver output per layer.
6. Import board outline/mounting/keepouts from MCAD (DXF/STEP) on Edge.Cuts / User layers.

## 3. Custom rule examples (verify syntax against your version's rule help)
```
(version 1)
(rule "HV_clearance"
  (condition "A.hasNetclass('HV') && !B.hasNetclass('HV')")
  (constraint clearance (min 2.5mm)))
(rule "HV_creepage"            # creepage constraint available in KiCad 9+
  (condition "A.hasNetclass('HV') && !B.hasNetclass('HV')")
  (constraint creepage (min 4.0mm)))
(rule "USB_pair"
  (condition "A.inDiffPair('/USB_D*')")
  (constraint diff_pair_gap (opt 0.15mm))
  (constraint diff_pair_uncoupled (max 2mm)))
(rule "PCIe_L3_width"
  (layer "In3.Cu")
  (condition "A.hasNetclass('PCIE_85')")
  (constraint track_width (opt 0.11mm)))
(rule "BGA_neckdown"
  (condition "A.intersectsCourtyard('U1')")
  (constraint track_width (min 0.09mm)))
(rule "DDR_byte0_skew"
  (condition "A.hasNetclass('DDR_B0')")
  (constraint skew (max 0.25mm)))
(rule "microvia_size"
  (condition "A.Via_Type == 'Micro'")
  (constraint hole_size (min 0.1mm)) (constraint via_diameter (min 0.25mm)))
(rule "no_vias_in_antenna"
  (condition "A.Type == 'Via' && A.intersectsArea('ANT_KEEPOUT')")
  (constraint disallow via))
```

## 4. High-layer-count & HDI in KiCad
- KiCad supports many copper layers (up to 32 in current versions — check), through, blind/buried and micro vias. Define layer pairs for blind/buried vias in the via tool; microvias span adjacent layers only.
- Back-drill / controlled-depth drill: if the installed version has no native back-drill definition, document back-drill in the fab drawing and IPC-2581/ODB++ export notes, and generate/verify separate drill instructions with the fab. Confirm in the version's release notes before claiming support.
- Length/skew tuning: use the tuning tools (KiCad 10 revamped) with time-domain targets if available; enter propagation delay per layer where supported.
- Use teardrops (Board Setup → Teardrops) for small annular rings and flex.
- Zones: set priorities deliberately, thermal relief vs solid per zone/pad, minimum width, remove islands policy; refill (`B`) and re-run DRC before export.

## 5. CLI (discover exact flags with `kicad-cli <group> <cmd> --help`)
```
kicad-cli version
kicad-cli sch erc  --severity-all --format json -o erc.json  project.kicad_sch
kicad-cli pcb drc  --schematic-parity --severity-all --format json -o drc.json  project.kicad_pcb
kicad-cli sch export netlist / bom / pdf / python-bom
kicad-cli pcb export gerbers --board-plot-params -o fab/  project.kicad_pcb   # use the board's saved plot settings
kicad-cli pcb export drill   -o fab/  --format excellon --excellon-separate-th --generate-map  project.kicad_pcb
kicad-cli pcb export pos     --format csv --units mm --side both -o fab/cpl.csv  project.kicad_pcb
kicad-cli pcb export ipc2581 -o fab/board.xml  project.kicad_pcb
kicad-cli pcb export odb     -o fab/  project.kicad_pcb            # KiCad 9+
kicad-cli pcb export ipcd356 -o fab/board.ipc  project.kicad_pcb
kicad-cli pcb export step    -o mech/board.step  project.kicad_pcb
kicad-cli jobset run ...                                            # KiCad 9+ job sets for repeatable outputs
```
Add `--exit-code-violations` where available to make CI fail on violations. Record command, version and summary counts in the verification report.

## 6. Review & output practice
- ERC: resolve or justify each warning (power flags, unconnected pins with no-connect flags, pin type conflicts).
- DRC with schematic parity: zero unrouted, zero errors; list every exclusion with reason.
- Visual: 3D viewer for placement/collisions/polarity; net inspector for unrouted; board statistics.
- Export, then load Gerbers/drills in GerbView and compare layer-by-layer; check drill/outline alignment, mask/paste, silkscreen clipping.
- For JLCPCB assembly: BOM with LCSC part numbers field, CPL rotation check in their viewer.
