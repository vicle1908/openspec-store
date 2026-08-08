## Review Gate

- [ ] 0.1 Preserve the independent review report and official documentation references.
- [ ] 0.2 Re-run config-schema checks before any mutation; stop if a proposed field is unsupported.

## Claude Code

- [ ] 1.1 Back up `~/.claude/settings.json`.
- [ ] 1.2 Verify current `API_TIMEOUT_MS`, `MCP_TIMEOUT`, and `MCP_TOOL_TIMEOUT`; retain generous finite values and do not set them to zero.
- [ ] 1.3 Retain `ECC_DISABLED_HOOKS` unless each disabled hook is separately reviewed.
- [ ] 1.4 Verify `bypassPermissions` and high-turn invocation behavior with a bounded smoke test; do not rewrite the existing 68-rule permission set.

## Antigravity

- [ ] 2.1 Confirm v1.1.11 headless full-permission behavior and model connectivity.
- [ ] 2.2 Make no persistent config changes unless a new official setting is verified.

## OpenCode

- [ ] 3.1 Back up `~/.config/opencode/opencode.json`.
- [ ] 3.2 Preserve existing `edit`, `bash`, and `webfetch` `allow` permissions; add documented `doom_loop: ask` only after schema validation.
- [ ] 3.3 Add and schema-check `external_directory` for `/Users/androidteam/Developer/**` using the official mapping form.
- [ ] 3.4 Verify in-repository and cross-repository smoke runs, including the external-directory rule.
## Pi

- [ ] 4.1 Back up `~/.pi/agent/settings.json` and `~/.pi/agent/mcp.json`.
- [ ] 4.2 Inspect the adapter’s direct/proxy mode and current 77-tool registration.
- [ ] 4.3 Prefer proxy mode or a measured curated direct set while preserving required MCP capability.
- [ ] 4.4 Run a full extension-enabled smoke test and confirm the process exits cleanly.
- [ ] 4.5 Only if measured context pressure justifies it, increase `reserveTokens` to 32768 and `keepRecentTokens` to 32768; otherwise retain current values.

## Codex

- [ ] 5.1 Back up `~/.codex/config.toml`.
- [ ] 5.2 Add `approval_policy = "never"` to the actual Codex config and validate it with `codex doctor`.
- [ ] 5.3 Verify `danger-full-access` and no-flag smoke execution.

## Kimi Code

- [ ] 6.1 Back up `~/.kimi-code/config.toml`.
- [ ] 6.2 Preserve `default_permission_mode = "auto"` and `max_attempts_per_step = 5`.
- [ ] 6.3 Preserve the current `reserved_context_size = 50000` and `mcp.tool_timeout_ms = 100000` unless measured evidence supports larger finite values.
- [ ] 6.4 Validate whether the installed CLI supports named profiles; if not, document plan mode and larger context as invocation-level options rather than inventing config keys.

## Final Validation

- [ ] 7.1 Validate the OpenSpec change.
- [ ] 7.2 Run real smoke tests for all seven available CLI agents, including Goose.
- [ ] 7.3 Verify no credential values or unintended files changed.
- [ ] 7.4 Run `git diff --check` and repository status checks.
