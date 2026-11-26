#!/bin/bash
# Download the Freerouting autorouter jar from its official GitHub releases (github.com/freerouting/freerouting).
# Pinned to v1.9.0 - the version this toolkit was tested with (its CLI: -de in.dsn -do out.ses -mp passes -mt threads).
# usage: get_freerouting.sh [dest_dir=~/.local/share/freerouting]
set -e
VER=${FREEROUTING_VERSION:-1.9.0}
DEST=${1:-$HOME/.local/share/freerouting}
mkdir -p "$DEST"
URL="https://github.com/freerouting/freerouting/releases/download/v${VER}/freerouting-${VER}.jar"
echo "downloading $URL"
curl -fL --retry 3 -o "$DEST/freerouting.jar" "$URL"
echo "saved $DEST/freerouting.jar  (needs Java 17+: java -version)"
echo "export FREEROUTING_JAR=$DEST/freerouting.jar"
