#!/bin/bash
set -euo pipefail

echo "=== Hooks Verification ==="
echo ""

BASE_URL="${AGENTMEMORY_URL:-http://localhost:3111}"
PLUGIN_ROOT="$HOME/.npm-global/lib/node_modules/@agentmemory/agentmemory/plugin"

echo "1. Checking hooks in Claude Code config..."
CONFIG_FILE="$HOME/.claude/settings.json"
if [ -f "$CONFIG_FILE" ]; then
  HOOKS=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(sum(len(v) for v in c.get('hooks',{}).values()))" 2>/dev/null)
  echo "   OK: $HOOKS hook entries configured in $CONFIG_FILE"
else
  echo "   WARN: No Claude Code settings.json found (hooks may be via plugin)"
fi

echo "2. Checking hook scripts exist..."
MISSING=0
for script in session-start prompt-submit pre-tool-use post-tool-use stop pre-compact; do
  if [ ! -f "$PLUGIN_ROOT/scripts/${script}.mjs" ]; then
    echo "   FAIL: Missing $PLUGIN_ROOT/scripts/${script}.mjs"
    MISSING=$((MISSING + 1))
  fi
done
if [ "$MISSING" -gt 0 ]; then
  echo "   FAIL: $MISSING hook script(s) missing"
  exit 1
fi
echo "   OK: All core hook scripts present"

echo "3. Checking agentmemory audit log..."
AUDIT=$(curl -sf "$BASE_URL/agentmemory/audit?limit=5" 2>/dev/null || echo "")
if [ -n "$AUDIT" ]; then
  COUNT=$(echo "$AUDIT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('entries', d if isinstance(d, list) else [])))" 2>/dev/null)
  echo "   OK: $COUNT audit entries available"
else
  echo "   WARN: Could not fetch audit log (server may not be running)"
fi

echo ""
echo "=== ALL CHECKS PASSED ==="
