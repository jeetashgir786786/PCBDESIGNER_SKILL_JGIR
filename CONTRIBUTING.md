# Contributing

Thanks for helping make PCBDESIGNER_SKILL_JGIR better. This project ships engineering guidance that people may build hardware from, so changes need evidence.

## Ground rules
- **Sources for numbers.** Any new numeric claim in `references/` must cite where it came from: a datasheet, standard, vendor guide or fab page. Capability numbers must also carry a date, e.g. "JLCPCB, checked 2026-11".
- **No invented verification.** Don't claim a tool result, simulation or test you did not run. Use the skill's labels: `VERIFIED (source)`, `ASSUMPTION`, `UNVERIFIED`.
- **Keep `SKILL.md` lean.** Detail belongs in `references/`. `SKILL.md` routes to it.

## Development setup
```bash
git clone https://github.com/jeetashgir786786/PCBDESIGNER_SKILL_JGIR.git
cd PCBDESIGNER_SKILL_JGIR
python3 -m pip install -r requirements-dev.txt
make check          # lint + tests + package validation (no KiCad needed)
```

To work on `scripts/kicad_auto/` you also need KiCad 7+ with the `pcbnew` Python module, Java 17+ and Freerouting. Run `python3 pcbdesigner-skill-jgir/scripts/kicad_auto/check_env.py` to see what's missing.

## Changes to the KiCad toolkit
Before opening a PR, run the example end to end and paste the summary lines into the PR:
```bash
make example        # pipeline.sh on examples/usb_uart_spec.py (2-layer)
LAYERS=4 make example
```
Both must end with `RESULT PASS` and `unconnected=0 errors=0`. State your KiCad, Freerouting and Java versions.

## Pull requests
1. Fork, then create a branch: `feat/<topic>`, `fix/<topic>` or `docs/<topic>`.
2. Keep each PR to one topic. Update `CHANGELOG.md` under **Unreleased**.
3. `make check` must pass. CI runs it on every push.
4. Fill in the PR template, including the verification section.

## Reporting issues
Use the issue templates. For a wrong engineering claim, quote the file and line, and give the correct value with its source.

## Code style
- Python 3.10+, linted with `ruff` (config in `pyproject.toml`).
- One pcbnew operation per subprocess where items are removed (see `references/kicad-automation.md` §6).
- Scripts take paths as arguments. No hard-coded user paths.

By contributing you agree that your contributions are licensed under the MIT License and that you follow the [Code of Conduct](CODE_OF_CONDUCT.md).
