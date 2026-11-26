#!/usr/bin/env python3
"""Validate the skill folder and build the installable ZIP.

usage: python3 tools/package_skill.py [--check-only] [--version X.Y.Z]

Checks (same limits Claude enforces on upload):
  * SKILL.md exists and starts with YAML frontmatter holding `name` and `description`
  * name: lowercase letters, digits, hyphens; <= 64 chars; no reserved words; matches the folder name
  * description: non-empty, <= 1024 chars, no XML/angle brackets
  * no caches, logs or generated CAD junk inside the skill folder
Output: dist/<name>-v<version>.zip containing the folder <name>/ (the layout Claude expects).
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "pcbdesigner-skill-jgir"
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
RESERVED = ("anthropic", "claude")
JUNK_DIRS = {"logs"}                                   # build artefacts that must never be committed
JUNK_SUFFIXES = {".dsn", ".ses", ".kicad_prl", ".zip"}
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".ruff_cache"}  # local caches: ignored, never packaged
SKIP_SUFFIXES = {".pyc", ".pyo"}


def read_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with '---' YAML frontmatter")
    end = text.index("\n---", 4)
    block = text[4:end]
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(block)
    except ImportError:  # minimal fallback parser for `key: value` lines
        data = {}
        for line in block.splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def validate(skill_dir: Path = SKILL_DIR) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"missing {skill_md}"]
    try:
        fm = read_frontmatter(skill_md)
    except ValueError as e:
        return [str(e)]
    name, desc = str(fm.get("name", "")), str(fm.get("description", ""))
    if not NAME_RE.match(name):
        errors.append(f"name {name!r}: lowercase letters, digits and hyphens only, max 64 chars")
    if any(w in name for w in RESERVED):
        errors.append(f"name {name!r} contains a reserved word {RESERVED}")
    if name != skill_dir.name:
        errors.append(f"name {name!r} must match folder name {skill_dir.name!r}")
    if not desc:
        errors.append("description is empty")
    if len(desc) > 1024:
        errors.append(f"description is {len(desc)} chars (max 1024)")
    if "<" in desc or ">" in desc:
        errors.append("description must not contain angle brackets / XML")
    for p in skill_dir.rglob("*"):
        if p.is_dir() and p.name in JUNK_DIRS:
            errors.append(f"junk directory in skill: {p.relative_to(ROOT)}")
        if p.is_file() and p.suffix in JUNK_SUFFIXES:
            errors.append(f"junk file in skill: {p.relative_to(ROOT)}")
    return errors


def build(version: str, skill_dir: Path = SKILL_DIR) -> Path:
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    out = dist / f"{skill_dir.name}-v{version}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(skill_dir.rglob("*")):
            if p.is_file() and not (set(p.relative_to(skill_dir).parts) & SKIP_DIRS) and p.suffix not in SKIP_SUFFIXES:
                info = zipfile.ZipInfo.from_file(p, f"{skill_dir.name}/{p.relative_to(skill_dir).as_posix()}")
                if p.suffix == ".sh" or p.stat().st_mode & 0o111:
                    info.external_attr = 0o755 << 16
                else:
                    info.external_attr = 0o644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, p.read_bytes())
    return out


def current_version() -> str:
    m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "0.0.0"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--version", default=None, help="defaults to the newest version in CHANGELOG.md")
    a = ap.parse_args()
    errors = validate()
    if errors:
        print("Skill validation FAILED:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"Skill validation passed: {SKILL_DIR.name}")
    if a.check_only:
        return 0
    out = build((a.version or current_version()).lstrip("v"))
    with zipfile.ZipFile(out) as zf:
        n = len(zf.namelist())
    print(f"Built {out.relative_to(ROOT)} ({n} files, {out.stat().st_size / 1024:.0f} KiB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
