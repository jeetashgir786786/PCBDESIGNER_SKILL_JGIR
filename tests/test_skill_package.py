"""The skill folder must satisfy the limits Claude enforces on upload."""
import re
import zipfile

import package_skill as ps
from conftest import SKILL


def test_skill_validates():
    assert ps.validate() == []


def test_frontmatter_fields():
    fm = ps.read_frontmatter(SKILL / "SKILL.md")
    assert fm["name"] == "pcbdesigner-skill-jgir"
    assert 50 < len(fm["description"]) <= 1024


def test_every_reference_in_router_exists():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    refs = set(re.findall(r"references/[a-z0-9-]+\.md", text))
    assert refs, "SKILL.md should route to reference files"
    missing = [r for r in refs if not (SKILL / r).exists()]
    assert not missing, f"SKILL.md points at missing files: {missing}"


def test_validator_rejects_bad_names(tmp_path):
    d = tmp_path / "Bad_Name"
    d.mkdir()
    (d / "SKILL.md").write_text("---\nname: Bad_Name\ndescription: x <tag>\n---\n")
    errs = ps.validate(d)
    assert any("lowercase" in e for e in errs)
    assert any("angle brackets" in e for e in errs)


def test_zip_layout(tmp_path, monkeypatch):
    monkeypatch.setattr(ps, "ROOT", tmp_path)
    (tmp_path / "CHANGELOG.md").write_text("## [9.9.9] - x\n")
    out = ps.build("9.9.9")
    names = zipfile.ZipFile(out).namelist()
    assert all(n.startswith("pcbdesigner-skill-jgir/") for n in names)
    assert "pcbdesigner-skill-jgir/SKILL.md" in names
    assert not any("__pycache__" in n for n in names)
