## Config Changes

### 1. Claude Code (~/.claude/settings.json)
- Remove 68 redundant Bash allow rules, keep `Bash(*)`
- Add `Read(*)`, `Write(*)`, `Edit(*)`, `WebSearch`
- Set `API_TIMEOUT_MS=0`, `MCP_TIMEOUT=0`, `MCP_TOOL_TIMEOUT=0` (unlimited)
- Remove `ECC_DISABLED_HOOKS` (all hooks disabled)

### 2. agy — No changes
Already at maximum: `--dangerously-skip-permissions`

### 3. OpenCode (~/.config/opencode/opencode.json)
- Set `permission: { "*": "allow", "doom_loop": "ask" }`
- Add `external_directory: { "~/Developer/**": "allow" }`

### 4. Pi (~/.pi/agent/settings.json)
- `compaction.reserveTokens`: 16384 → 32768
- `compaction.keepRecentTokens`: 20000 → 40000

### 5. Codex (~/.fable-5)
- Add `approval_policy = "never"` as default

### 6. fable-5 (~/.fable-5)
- `default_plan_mode`: false → true
- `max_attempts_per_step`: 5 → 3
- `reserved_context_size`: 50000 → 80000

## Risks
- Unlimited timeouts mitigated by Hermes host timeout
- All-permissions-allow acceptable for controlled workspace
- plan_mode default adds planning step for simple tasks
