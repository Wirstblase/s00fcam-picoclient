#!/usr/bin/env bash
# setup_wifi.sh — Generate wifi_creds.json
# Run this BEFORE copying files to the Pico

set -euo pipefail

CREDS_FILE="wifi_creds.json"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  s00fcam-picoclient — WiFi Credentials Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "$CREDS_FILE" ]; then
    echo "$CREDS_FILE already exists."
    read -rp "   Overwrite? [y/N] " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "   Keeping existing credentials. Done."
        exit 0
    fi
    echo ""
fi

read -rp "  WiFi SSID: " ssid
if [ -z "$ssid" ]; then
    echo "SSID cannot be empty."
    exit 1
fi

read -rsp "  WiFi Password: " password
echo ""

if [ -z "$password" ]; then
    echo ""
    echo "Empty password — connecting to an open network."
fi

cat > "$CREDS_FILE" <<EOF
{"ssid": "$ssid", "password": "$password"}
EOF

echo ""
echo "Credentials written to $CREDS_FILE"
echo ""
echo "Next steps:"
echo "  1. Connect your Pi via USB"
echo "  2. Copy $CREDS_FILE to the pi's filesystem:"
echo "     mpremote cp $CREDS_FILE :"
echo "     (or drag it via Thonny's file manager)"
echo ""
