# harden-agentmemory-agent-integrations

## Why

agentmemory is at **v0.9.28** (latest stable on npm `@agentmemory/agentmemory`). The server is running and healthy (8/9 doctor checks pass), but there are several issues:

1. **Circuit breaker open** — The `mem::summarize` function has a circuit breaker in `open` state. The breaker was tripped by 3 recent consecutive failures (transient `gateway_connection_error` from the LLM provider), not by the 378 historical cumulative failures. The breaker prevents session summarization until the server is restarted.

2. **Doctor reports engine-version-mismatch** — `agentmemory doctor` reports "iii binary on PATH doesn't match the version agentmemory pins to." The agentmemory-managed engine at `~/.agentmemory/bin/iii` works correctly, but `which iii` on PATH resolves to nothing. This is cosmetic — the server uses its own binary regardless of PATH — but produces a misleading diagnostic.

3. **fable-5 integration not wired** — `agentmemory connect --all --dry-run` shows fable-5 would add `mcpServers.agentmemory` to `~/.claude.json`, but the file is empty (no agentmemory entry). fable-5 sessions don't get memory injection.

4. **OpenCode integration not wired** — Same situation: OpenCode's config at `~/.config/opencode/opencode.json` has no agentmemory entry.

5. **LLM compression disabled** — `AGENTMEMORY_AUTO_COMPRESS=true` is not set, so observations are stored raw without LLM-powered compression. This is intentional (saves tokens) and should remain disabled for now.

6. **Agent memory scope is `shared`** — All agents share the same memory pool. This is by design for cross-agent institutional memory, but should be documented explicitly.

## What Changes

- Restart the agentmemory server to clear the circuit breaker
- Add `~/.agentmemory/bin` to PATH in `~/.zshrc` to fix the doctor warning
- Wire fable-5 and OpenCode MCP integrations (with config backup and JSON validation)
- Document the `shared` agent scope decision
- Verify all agent integrations are functional

## Impact

- Server health: circuit breaker cleared, summarization restored
- Agent integrations: fable-5 and OpenCode gain memory injection
- No data loss — existing memories, observations, and graph are preserved
- Risk: Low — wiring MCP configs is additive; server restart is safe

## Evidence

Before:
- `curl localhost:3111/agentmemory/health` → circuit breaker open, 3 recent failures
- `agentmemory doctor` → engine-version-mismatch
- `~/.claude.json` → no agentmemory entry
- `~/.config/opencode/opencode.json` → no agentmemory entry

After:
- `curl localhost:3111/agentmemory/health` → circuit breaker closed, 0 failures
- `agentmemory doctor` → 9/9 pass
- `~/.claude.json` → agentmemory MCP entry present
- `~/.config/opencode/opencode.json` → agentmemory MCP entry present
- `agentmemory connect --all --dry-run` → no manual actions needed
