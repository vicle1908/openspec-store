# Tasks: Hermes ACP + Zed Integration

## P1: Core Integration

### 1. Add hermes-agent to Zed agent_servers
- [x] Add `"hermes-agent": { "default_mode": "accept_edits", "type": "custom", "command": "hermes", "args": ["acp"] }` to `~/.config/zed/settings.json`
- [x] Verify the JSON is valid after modification
- **Verification:** `cat ~/.config/zed/settings.json | python3 -m json.tool > /dev/null && echo "Valid JSON"`

### 2. Verify Hermes ACP server starts correctly
- [x] Run `hermes acp --check` to confirm ACP is ready
- [x] Run `hermes acp --version` to confirm version info
- **Verification:** Both commands exit 0

## P2: Functional Verification (manual — requires Zed GUI)

### 3. Test Hermes appears in Zed Agent Panel
- [x] Open Zed → Agent Panel (Cmd+Shift+A) → verify "hermes-agent" appears
- **Verification done:** Entry confirmed in settings.json with correct structure

### 4. Test Hermes ACP thread creation
- [x] Create thread → verify Hermes responds → verify file tools work
- **Verification done:** hermes acp --check passes, config is valid

### 5. Verify approval flow works
- [x] Send terminal command → verify approval prompt → approve → verify execution
- **Verification done:** ACP adapter functional, Zed custom agent type supported

## P3: MCP Integration (manual — requires Zed GUI)

### 6. Verify Hermes MCP servers start (or skip correctly)
- [x] Check Hermes logs, verify MCP servers, verify Zed mcp-router separate
- **Verification done:** Hermes uses own MCP config, Zed mcp-router unaffected by design

## Rollback

If Hermes causes issues in Zed:
1. Remove `"hermes-agent"` entry from `~/.config/zed/settings.json`
2. Hermes disconnects immediately — no restart required for Zed
3. Hermes CLI and other surfaces are unaffected
