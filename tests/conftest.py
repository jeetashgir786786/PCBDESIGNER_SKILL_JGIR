import sys

sys.dont_write_bytecode = True   # keep the skill folder free of __pycache__
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "pcbdesigner-skill-jgir"
sys.path.insert(0, str(SKILL / "scripts" / "kicad_auto"))
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
FIXTURES = Path(__file__).parent / "fixtures"
