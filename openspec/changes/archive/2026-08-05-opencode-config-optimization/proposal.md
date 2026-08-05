# Proposal: OpenCode Configuration Optimization

## Why

The current OpenCode config has providers and agents set up correctly but is missing several built-in optimization features documented in the official OpenCode docs (opencode.ai/docs). Specifically:

1. **LSP disabled** — No language server integration. Agents can't get real-time diagnostics (type errors, lint issues) from the code they edit. The official docs say LSP "can help the agent find and fix issues by providing diagnostics."
2. **Formatters disabled** — No auto-formatting after writes/edits. Code style inconsistencies accumulate. Official docs: "OpenCode can format files after they are written or edited using language-specific formatters."
3. **No workspace instructions** — OpenCode doesn't load our `AGENTS.md` files, so agents lack project context. Official docs support `instructions` array pointing to rule files.
4. **No compaction config** — Long sessions can overflow context. Default compaction is on but unconfigured.
5. **No watcher ignores** — File watcher processes node_modules, .git, __pycache__ unnecessarily.
6. **Google proxy down** — Port 8045 unreachable, making all Google/Antigravity models unavailable.
7. **agentmemory MCP down** — Port 3111 unreachable, making the memory feature non-functional.

## What Changes

### Enable (per official docs)
- **LSP**: `pyright` (Python), `gopls` (Go), `typescript` (JS/TS), `sourcekit-lsp` (Swift) — all have built-in support
- **Formatters**: `ruff` (Python), `gofmt` (Go), `prettier` (JS/TS/HTML/CSS/JSON/YAML)
- **Instructions**: Point to workspace `AGENTS.md` for project context
- **Compaction**: Enable auto-compaction with pruning
- **Watcher ignores**: Skip node_modules, .git, __pycache__, .venv, dist, build

### Fix
- Disable `agentmemory` MCP (server not running, connection refused on 3111)

### Skip (not applicable)
- No spec delta needed (config-only change)

## Compatibility

- All changes are additive or fix existing dead configs
- LSP/formatters auto-install when requirements are met (per official docs)
- No breaking changes to existing workflows

## Reference

All changes verified against official documentation:
- https://opencode.ai/docs/lsp
- https://opencode.ai/docs/formatters
- https://opencode.ai/docs/config
- https://opencode.ai/docs/mcp-servers
- https://opencode.ai/docs/tools
