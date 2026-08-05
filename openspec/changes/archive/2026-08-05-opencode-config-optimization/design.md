# Design: OpenCode Configuration Optimization

## Changes to `~/.config/opencode/opencode.jsonc`

### 1. Enable LSP (official built-in support)

```jsonc
"lsp": {}
```

Per official docs: "To enable all built-in LSP servers, set `lsp` to `true`" or use `{}` to keep built-ins enabled. Built-in LSP servers auto-install when requirements are met:
- **pyright**: .py, .pyi — requires `pyright` installed
- **gopls**: .go — requires `go` command available
- **typescript**: .ts, .tsx, .js, .jsx — requires `typescript` in project
- **sourcekit-lsp**: .swift, .objc — requires `swift` (Xcode on macOS)

### 2. Enable Formatters (official built-in support)

```jsonc
"formatter": {}
```

Per official docs: "When formatters are enabled, OpenCode will use `prettier` for matching files if your project has `prettier` in `package.json`." Built-in formatters:
- **ruff**: .py, .pyi — requires `ruff` command
- **gofmt**: .go — requires `gofmt` command
- **prettier**: .js, .ts, .html, .css, .json, .yaml — requires prettier in package.json

### 3. Add Workspace Instructions

```jsonc
"instructions": ["~/Developer/AGENTS.md"]
```

Per official docs: "You can configure the instructions for the model you're using through the `instructions` option. This takes an array of paths and glob patterns to instruction files."

### 4. Enable Compaction

```jsonc
"compaction": {
  "auto": true,
  "prune": true,
  "reserved": 4096
}
```

Per official docs: "`auto` - Automatically compact the session when context is full (default: true). `prune` - Remove old tool outputs to save tokens (default: false). `reserved` - Token buffer for compaction."

### 5. Add Watcher Ignores

```jsonc
"watcher": {
  "ignore": ["**/node_modules/**", "**/.git/**", "**/__pycache__/**", "**/.venv/**", "**/dist/**", "**/build/**"]
}
```

Per official docs: "You can configure file watcher ignore patterns through the `watcher` option. Patterns follow glob syntax."

### 6. Disable agentmemory MCP

```jsonc
"agentmemory": {
  "type": "local",
  "command": ["npx", "-y", "@agentmemory/mcp"],
  "environment": {
    "AGENTMEMORY_URL": "http://localhost:3111",
    "AGENT_ID": "opencode"
  },
  "enabled": false
}
```

Server not running (port 3111 unreachable). Disabled to prevent startup noise.

## What Stays Unchanged

- All provider configurations (shopapikey, cockpit, google, zai)
- All agent definitions (explore, oracle, librarian, frontend, docwriter)
- All plugin configurations
- mcp-router MCP server
- Permission and tool settings
- Model assignments

## Verification

After applying changes:
1. `opencode debug config` — verify new sections appear
2. `opencode run 'Hello' --model shopapikey/fable-5` — verify basic functionality
3. Check LSP activates on .py files (pyright diagnostics)
4. Check formatters run on .py files (ruff format)
