#!/bin/bash
# Real KiCad 3D-viewer images: top, bottom, two isometric views and a ray-traced hero shot.
# usage: images3d.sh <board.kicad_pcb> <outdir> <prefix> [zoom_clicks=2]
#  KiCad 9+: uses `kicad-cli pcb render` (headless).
#  KiCad 7/8: drives the GUI 3D viewer under Xvfb with xdotool + ImageMagick `import`.
#             Toolbar/menu click coordinates below were measured on KiCad 7.0.11 at 1920x1200;
#             if a view comes out wrong on another version, re-measure them from a screenshot.
#  env: RT_WAIT=90 (seconds for the ray-tracer), DISP=:78
PCB=$(realpath "$1"); O=$(realpath -m "$2"); P=$3; Z=${4:-2}; mkdir -p "$O"
MAJ=$(kicad-cli version | cut -d. -f1)
if [ "$MAJ" -ge 9 ] && kicad-cli pcb render --help >/dev/null 2>&1; then
  r(){ kicad-cli pcb render -o "$O/${P}_$1.png" -w 1920 -h 1200 $2 "$PCB" && echo "  $O/${P}_$1.png"; }
  r 3D_top "--side top --quality high"
  r 3D_bottom "--side bottom --quality high"
  r 3D_iso_top "--side top --rotate -45,0,-35 --perspective --quality high"
  r 3D_iso_bottom "--side bottom --rotate 45,0,35 --perspective --quality high"
  r 3D_iso_raytraced "--side top --rotate -45,0,-35 --perspective --quality high --floor"
  exit 0
fi
export DISPLAY=${DISP:-:78}
for v in 6 7 8; do export KICAD${v}_3DMODEL_DIR=${KICAD7_3DMODEL_DIR:-/usr/share/kicad/3dmodels}; done
pgrep -f "Xvfb $DISPLAY" >/dev/null || (Xvfb $DISPLAY -screen 0 1920x1200x24 >/dev/null 2>&1 &); sleep 2
cd "$(dirname "$PCB")"
pcbnew "$(basename "$PCB")" >/tmp/pcbnew_cap.log 2>&1 & PID=$!
for i in $(seq 1 40); do sleep 2
  D=$(xdotool search --name "Configure Global" 2>/dev/null | head -1); [ -n "$D" ] && xdotool key --window $D Return
  W=$(xdotool search --name "PCB Editor" 2>/dev/null | head -1); [ -n "$W" ] && break; done
[ -z "$W" ] && { echo "pcbnew window not found"; kill $PID; exit 1; }
sleep 4; xdotool windowactivate --sync $W; xdotool key --window $W alt+3
for i in $(seq 1 30); do sleep 2; V=$(xdotool search --name "3D Viewer" 2>/dev/null | head -1); [ -n "$V" ] && break; done
[ -z "$V" ] && { echo "3D viewer not found"; kill $PID; exit 1; }
sleep 8; xdotool windowmove $V 0 0; xdotool windowsize $V 1920 1160; sleep 4
cap(){ xdotool mousemove 1850 1050; sleep 0.5; xdotool mousemove 1860 1060; sleep 1.5   # park cursor: hover highlights parts
       import -window root -crop 1916x1070+2+66 "$1"; echo "  $1"; }
zoom(){ xdotool mousemove 960 600; for i in $(seq 1 $Z); do xdotool click 4; sleep 0.4; done; sleep 1; }
rot(){ for i in $(seq 1 $1); do xdotool mousemove $2 43 click 1; sleep 0.5; done; }   # 280 = rotate X, 426 = rotate Z
xdotool mousemove 960 1100 click 1
xdotool key z; sleep 2; zoom; cap "$O/${P}_3D_top.png"
xdotool key z; sleep 1.5; rot 5 280; rot 3 426; zoom; cap "$O/${P}_3D_iso_top.png"
xdotool key shift+z; sleep 2; zoom; cap "$O/${P}_3D_bottom.png"
xdotool key shift+z; sleep 1.5; rot 5 280; rot 3 426; zoom; cap "$O/${P}_3D_iso_bottom.png"
xdotool key z; sleep 1.5; rot 5 280; rot 3 426; zoom
xdotool mousemove 171 12 click 1; sleep 1; xdotool mousemove 186 37 click 1   # Preferences -> Raytracing
sleep ${RT_WAIT:-90}; cap "$O/${P}_3D_iso_raytraced.png"
kill $PID 2>/dev/null; sleep 1
