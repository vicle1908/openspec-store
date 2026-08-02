#!/bin/bash
set -euo pipefail

LABEL="com.tdt.agentmemory"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
SERVICE="gui/$(id -u)/${LABEL}"

echo "=== Agentmemory LaunchAgent Verification ==="
echo ""

if [ ! -f "$PLIST" ]; then
  echo "   FAIL: Missing $PLIST"
  exit 1
fi
plutil -lint "$PLIST" >/dev/null
echo "   OK: plist is valid"

if ! launchctl print "$SERVICE" >/dev/null 2>&1; then
  echo "   FAIL: $SERVICE is not loaded"
  echo "   Run: launchctl bootstrap gui/\$(id -u) $PLIST"
  exit 1
fi
echo "   OK: $SERVICE is loaded"

if ! launchctl print "$SERVICE" | grep -q "state = running"; then
  echo "   FAIL: $SERVICE is not running"
  exit 1
fi
echo "   OK: $SERVICE is running"

curl -sf http://localhost:3111/agentmemory/health >/dev/null || {
  echo "   FAIL: agentmemory health endpoint unavailable"
  exit 1
}
echo "   OK: health endpoint available"

agentmemory status | grep -q "Health:.*healthy" || {
  echo "   FAIL: agentmemory status is not healthy"
  exit 1
}
echo "   OK: agentmemory status healthy"

echo ""
echo "=== ALL CHECKS PASSED ==="
