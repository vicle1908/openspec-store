# harden-agentmemory-agent-integrations — Design

## Circuit Breaker Reset

The circuit breaker for `mem::summarize` is in `open` state, tripped by 3 recent consecutive failures (transient `gateway_connection_error`). The 378 in the health response is the cumulative historical `failureCount`, not the current breaker state.

Reset: restart the agentmemory server. The breaker is in-memory and clears on restart.

```bash
agentmemory stop
agentmemory &
```

Post-restart verification with retry:
```bash
for i in 1 2 3; do
  sleep 5
  health=$(curl -s http://localhost:3111/agentmemory/health)
  circuit=$(echo "$health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('circuitBreaker',{}).get('state','?'))" 2>/dev/null)
  if [ "$circuit" = "closed" ]; then echo "Circuit breaker: CLOSED ✅"; break; fi
  echo "Attempt $i: circuit=$circuit, retrying..."
done
```

If `agentmemory stop` hangs (stale pidfile), use `agentmemory stop --force`.

## PATH Fix

Add `~/.agentmemory/bin` to PATH in `~/.zshrc`:
```bash
echo 'export PATH="$HOME/.agentmemory/bin:$PATH"' >> ~/.zshrc
```

This ensures `which iii` resolves correctly and eliminates the doctor warning. The server already uses its own binary regardless, so this is cosmetic.

## Agent MCP Wiring

### Pre-flight: Backup configs

Before any `connect` command, back up the target config:
```bash
cp ~/.claude.json ~/.claude.json.bak 2>/dev/null || true
cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak 2>/dev/null || true
```

### fable-5 (fable-5)

```bash
agentmemory connect claude-code
```

This adds `mcpServers.agentmemory` to `~/.claude.json`. The file currently has empty `mcpServers: {}`, so the addition is safe.

Post-connect validation:
```bash
python3 -m json.tool ~/.claude.json > /dev/null && echo "JSON valid ✅" || echo "JSON BROKEN ❌"
grep -q "agentmemory" ~/.claude.json && echo "Entry present ✅" || echo "Entry missing ❌"
```

### OpenCode

```bash
agentmemory connect opencode
```

This adds `mcp.agentmemory` to `~/.config/opencode/opencode.json` alongside the existing `mcp.mcp-router`.

Post-connect validation:
```bash
python3 -m json.tool ~/.config/opencode/opencode.json > /dev/null && echo "JSON valid ✅" || echo "JSON BROKEN ❌"
grep -q "agentmemory" ~/.config/opencode/opencode.json && echo "Entry present ✅" || echo "Entry missing ❌"
```

### Hermes

Already configured: `~/.hermes/config.yaml` has `memory.provider: agentmemory` and `plugins.enabled: [agentmemory]`. No changes needed.

### Pi

Already configured: `~/.pi/agent/extensions/agentmemory/` has `index.js`, `security.js`, `package.json`. Pi auto-discovers extensions from that directory. No changes needed.

## Agent Scope Documentation

The `AGENTMEMORY_AGENT_SCOPE=shared` setting means all agents share memories. This is the correct setting for our workspace:
- Cross-agent institutional memory (Claude learns from Codex's observations)
- Each observation tagged with agent identity (`AGENT_ID`)
- Audit trail tracks which agent wrote what

Document this in the workspace-knowledge-tools skill.

## Auto-Compression: Deferred

`AGENTMEMORY_AUTO_COMPRESS=true` is intentionally not enabled in this change. Enabling it would:
- Improve observation quality (LLM summarizes raw tool output)
- Cost API tokens proportional to tool-call frequency
- Increase memory pressure on a process already at 89% heap utilization

This should be evaluated as a separate change after baseline stability is confirmed.

## Verification

After all fixes:
1. `agentmemory doctor` → 9/9 passing
2. `curl localhost:3111/agentmemory/health` → circuit breaker closed
3. `agentmemory status` → sessions incrementing, observations captured
4. fable-5: start a session, verify memory injection appears in context
5. OpenCode: start a session, verify memory injection
6. Pi: start a session, verify memory commands work
7. Hermes: already working (existing session uses it)
