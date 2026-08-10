# harden-agentmemory-agent-integrations — Tasks

## 1. Fix circuit breaker

- [x] 1.1 Stop agentmemory server: `agentmemory stop` — stopped successfully (pid 98923 + iii-engine pid 3604)
- [ ] 1.2 Wait 3 seconds for port release
- [x] 1.3 Start agentmemory server: `agentmemory &` — restarted, pid 61036
- [ ] 1.4 Verify health with retry (3 attempts, 5s interval): `curl localhost:3111/agentmemory/health`
- [x] 1.5 Confirm circuit breaker state is "closed" — verified: Circuit: closed, Sessions: 442

## 2. Fix PATH issue

- [x] 2.1 Check `which iii` — confirms NOT on PATH (but already in .zshrc line 94)
- [ ] 2.2 Check `~/.agentmemory/bin/iii --version` — confirm pinned version works
- [x] 2.3 Add `~/.agentmemory/bin` to PATH in `~/.zshrc` — ALREADY PRESENT (line 94)
- [x] 2.4 Source `~/.zshrc` and re-verify `which iii` — resolves to ~/.agentmemory/bin/iii (0.11.2)
- [x] 2.5 Re-run `agentmemory doctor` — engine-version-mismatch persists (cosmetic: server uses its own binary, not PATH)

## 3. Wire fable-5 (fable-5) MCP

- [ ] 3.1 Backup config: `cp ~/.claude.json ~/.claude.json.bak 2>/dev/null || true`
- [ ] 3.2 Run `agentmemory connect claude-code`
- [ ] 3.3 Validate JSON: `python3 -m json.tool ~/.claude.json > /dev/null`
- [ ] 3.4 Verify entry: `grep -q agentmemory ~/.claude.json`

## 4. Wire OpenCode MCP

- [ ] 4.1 Backup config: `cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak 2>/dev/null || true`
- [ ] 4.2 Run `agentmemory connect opencode`
- [ ] 4.3 Validate JSON: `python3 -m json.tool ~/.config/opencode/opencode.json > /dev/null`
- [ ] 4.4 Verify entry: `grep -q agentmemory ~/.config/opencode/opencode.json`

## 5. Document agent scope

- [ ] 5.1 Add agentmemory shared-scope documentation to workspace-knowledge-tools skill
- [ ] 5.2 Document that `shared` scope is intentional for cross-agent memory

## 6. Verify all integrations

- [ ] 6.1 `agentmemory doctor` → 9/9 passing
- [ ] 6.2 `agentmemory status` → healthy, sessions incrementing
- [ ] 6.3 Hermes: verify memory injection in active session
- [ ] 6.4 Pi: verify memory commands work
- [ ] 6.5 fable-5: verify memory tools available
- [ ] 6.6 OpenCode: verify memory tools available

## 7. Archive

- [ ] 7.1 No source commits needed (config changes only)
- [ ] 7.2 Archive change and commit store
