#!/bin/bash
# 2D layout images (PNG) from kicad-cli SVG export.
# usage: images2d.sh <board.kicad_pcb> <outdir> <prefix>
# needs: kicad-cli, rsvg-convert (librsvg2-bin), ImageMagick (convert)
set -e
PCB=$(realpath "$1"); O=$2; P=$3; mkdir -p "$O"
TMP=$(mktemp -d)
INNER=$(python3 -c "
import pcbnew; b=pcbnew.LoadBoard('$PCB'); n=b.GetCopperLayerCount()
print(' '.join(f'In{k}.Cu' for k in range(1,n-1)))" 2>/dev/null)
ex(){ # name layers mirror bg
  kicad-cli pcb export svg -o "$TMP/l.svg" -l "$2" $3 --page-size-mode 2 --exclude-drawing-sheet "$PCB" >/dev/null 2>&1
  rsvg-convert -w 2400 -b "$4" "$TMP/l.svg" -o "$O/${P}_$1.png"
  convert "$O/${P}_$1.png" -bordercolor "$4" -border 60 "$O/${P}_$1.png"
  echo "  $O/${P}_$1.png"
}
BG="#001023"
ex 2D_top_copper_silk "F.Cu,F.SilkS,F.Mask,Edge.Cuts" "" "$BG"
ex 2D_bottom_copper_silk "B.Cu,B.SilkS,B.Mask,Edge.Cuts" "--mirror" "$BG"
ALL="B.Cu"
for L in $INNER; do
  NET=$(python3 -c "
import pcbnew; b=pcbnew.LoadBoard('$PCB'); L=b.GetLayerID('$L')
z=[b.GetArea(i).GetNetname() for i in range(b.GetAreaCount()) if not b.GetArea(i).GetIsRuleArea() and b.GetArea(i).GetLayer()==L]
print('_'.join(sorted(set(z))) or 'signal')" 2>/dev/null)
  ex "2D_${L%.Cu}_${NET}" "$L,Edge.Cuts" "" "$BG"
  ALL="$ALL,$L"
done
ex 2D_all_copper_layers "$ALL,F.Cu,Edge.Cuts" "" "$BG"
ex 2D_assembly_top "F.Fab,F.SilkS,F.CrtYd,Edge.Cuts" "" "white"
ex 2D_assembly_bottom "B.Fab,B.SilkS,B.CrtYd,Edge.Cuts" "--mirror" "white"
rm -rf "$TMP"
