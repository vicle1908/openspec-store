# Tasks: OpenCode Configuration Optimization

## Section 1: Backup

- [x] 1.1 Backup `~/.config/opencode/opencode.jsonc` with timestamp

## Section 2: Enable LSP

- [x] 2.1 Add `"lsp": {}` to config to enable all built-in LSP servers
- [x] 2.2 Verify pyright is available: `which pyright` or install via `npm i -g pyright`

## Section 3: Enable Formatters

- [x] 3.1 Add `"formatter": {}` to config to enable all built-in formatters
- [x] 3.2 Verify ruff is available: `which ruff`

## Section 4: Add Workspace Instructions

- [x] 4.1 Add `"instructions": ["~/Developer/AGENTS.md"]` to config

## Section 5: Enable Compaction

- [x] 5.1 Add `"compaction": { "auto": true, "prune": true, "reserved": 4096 }` to config

## Section 6: Add Watcher Ignores

- [x] 6.1 Add `"watcher": { "ignore": ["**/node_modules/**", "**/.git/**", "**/__pycache__/**", "**/.venv/**", "**/dist/**", "**/build/**"] }` to config

## Section 7: Disable agentmemory MCP

- [x] 7.1 Change `"enabled": true` to `"enabled": false` on agentmemory MCP

## Section 8: Validation

- [x] 8.1 Run `opencode debug config` — verify new sections appear
- [x] 8.2 Run `opencode run 'Hello' --model shopapikey/fable-5` — verify basic functionality
- [x] 8.3 Verify config parses without errors

## Section 9: Archive

- [x] 9.1 Mark all tasks complete
- [x] 9.2 Commit to openspec-store
- [x] 9.3 Archive the change
