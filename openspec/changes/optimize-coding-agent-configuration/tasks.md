## 1. Claude Code Optimization

- [ ] 1.1 Back up current `~/.claude/settings.json` to `~/.claude/settings.json.bak`
- [ ] 1.2 Rewrite permissions: keep `Bash(*)`, `Read(*)`, `Write(*)`, `Edit(*)`, `WebSearch`, remove 68 redundant one-off rules
- [ ] 1.3 Set `API_TIMEOUT_MS=0`, `MCP_TIMEOUT=0`, `MCP_TOOL_TIMEOUT=0` (unlimited)
- [ ] 1.4 Remove `ECC_DISABLED_HOOKS` env var (all hooks already disabled, no need to list them)
- [ ] 1.5 Verify: `claude --version` and `claude auth status --text` still work

## 2. OpenCode Optimization

- [ ] 2.1 Back up current `~/.config/opencode/opencode.json` to `opencode.json.bak`
- [ ] 2.2 Set global `permission: { "*": "allow", "doom_loop": "ask" }`
- [ ] 2.3 Add `external_directory: { "~/Developer/**": "allow" }` for cross-repo access
- [ ] 2.4 Verify: `opencode run 'Reply with OK'` succeeds

## 3. Pi Optimization

- [ ] 3.1 Back up current `~/.pi/agent/settings.json` to `settings.json.bak`
- [ ] 3.2 Increase `compaction.reserveTokens` from 16384 to 32768
- [ ] 3.3 Increase `compaction.keepRecentTokens` from 20000 to 40000
- [ ] 3.4 Verify: `pi -p --no-session --no-tools --provider shopapikey --model fable-5 'Reply with OK'` succeeds

## 4. Codex Optimization

- [ ] 4.1 Back up current `~/.fable-5.toml` to `config.toml.bak`
- [ ] 4.2 Add `approval_policy = "never"` to config.toml
- [ ] 4.3 Verify: `codex exec --sandbox danger-full-access --skip-git-repo-check 'Reply with OK'` succeeds (no `-c` flag needed)

## 5. fable-5 Optimization

- [ ] 5.1 Back up current `~/.fable-5-code/config.toml` to `config.toml.bak`
- [ ] 5.2 Set `default_plan_mode = true`
- [ ] 5.3 Change `max_attempts_per_step` from 5 to 3
- [ ] 5.4 Increase `reserved_context_size` from 50000 to 80000
- [ ] 5.5 Verify: `fable-5 doctor config` passes

## 6. agy — No Changes

- [ ] 6.1 Confirm agy is already at maximum capability (no config changes needed)

## 7. Validation

- [ ] 7.1 Run smoke test on all 6 agents to confirm configs work
- [ ] 7.2 Update Hermes skills with new config details
