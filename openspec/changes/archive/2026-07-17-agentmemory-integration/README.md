# Agentmemory Integration — Quick Start

## Current implementation state

- `agentmemory` and `@agentmemory/mcp` are installed globally at version `0.9.24`.
- REST API: `http://localhost:3111`
- Viewer: `http://localhost:3113`
- Ollama is managed as a Homebrew service for reliable embeddings:
  `brew services start ollama`
- TDT LLM credentials remain centralized in `~/.tdt/.env`.
- Agentmemory config lives in `~/.agentmemory/.env` and references those TDT variables.
- `~/.agentmemory/.env` must use resolved literal values for `OPENAI_API_KEY` and `OPENAI_BASE_URL`; do not put `${OMNIROUTE_*}` references there because agentmemory uses `dotenv`, not `dotenv-expand`.

## Persistent startup

Agentmemory now runs as a user LaunchAgent:

- plist: ``/Users/lekhanhvinh/Developer/tdt/tdt-meta/config/launchd/com.tdt.agentmemory.plist` deployed to `~/Library/LaunchAgents/com.tdt.agentmemory.plist``
- stdout: `~/.agentmemory/launchd-stdout.log`
- stderr: `~/.agentmemory/launchd-stderr.log`
- command: `source ~/.tdt/.env && exec ~/.npm-global/bin/agentmemory`

Ollama embeddings are also managed persistently with Homebrew:

```bash
brew services start ollama
```

LaunchAgent controls:

```bash
# Start/load
launchctl bootstrap gui/$(id -u) `/Users/lekhanhvinh/Developer/tdt/tdt-meta/config/launchd/com.tdt.agentmemory.plist` deployed to `~/Library/LaunchAgents/com.tdt.agentmemory.plist`
launchctl enable gui/$(id -u)/com.tdt.agentmemory

# Stop/unload
launchctl bootout gui/$(id -u) `/Users/lekhanhvinh/Developer/tdt/tdt-meta/config/launchd/com.tdt.agentmemory.plist` deployed to `~/Library/LaunchAgents/com.tdt.agentmemory.plist`

# Inspect
launchctl print gui/$(id -u)/com.tdt.agentmemory
agentmemory status
```

If `agentmemory status` shows `v?`, `Health: unknown`, or `0` sessions unexpectedly, the REST worker is not running even if MCP shim processes exist; reload the LaunchAgent with the commands above.

## Agent integrations

### Claude Code

Configured in:

- `~/.claude.json` — MCP server `agentmemory`
- `~/.claude/settings.json` — 12 lifecycle hook entries pointing at the globally installed plugin scripts

Refresh after agentmemory upgrades:

```bash
agentmemory connect claude-code --force
# Hooks are maintained manually in ~/.claude/settings.json from the installed plugin scripts.
```

### Codex

Configured in:

- `~/.codex/config.toml` — MCP server `agentmemory`
- `~/.codex/hooks.json` — Codex Desktop hook workaround for lifecycle capture

Refresh after agentmemory upgrades:

```bash
agentmemory connect codex --with-hooks --force
```

### pi

Configured in:

- `~/.pi/agent/extensions/agentmemory/`
- `~/.pi/agent/settings.json` with `~/.pi/agent/extensions/agentmemory` in `extensions`

The pi extension was copied from the upstream `integrations/pi` folder because `agentmemory connect pi` reports that automatic TypeScript extension registration is not implemented yet.


## Installed AI CLI coverage

The following installed AI CLIs are integrated with agentmemory:

| CLI | Integration | Config path | Notes |
|---|---|---|---|
| Claude Code (`claude`) | MCP + 12 hooks | `~/.claude.json`, `~/.claude/settings.json` | Upstream recommends plugin marketplace; local config also pins explicit hook scripts for inspectability. |
| Codex (`codex`) | MCP + global hook workaround | `~/.codex/config.toml`, `~/.codex/hooks.json` | `agentmemory connect codex --with-hooks --force`; restart Codex to pick up changes. |
| pi (`pi`) | Native TypeScript extension | `~/.pi/agent/extensions/agentmemory`, `~/.pi/agent/settings.json` | Manual copy from upstream `integrations/pi` because `connect pi` reports auto-copy is not implemented. |
| Gemini CLI (`gemini`) | MCP | `~/.gemini/settings.json` | Wired with `agentmemory connect gemini-cli --force`. |
| Cursor (`cursor`) | MCP | `~/.cursor/mcp.json` | Wired with `agentmemory connect cursor --force`. |
| Kiro (`kiro`) | MCP | `~/.kiro/settings/mcp.json` | Wired with `agentmemory connect kiro --force`. |
| Zed (`zed`) | MCP context server | `~/.config/zed/settings.json` | Wired with `agentmemory connect zed --force`. |
| Goose (`goose`) | MCP stdio extension | `~/.config/goose/config.yaml` | Added manually because `agentmemory connect` does not currently expose a Goose adapter. |

The `skills` CLI was also run with `npx skills add rohitg00/agentmemory -y -a '*'` so the eight agentmemory skills are available broadly across installed/supported agents.

## Verification scripts

Run these from the workspace root or from `tdt-meta`:

```bash
# Installation, version, credentials, Ollama, and config
./openspec/changes/agentmemory-integration/verify-install.sh

# OmniRoute LLM + Ollama embedding calls
./openspec/changes/agentmemory-integration/verify-omniroute-ollama.sh

# REST API, viewer, and MCP tools/list (expects 53 tools)
./openspec/changes/agentmemory-integration/verify-mcp.sh

# Claude hook config, plugin scripts, and audit access
./openspec/changes/agentmemory-integration/verify-hooks.sh

# Real save/search/export/delete and slot lifecycle operations
./openspec/changes/agentmemory-integration/verify-e2e.sh
```

Full OpenSpec validation:

```bash
openspec validate agentmemory-integration --strict
openspec instructions apply --change agentmemory-integration --json
```

Expected OpenSpec progress is `60/60`, `all_done`.

## Real-operation notes

- Use `memory_save` only for durable facts, decisions, preferences, workflows, or reusable lessons.
- Use `memory_smart_search` or `memory_recall` before relying on prior context.
- Use `memory_export` for persistence checks.
- Use `memory_audit` for operational inspection.
- Use `memory_governance_delete` with `memoryIds`, not a single `id` field:

```json
{
  "memoryIds": "mem_abc123",
  "reason": "cleanup test memory"
}
```

The MCP schema documents `memoryIds` as a comma-separated string. Context7 upstream docs also say the API accepts an ID array; the local MCP path has been verified with the comma-separated string form.

Slot APIs are enabled and verified: `memory_slot_create`, `memory_slot_get`, `memory_slot_append`, `memory_slot_replace`, and `memory_slot_delete`.

`memory_diagnose` may warn that older memories have no project scope. For the current small memory set this is non-blocking, but future multi-repo usage should prefer passing stable `project` values to `memory_save` and follow any migrate remediation printed by diagnostics.

## Historical import

A bounded historical import was run with:

```bash
agentmemory import-jsonl --max-files 50
```

This seeded prior Claude Code sessions for Replay verification without importing the entire large transcript tree in one pass. For more import coverage, run by project subdirectory under `~/.claude/projects`.

## Rollback

```bash
agentmemory stop
npm uninstall -g @agentmemory/agentmemory @agentmemory/mcp
brew services stop ollama  # only if Ollama is no longer needed by other tools
rm -rf ~/.agentmemory      # optional destructive data removal
```

Also remove agent config entries from `~/.claude.json`, `~/.claude/settings.json`, `~/.codex/config.toml`, `~/.codex/hooks.json`, and `~/.pi/agent/settings.json` if fully uninstalling.
