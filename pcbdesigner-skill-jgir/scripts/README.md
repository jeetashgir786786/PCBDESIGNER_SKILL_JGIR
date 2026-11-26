# Scripts

Transparent first-order calculators. They implement published closed-form approximations and print their own validity warnings. They are not field solvers, IPC-2152 implementations or simulators.

| Script | Purpose |
|---|---|
| `pcb_calc.py` | Impedance (IPC-2141 microstrip/stripline/differential), propagation delay & skew-to-length, critical length & knee frequency, via-stub resonance, IPC-2221 trace & via current, PDN target impedance, plane capacitance, IPC-2221B Table 6-1 spacing lookup, aspect ratio, rough insertion loss, BGA escape layer estimate, via thermal resistance |
| `ohms_law.py` | V/I/R/P from any two |
| `divider.py` | Unloaded divider |

Run `python3 pcb_calc.py <subcommand> --help`. Report the exact command and output when using a result, and label it as an estimate.

## `kicad_auto/` — automated KiCad build path (see `references/kicad-automation.md`)

| Script | Purpose |
|---|---|
| `check_env.py` | Lists missing dependencies and how to install them |
| `get_freerouting.sh` | Downloads the Freerouting jar from its official GitHub release (v1.9.0) |
| `build.py` | Design spec → schematic, symbol/footprint libs, placed PCB, stackup, net classes, fab rules, `design.json` |
| `route.py` | Freerouting autoroute + plane fan-out + grid A* finisher (rip-up, hole and clearance rules, best-round and best-attempt keeping) |
| `verify.py` | DRC + board↔design + schematic↔design parity (+ ERC on KiCad 8+) |
| `fab.py` | Gerbers X2, Excellon drills and maps, JLCPCB zip, BOM (JLCPCB + full with LCSC status), CPL, PDFs, STEP |
| `images2d.sh` / `images3d.sh` | Layer PNGs; KiCad 3D-viewer images (headless GUI capture on KiCad 7/8, `kicad-cli pcb render` on 9+) |
| `pipeline.sh` | Every step above in order; stops at the first failed gate |
| `drc.py` | DRC runner and report parser (`python3 drc.py board.kicad_pcb`) |
| Internals | `sch_gen.py`, `pcb_gen.py`, `libsym.py`, `fpgen.py`, `parts.py`, `fab_rules.py`, `kenv.py`, `fanout.py`, `astar_net.py`, `ses_import.py`, `ripup.py`, `dedupe.py`, `models3d.py` |
| 3D extras | `step2glb.py` and `board_glb.py` (STEP → GLB with copper overlay, for web viewers), `render.py` (offscreen GLB render) |
| Examples | `examples/spec_template.py` (every field documented), `examples/usb_uart_spec.py` (CH340C USB-UART bridge; `LAYERS=4` for the 4-layer variant) |

Tested on KiCad 7.0.11 + Freerouting 1.9.0 + Java 21 on Linux. Treat any other version as untested until the example passes `pipeline.sh`.
