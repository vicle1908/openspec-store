# Tasks: Hermes ACP + Zed Integration

## P1: Core Integration

### 1. Add hermes-agent to Zed agent_servers
- Add `"hermes-agent": { "type": "custom", "command": "hermes", "args": ["acp"] }` to `~/.config/zed/settings.json`
- Verify the JSON is valid after modification
- **Verification:** `cat ~/.config/zed/settings.json | python3 -m json.tool > /dev/null && echo "Valid JSON"`

### 2. Verify Hermes ACP server starts correctly
- Run `hermes acp --check` to confirm ACP is ready
- Run `hermes acp --version` to confirm version info
- **Verification:** Both commands exit 0

## P2: Functional Verification

### 3. Test Hermes appears in Zed Agent Panel
- Open Zed
- Open Agent Panel (Cmd+Shift+A)
- Verify "hermes-agent" appears in the agent selector/new-thread menu
- **Verification:** Hermes is listed as a selectable agent

### 4. Test Hermes ACP thread creation
- Create a new thread with Hermes agent in Zed
- Verify Hermes responds to a test prompt
- Verify file tools operate on the project directory
- **Verification:** Hermes processes the prompt and returns a response

### 5. Verify approval flow works
- Send a terminal command (e.g., `git status`) through Hermes in Zed
- Verify the approval prompt appears in Zed
- Approve and verify the command executes
- **Verification:** Terminal command routes through Zed approval UI

## P3: MCP Integration

### 6. Verify Hermes MCP servers start (or skip correctly)
- Check Hermes logs (stderr) when starting an ACP thread
- Verify MCP servers from Hermes config are started (unless skipped)
- Verify Zed's own mcp-router remains separate
- **Verification:** Hermes MCP tools appear in the ACP session (or are absent if intentionally skipped)

## Rollback

If Hermes causes issues in Zed:
1. Remove `"hermes-agent"` entry from `~/.config/zed/settings.json`
2. Hermes disconnects immediately — no restart required for Zed
3. Hermes CLI and other surfaces are unaffected
