#!/bin/bash
# One-shot: spec -> KiCad project -> autoroute -> verify -> fab package -> 2D/3D images.
# usage: pipeline.sh <spec.py> <out_dir> [freerouting passes=20] [attempts=1]
# Stops after a failed gate; read the printed report before changing anything.
set -o pipefail
T=$(cd "$(dirname "$0")" && pwd)
SPEC=$1; OUT=$2; PASSES=${3:-20}; ATT=${4:-1}
NAME=$(python3 -c "import importlib.util,sys;s=importlib.util.spec_from_file_location('s','$SPEC');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(m.NAME)")
f(){ grep -v '^swig/python'; }
echo "== build";  B=$(python3 "$T/build.py" "$SPEC" "$OUT" 2>&1 | f) || { echo "$B"; exit 1; }; echo "$B"
if echo "$B" | grep -q COURTYARD; then echo "!! courtyard overlaps: fix placement in the spec before routing"; exit 1; fi
echo "== route";  python3 "$T/route.py" "$OUT/$NAME.kicad_pcb" --passes "$PASSES" --attempts "$ATT" 2>&1 | f
echo "== verify"; python3 "$T/verify.py" "$OUT" "$NAME" 2>&1 | f; V=$?
echo "== fab";    python3 "$T/fab.py" "$OUT" "$NAME" 2>&1 | f
echo "== images"; bash "$T/images2d.sh" "$OUT/$NAME.kicad_pcb" "$OUT/images" "$NAME" 2>&1 | f
bash "$T/images3d.sh" "$OUT/$NAME.kicad_pcb" "$OUT/images" "$NAME" 2>&1 | f
[ $V -eq 0 ] && echo "ALL GATES PASSED (ERC still to run in the GUI on KiCad 7)" || echo "VERIFY FAILED - see above"
