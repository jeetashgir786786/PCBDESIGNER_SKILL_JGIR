# Installation

## 1. Claude apps (claude.ai, desktop, mobile)
1. Download `pcbdesigner-skill-jgir-vX.Y.Z.zip` from the [latest release](https://github.com/jeetashgir786786/PCBDESIGNER_SKILL_JGIR/releases/latest).
   Or build it yourself with `make package`, which writes the zip to `dist/`.
2. Open **Settings → Capabilities**, make sure Skills are enabled, then upload the ZIP under **Skills**.
3. Start a new chat and ask a PCB question. Claude loads the skill when its description matches the task.

> Upgrading from an older version: delete the old skill first, then upload the new ZIP.

## 2. Claude Code
```bash
git clone https://github.com/jeetashgir786786/PCBDESIGNER_SKILL_JGIR.git
mkdir -p ~/.claude/skills
cp -r PCBDESIGNER_SKILL_JGIR/pcbdesigner-skill-jgir ~/.claude/skills/        # personal
# or, for one project only:
# cp -r PCBDESIGNER_SKILL_JGIR/pcbdesigner-skill-jgir <project>/.claude/skills/
```
To follow updates, create a symlink to the clone instead of copying, then `git pull`.

## 3. Claude API / Agent SDK
Upload the zipped folder as a custom skill with the Skills API. See the [Agent Skills docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

## 4. Other agents
Give `SKILL.md` to the agent as its instructions, and the `references/` folder as knowledge files. The scripts are plain Python and Bash and run anywhere their dependencies are installed.

## KiCad toolkit dependencies (optional)
You only need these if you want the agent, or you, to generate and route real KiCad projects.

| Need | Linux (Ubuntu/Debian) | Notes |
|---|---|---|
| KiCad 7+ with the `pcbnew` Python module | `sudo apt install kicad` | Tested on 7.0.11. On Windows, use the KiCad Command Prompt. On macOS, use the Python bundled in KiCad.app |
| Java 17+ | `sudo apt install openjdk-17-jre` | Needed by Freerouting |
| Freerouting | `bash scripts/kicad_auto/get_freerouting.sh` | Official GitHub release v1.9.0 |
| numpy, Pillow | `pip install numpy pillow` | A* finisher |
| Xvfb, xdotool, ImageMagick, librsvg | `sudo apt install xvfb xdotool imagemagick librsvg2-bin` | Headless image capture |
| CadQuery (optional) | `pip install cadquery` | Placeholder 3D bodies |

Check what's installed:
```bash
python3 pcbdesigner-skill-jgir/scripts/kicad_auto/check_env.py
```
