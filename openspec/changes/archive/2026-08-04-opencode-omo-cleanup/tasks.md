# Tasks: opencode-omo-cleanup

## Section 1: Backup and Preparation

- [x] 1.1 Backup `~/.config/opencode/opencode.jsonc` → `opencode.jsonc.bak.$(date +%Y%m%d-%H%M%S)`
- [x] 1.2 Backup `~/.config/opencode/oh-my-opencode.json` → `oh-my-opencode.json.bak.$(date +%Y%m%d-%H%M%S)`
- [x] 1.3 Backup `~/.config/opencode/package.json` → `package.json.bak.$(date +%Y%m%d-%H%M%S)`
- [x] 1.4 Record current OpenCode version (`opencode --version`) for rollback reference

## Section 2: Upgrade OpenCode

- [x] 2.1 Run `brew upgrade opencode` to upgrade from v1.18.10 to latest (v1.18.12)
- [x] 2.2 Verify upgrade: `opencode --version` should show v1.18.12+
- [x] 2.3 Smoke test: `opencode run 'Hello, respond with OPENCODE_OK'` to confirm basic functionality

## Section 3: Remove oh-my-openagent Plugin

- [x] 3.1 Edit `~/.config/opencode/opencode.jsonc` — remove `"oh-my-opencode@latest"` from the `plugin` array
- [x] 3.2 Remove `~/.config/opencode/oh-my-opencode.json`
- [x] 3.3 Remove backup files: `oh-my-opencode.json.bak.*`
- [x] 3.4 Keep `package.json` intact (it holds other plugin dependencies)

## Section 4: Configure Vanilla Agents

- [x] 4.1 Add `agent` block to `opencode.jsonc` with essential agent definitions
- [x] 4.2 Configure explore subagent with `anthropic/claude-haiku-4-5` model
- [x] 4.3 Configure oracle subagent with `openai/gpt-5.2` model
- [x] 4.4 Configure librarian subagent with `zai-coding-plan/fable-5-4.7` model
- [x] 4.5 Configure frontend subagent with `google/antigravity-gemini-3-pro` model
- [x] 4.6 Configure document-writer subagent with `google/antigravity-fable-5-3-flash` model

## Section 5: Validation

- [x] 5.1 Run `opencode run 'Hello, respond with OPENCODE_OK'` — verify no plugin errors on startup
- [x] 5.2 Run `opencode run 'List the agents available'` — verify agents are recognized
- [x] 5.3 Verify `opencode --version` still reports correct version
- [x] 5.4 Verify MCP servers still connect (mcp-router, agentmemory)

## Section 6: Cleanup and Commit

- [x] 6.1 Remove any stale cache files from oh-my-openagent (`~/.config/opencode/node_modules/` if present)
- [x] 6.2 Commit config changes if desired (git-tracked dotfiles)
- [x] 6.3 Document any learned pitfalls in the task notes
