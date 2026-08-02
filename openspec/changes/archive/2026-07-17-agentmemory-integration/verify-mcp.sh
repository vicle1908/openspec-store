#!/bin/bash
set -euo pipefail

echo "=== MCP Integration Verification ==="
echo ""

BASE_URL="${AGENTMEMORY_URL:-http://localhost:3111}"
VIEWER_URL="${AGENTMEMORY_VIEWER_URL:-http://localhost:3113}"

echo "1. Checking agentmemory server health..."
HEALTH=$(curl -sf "$BASE_URL/agentmemory/health") || {
  echo "   FAIL: Server not running at $BASE_URL"
  echo "   Start: source ~/.tdt/.env && agentmemory"
  exit 1
}
HEALTH_JSON="$HEALTH" python3 - <<'PY'
import json, os
payload = json.loads(os.environ["HEALTH_JSON"])
status = payload.get("status")
version = payload.get("version")
if status != "healthy":
    raise SystemExit(f"health status is {status!r}, expected 'healthy'")
print(f"   OK: Server healthy (v{version})")
PY

echo "2. Checking viewer..."
curl -sf "$VIEWER_URL" > /dev/null || {
  echo "   FAIL: Viewer not accessible at $VIEWER_URL"
  exit 1
}
echo "   OK: Viewer accessible"

echo "3. Checking MCP tools through stdio protocol..."
AGENTMEMORY_URL="$BASE_URL" python3 - <<'PY'
import json
import os
import select
import subprocess
import time

required = {
    "memory_smart_search",
    "memory_save",
    "memory_sessions",
    "memory_export",
    "memory_audit",
    "memory_governance_delete",
}

env = os.environ.copy()
proc = subprocess.Popen(
    ["npx", "-y", "@agentmemory/mcp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env=env,
)
try:
    request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()

    line = ""
    deadline = time.time() + 10
    assert proc.stdout is not None
    while time.time() < deadline:
        ready, _, _ = select.select([proc.stdout], [], [], 0.2)
        if ready:
            line = proc.stdout.readline().strip()
            break
    if not line:
        stderr = proc.stderr.read(1000) if proc.stderr is not None else ""
        raise SystemExit(f"MCP tools/list timed out; stderr={stderr!r}")

    response = json.loads(line)
    tools = response.get("result", {}).get("tools", [])
    names = {tool.get("name") for tool in tools}
    missing = sorted(required - names)
    if missing:
        raise SystemExit(f"Missing MCP tools: {', '.join(missing)}")
    if len(tools) < 53:
        raise SystemExit(f"Expected at least 53 tools, got {len(tools)}")
    print(f"   OK: {len(tools)} MCP tools available")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
PY

echo ""
echo "=== ALL CHECKS PASSED ==="
