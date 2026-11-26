# KiCad automation toolkit (`scripts/kicad_auto/`)

End-to-end, scriptable path from a Python design spec to a routed, verified, JLCPCB-ready KiCad project with
2D and 3D images. It was hardened on real 2- and 4-layer MCU boards and is regression-tested on the bundled
`examples/usb_uart_spec.py`.

**Tested on KiCad 7.0.11 (Linux) with Freerouting 1.9.0.** It uses the SWIG `pcbnew` API, which is still
present in KiCad 8 and 9 but deprecated (KiCad 9 adds the IPC API). On another version, run the example
first and fix any API breakage before you use the toolkit on a real board. Never report a gate as passed
unless you ran it on that version and read its output.

## 1. When to use it
- **FULL DESIGN / CAD-AUTOMATION modes** when the user wants actual KiCad files, not just guidance.
- Boards up to roughly 150 parts and 2–6 layers, through-hole vias only (no HDI or microvias in the router).
- Do not use the autorouter alone for controlled-impedance pairs (USB/Ethernet/PCIe), RF feeds, switching-regulator
  hot loops or high-current paths. Either route those yourself in the spec stage, or route by hand in KiCad and
  run `route.py --keep` (locked copper is preserved). Then review them by eye.

## 2. Setup
```
python3 scripts/kicad_auto/check_env.py        # shows what is missing and how to install it
bash scripts/kicad_auto/get_freerouting.sh     # official GitHub release jar (v1.9.0), Java 17+
```
Run the scripts with the Python that can `import pcbnew`:
- Linux: the system `python3`.
- Windows: the KiCad Command Prompt.
- macOS: the Python bundled inside KiCad.app.

## 3. Workflow (one gate per step)
| Step | Command | Gate to pass before going on |
|---|---|---|
| Spec | copy `examples/spec_template.py` | pin numbers checked against the footprint (`python3 libsym.py Lib:Sym` lists them) |
| Build | `build.py spec.py out/` | no `COURTYARD` lines; placement DRC has only unconnected items and cosmetic warnings |
| Route | `route.py out/NAME.kicad_pcb --passes 20 [--attempts 3]` | `unconnected=0 errors=0` |
| Verify | `verify.py out/ NAME` | `RESULT PASS`: DRC, board↔design parity and schematic↔design parity |
| Fab | `fab.py out/ NAME` | Gerbers + drills zip, BOM/CPL; every UNVERIFIED LCSC line gets checked |
| Images | `images2d.sh` / `images3d.sh` | open and look at them; a hovered part shows highlighted |
| All of it | `pipeline.sh spec.py out/ 20 3` | stops at the first failed gate |

`design.json` (written by `build.py`) is the netlist of record. The parity checks compare the schematic
and the board against it. Change the spec and rebuild; don't hand-edit nets in the generated files.

## 4. What `route.py` does
1. Removes outer-layer pours and saves them to a JSON file, because Freerouting treats a pour as an obstacle.
2. Fans out inner planes: a locked stub and via from each SMD pad of every net that owns an inner-layer zone.
   Freerouting does not connect pads to zones.
3. Exports Specctra DSN, runs `java -jar freerouting.jar -de x.dsn -do x.ses -mp N`, then imports the SES with
   its own importer, because KiCad 7's Python ImportSpecctraSES has no board argument.
4. Finish rounds. Each round runs DRC, takes the unconnected nets plus the nets involved in clearance or short
   errors, and reroutes them with a grid A* router that keeps clearance, hole-to-hole and edge rules:
   - Round 1: plain A* reroute.
   - Round 2 and later: rip up and reroute on a finer grid.
   - Round 3 and later: also rip up the neighbouring nets around the open pads.
   - The best round is kept, since later rounds can make things worse.
5. With `--attempts N`, repeats steps 3–4 from the same starting board N times and keeps the best result.
   Each attempt adds 7 to the Freerouting pass budget, because identical input gives an identical result.
6. Restores the pours, refills, and writes `docs/NAME_DRC_routed.rpt`.

Every pcbnew step runs in a fresh subprocess. After `board.Remove()` the SWIG type registry is corrupted
for the rest of that process.

**Measured results** (this toolkit, KiCad 7.0.11, Freerouting 1.9.0, one CPU thread, Nov 2026):

| Board | Result | Time |
|---|---|---|
| `usb_uart_spec.py`, 2-layer, 12 parts | 0 unconnected, 0 DRC errors, verify PASS | ~40 s routing; ~3 min for `pipeline.sh` incl. images |
| same, 4-layer (GND + 3V3 planes) | 0 unconnected, 0 DRC errors, verify PASS | ~35 s |
| Dense MCU board, re-routed from scratch unattended (30×30 mm, 4-layer, ~70 parts, 0.5 mm-pitch LGA sensor) | **1 open connection** (an SPI line at the LGA), **0 DRC errors** | ~4 min per attempt |

On the dense board, more attempts or rounds did not improve on round 2. Freerouting gives the same result for
the same board, so diversity has to come from placement. Its hand-finished version needed placement changes
(decoupling caps moved, one SPI pin swapped) plus two micro-fixes (a via nudge and a 0.14 mm neck-down).

The last one or two connections on dense boards are usually a **placement** problem, not a router problem.

## 5. When connections stay open
Work through these in order, rebuilding and rerouting after each change:
1. Look at the open pads in the report. Find what blocks the escape: a part too close, a via fence, a keepout.
2. **Move parts.** Give 0.5–1 mm more room around fine-pitch parts and pull decoupling caps off the escape side.
3. **Swap pins.** On an MCU with a GPIO matrix (ESP32), move the signal to a free pin that faces its
   destination. Update the spec and firmware notes together.
4. Make the default via smaller where the fab allows it (`fab_rules.py`), or add a layer.
5. As a last resort, route the net by hand in KiCad, lock it, and run `route.py --keep`.
Never accept a board with open connections because "the pour will connect it". Re-run DRC with the pours filled.

## 6. Pitfalls this toolkit already handles (keep them if you edit it)
| Symptom | Cause | Fix in code |
|---|---|---|
| Segfault when placing bottom parts | `Flip()` called before `board.Add()` | add, then flip, then rotate (`pcb_gen.place_parts`) |
| Net classes lost | `SaveBoard` rewrites `.kicad_pro` | write the project after saving (`build.py`) |
| Stackup missing in the fab output | `BOARD_STACKUP` not usable from SWIG | inject a text `(stackup …)` block (`add_stackup`) |
| Pads not connected to inner planes | Freerouting ignores zones | `fanout.py` before routing |
| Random crashes after removing items | SWIG registry corrupted | one subprocess per step |
| JSON parse errors from subprocess output | SWIG prints "memory leak" lines to stdout | filter `swig/python` lines |
| A* tracks 0.02 mm under clearance | raster rounding plus staircase paths | one grid-cell margin, string-pulling, conservative line check |
| Stacked same-net vias / hole_near_hole | A* layer flip-flop | hole-to-hole map on via sites, reject paths with close own vias |
| Tracks too close to NPTH | copper clearance used instead of hole clearance | NPTH uses max(clearance, hole_clearance) |
| A pad looks connected but DRC disagrees | raster sliver overlap | a pad counts as connected only with ≥4 overlapping cells |
| Thermal-via pads under a module short to bottom parts | footprint PTH sub-pads | `strip_vias=True` on that part |
| 2-layer JLCPCB rejects 0.2 mm vias | 2-layer minimum is 0.3 mm drill / 0.5 mm via (Nov 2026 snapshot) | `fab_rules.DEFAULT_VIA[2] = (0.6, 0.3)` |
| 3D image shows a highlighted part | mouse hover in the 3D viewer | park the cursor before capture (`images3d.sh`) |
| USB-C D+/D− need to cross between A and B pads | the A6/B6 and A7/B7 pairs are interleaved | A* finds a via-free bridge behind the pads; check it by eye |

## 7. What is still not automatic (say so in the handoff)
- **ERC:** `kicad-cli sch erc` exists only from KiCad 8. On KiCad 7, ERC must be run in the GUI.
  The generator adds no-connect flags, but power-flag warnings need `FLAG()` parts.
- **Schematic layout:** the generator places parts in grouped columns with net labels. It is correct and readable,
  but not hand-drawn. Expect to tidy it if the schematic is a deliverable.
- **Impedance-controlled routing, length matching and differential pairs** are not handled by the autorouter.
- **LCSC part numbers** from `parts.py` were written from memory and are flagged UNVERIFIED until checked.
- **CPL rotations** need JLCPCB's placement preview; some footprints are offset by 90° or 180°.
- **Placeholder 3D boxes** (`box_models`) are fit-check bodies only, not vendor models.
- **images3d.sh on KiCad 7/8:** the GUI click coordinates were measured on KiCad 7.0.11 at 1920×1200.
  On KiCad 9+ the script uses `kicad-cli pcb render`; that path is written from the CLI documentation
  and was not run in testing.
