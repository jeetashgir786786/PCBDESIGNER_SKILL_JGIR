# PCBDESIGNER_SKILL_JGIR (v3)

A cross-platform Agent Skill for PCB engineering, from 2-layer boards to 24–32+ layer HDI designs. It structures expert-level guidance and calculations; it does not guarantee that AI-generated designs are correct or fabrication-ready.

## What's new in v3: automated KiCad build path
- `scripts/kicad_auto/`: design spec → schematic + placed PCB → **Freerouting autoroute** + plane fan-out + A* finisher → DRC and netlist-parity gate → JLCPCB Gerbers/drills/BOM/CPL → real KiCad 2D and 3D images. One command runs it all: `pipeline.sh`.
- Hardened on real 2- and 4-layer designs. Regression-tested on a bundled USB-UART example (2- and 4-layer, both route to 0 unconnected / 0 DRC errors).
- `references/kicad-automation.md`: the workflow, gates, measured results, a troubleshooting order for open nets, and a table of pitfalls already handled.
- Tested on KiCad 7.0.11 + Freerouting 1.9.0. Other versions: run the example first.

## What was in v2
- Rewritten `SKILL.md` with a reference router, high-layer/HDI fast path, quick-number table and strict honesty rules.
- 24 reference files: glossary, stackups 2–32 layers, high-layer-count workflow, HDI/microvias, materials & finishes, SI, interface cheat sheet (USB, PCIe 3–7, DDR4/5, Ethernet, HDMI, MIPI, SerDes), PI, power electronics, EMC, RF, high-voltage/creepage, analog, MCU, thermal/mechanical, flex/rigid-flex, DFA/DFT, DFM & outputs, fab capability snapshots (dated Nov 2026), standards map, KiCad 9/10, calculations, review/troubleshooting checklists.
- `scripts/pcb_calc.py`: impedance, delay/skew, critical length, stub resonance, trace/via current, Ztarget, plane capacitance, IPC-2221B spacing, aspect ratio, loss estimate, BGA escape layers, via thermal resistance.
- `templates/stackup-spec.md` plus the original requirement/review/handoff templates.
- 18 evaluation cases including 24-layer, HDI, PCIe Gen5, DDR5, PDN and safety-spacing tests.

## Install / use
- Claude (claude.ai / desktop): Settings → Capabilities/Skills → upload this ZIP (replace the older version). Claude Code: place the folder in `~/.claude/skills/` or the project's `.claude/skills/`.
- Other agents (GPT/Codex etc.): use `SKILL.md` as instructions and the `references/` files as knowledge files.

## Maintenance
Fab capabilities, KiCad versions and standard revisions are dated in the files — refresh them every few months. Interface and vendor numbers must be checked against the current spec/vendor guide for each design.
