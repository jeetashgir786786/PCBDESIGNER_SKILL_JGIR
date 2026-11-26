# Usage

The skill picks its depth to match the request. A quick question gets a direct answer; a full design goes through every gate.

## Example prompts by task mode

| Mode | Prompt |
|---|---|
| Quick consult | "What's the difference between a blind and a buried via, and when do I pay for each?" |
| Calculation | "Trace width for 4 A, outer layer, 1 oz, 20 °C rise. Show the assumptions." |
| Stackup / impedance | "8-layer 1.6 mm stackup at JLCPCB for 90 Ω USB and 100 Ω Ethernet pairs." |
| High-layer / HDI | "Plan the layer count and via technology for a 0.5 mm-pitch 900-ball FPGA with DDR4." |
| Design review | "Review the attached schematic PDF for an STM32G4 motor controller. Findings first, ranked by severity." |
| Troubleshooting | "My ESP32 board browns out when Wi-Fi starts. Rank the hypotheses and give tests to tell them apart." |
| Manufacturing prep | "What do I need to send JLCPCB for a 4-layer PCBA order with bottom-side parts?" |
| Full design (KiCad) | "Design, route and give me fab files for a USB-C to 3.3 V UART board for JLCPCB PCBA." |

## What good output looks like
- **Labels** on every important number: `VERIFIED (source)`, `USER REQUIREMENT`, `ASSUMPTION`, `ENGINEERING DECISION` or `UNVERIFIED`.
- **Calculations** laid out as equation → inputs with units → result → margin.
- **Reviews** as a findings table: ID, severity, location, evidence, impact, fix, how to verify.
- **Generated CAD** comes with a verification status (`PRELIMINARY`, `REVIEWED`, `TOOL-CHECKED` or `RELEASE-CANDIDATE`) and the actual tool output.

## Writing a design spec for the toolkit
Start from [`spec_template.py`](../pcbdesigner-skill-jgir/scripts/kicad_auto/examples/spec_template.py). It documents every field. Follow these rules:
1. Map nets by **footprint pad number**, not datasheet pin name. Run `python3 libsym.py Lib:Symbol` to list the pins of a symbol.
2. Place connectors and mechanical parts first, then the main ICs, then decoupling next to their pins.
3. Run `build.py` and fix every `COURTYARD` line before routing.
4. Route sensitive nets (diff pairs, RF, power-stage hot loops) by hand and lock them. Then run `route.py --keep`.

Then run:
```bash
cd pcbdesigner-skill-jgir/scripts/kicad_auto
./pipeline.sh my_spec.py out/ 20 1
```

See [references/kicad-automation.md](../pcbdesigner-skill-jgir/references/kicad-automation.md) for each gate, the measured results and how to fix open nets.
