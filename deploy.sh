#!/usr/bin/env bash
# deploy.sh — Copy all source files to the Pi Pico 2 W via mpremote
# Overwrites existing files. Run from the project root.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
CREDS_FILE="$SCRIPT_DIR/wifi_creds.json"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  s00fcam-picoclient — Deploy to Pi pico"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if ! command -v mpremote &> /dev/null; then
    echo "mpremote not found. Install with: pip3 install mpremote"
    exit 1
fi

if [ ! -d "$SRC_DIR" ]; then
    echo "src/ directory not found. Run from the project root."
    exit 1
fi

echo "Looking for pi..."
echo ""

CMD="mpremote"

for f in "$SRC_DIR"/*.py; do
    fname=$(basename "$f")
    echo "  📄 $fname"
    CMD="$CMD cp $f :$fname +"
done

if [ -f "$CREDS_FILE" ]; then
    echo "  🔑 wifi_creds.json"
    CMD="$CMD cp $CREDS_FILE :wifi_creds.json +"
else
    echo ""
    echo "wifi_creds.json not found — run ./setup_wifi.sh first"
fi

CMD="$CMD reset"

echo ""
echo "Deploying..."
eval "$CMD"

echo ""
echo "Deploy complete! rebooting pi"
echo ""
