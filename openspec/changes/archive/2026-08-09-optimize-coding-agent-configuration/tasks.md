## Review Gate

- [x] 0.1 Preserve the independent review report and official documentation references.
- [x] 0.2 Re-run config-schema checks before any mutation; stop if a proposed field is unsupported.

## Claude Code

- [x] 1.1 Back up `~/.claude/settings.json`.
- [x] 1.2 Verify current `API_TIMEOUT_MS`, `MCP_TIMEOUT`, and `MCP_TOOL_TIMEOUT`; retain generous finite values and do not set them to zero.
- [x] 1.3 Retain `ECC_DISABLED_HOOKS` unless each disabled hook is separately reviewed.
- [x] 1.4 Verify `bypassPermissions` and high-turn invocation behavior with a bounded smoke test; do not rewrite the existing 68-rule permission set.

## Antigravity

- [x] 2.1 Confirm v1.1.11 headless full-permission behavior and model connectivity.
- [x] 2.2 Make no persistent config changes unless a new official setting is verified.

## OpenCode

- [x] 3.1 Back up `~/.config/opencode/opencode.json`.
- [x] 3.2 Preserve existing `edit`, `bash`, and `webfetch` `allow` permissions; add documented `doom_loop: ask` only after schema validation.
- [x] 3.3 Add and schema-check `external_directory` for `/Users/androidteam/Developer/**` using the official mapping form.
- [x] 3.4 Verify in-repository and cross-repository smoke runs, including the external-directory rule.

## Pi

- [x] 4.1 Back up `~/.pi/agent/settings.json` and `~/.pi/agent/mcp.json`.
- [x] 4.2 Inspect the adapter's direct/proxy mode and current 77-tool registration.
- [x] 4.3 Prefer proxy mode or a measured curated direct set while preserving required MCP capability.
- [x] 4.4 Run a full extension-enabled smoke test and confirm the process exits cleanly.
- [x] 4.5 Only if measured context pressure justifies it, increase `reserveTokens` to 32768 and `keepRecentTokens` to 32768; otherwise retain current values.

## Codex

- [x] 5.1 Back up `~/.fable-5.toml`.
- [x] 5.2 Add `approval_policy = "never"` to the actual Codex config and validate it with `codex doctor`.
- [x] 5.3 Verify `danger-full-access` and no-flag smoke execution.

## Kimi Code

- [x] 6.1 Back up `~/.fable-5.toml`.
- [x] 6.2 Preserve `default_permission_mode = "auto"` and `max_attempts_per_step = 5`.
- [x] 6.3 Preserve the current `reserved_context_size = 50000` and `mcp.tool_timeout_ms = 100000` unless measured evidence supports larger finite values.
- [x] 6.4 Validate whether the installed CLI supports named profiles; if not, document plan mode and larger context as invocation-level options rather than inventing config keys.

## Final Validation

- [x] 7.1 Validate the OpenSpec change.
- [x] 7.2 Run real smoke tests for all seven available CLI agents, including Goose.
- [x] 7.3 Verify no credential values or unintended files changed.
- [x] 7.4 Run `git diff --check` and repository status checks.
