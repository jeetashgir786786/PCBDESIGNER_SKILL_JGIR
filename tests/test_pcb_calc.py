"""Smoke tests for the calculator CLI: every documented example must run and print a result."""
import re
import subprocess
import sys

import pytest
from conftest import SKILL

CALC = SKILL / "scripts" / "pcb_calc.py"
EXAMPLES = [l.strip()[len("pcb_calc.py "):] for l in
            subprocess.run([sys.executable, str(CALC), "--help"], capture_output=True, text=True).stdout.splitlines()
            if l.strip().startswith("pcb_calc.py ")]


def test_help_lists_examples():
    assert len(EXAMPLES) >= 16


@pytest.mark.parametrize("args", EXAMPLES)
def test_example_runs(args):
    r = subprocess.run([sys.executable, str(CALC), *args.split()], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert re.search(r"\d", r.stdout)


def test_ztarget_value():
    r = subprocess.run([sys.executable, str(CALC), "ztarget", "--v", "0.8", "--ripple-pct", "2", "--di", "40"],
                       capture_output=True, text=True)
    # 0.8 V * 2 % / 40 A = 0.4 mOhm
    assert "0.4" in r.stdout
