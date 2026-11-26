# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [3.0.0] - 2026-11-26
### Added
- `scripts/kicad_auto/`: an automated KiCad build path that goes from design spec → schematic + placed PCB → Freerouting autoroute + plane fan-out + grid A* finisher → DRC and netlist parity → JLCPCB Gerbers/drills/BOM/CPL/STEP → KiCad 2D and 3D images (`pipeline.sh`).
- A* finisher features:
  - exact clearance check using KiCad's own hit-testing
  - hole-to-hole and NPTH hole-clearance rules
  - string-pulled paths
  - neighbour rip-up
  - best-round and best-attempt keeping
- `references/kicad-automation.md`, covering the workflow, gates, measured results, open-net troubleshooting and the pitfalls already handled.
- Example spec (`usb_uart_spec.py`, 2- and 4-layer) and an annotated spec template.
- Fab rule presets for JLCPCB and PCBWay (planning snapshot, Nov 2026).
- Eval cases 19–22, covering end-to-end builds, open-net honesty, pad-number mapping and 2-layer via rules.
- Repository tooling:
  - pytest suite
  - ruff lint
  - CI and release workflows
  - packaging script
  - issue and PR templates
  - citation file
### Changed
- Skill renamed to **PCBDESIGNER_SKILL_JGIR**; its skill id is `pcbdesigner-skill-jgir`.

## [2.0.0] - 2026-11
### Added
- Rewritten `SKILL.md`:
  - reference router
  - high-layer/HDI fast path
  - quick-number table
  - honesty rules
- 24 reference files (stackups 2–32 layers, HDI, materials, SI/PI, interfaces, EMC, RF, HV safety, flex, DFM, fab snapshots, standards map, KiCad).
- `pcb_calc.py` with 16 calculators.
- Stackup specification template.
- 18 evaluation cases.

## [1.0.0] - 2026-11
### Added
- First version: design process, requirement/review/handoff templates, basic calculators.

[Unreleased]: https://github.com/jeetashgir786786/PCBDESIGNER_SKILL_JGIR/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/jeetashgir786786/PCBDESIGNER_SKILL_JGIR/releases/tag/v3.0.0
