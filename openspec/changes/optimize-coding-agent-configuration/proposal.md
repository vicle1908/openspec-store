## Why

A multi-agent review found that the original maximum-capability proposal contained several invalid or counterproductive mutations. The goal remains maximum agentic capability, but the implementation must use the actual installed CLI schemas and preserve generous finite runtime bounds rather than creating unbounded hangs.

## Review Findings Incorporated

- Claude Code `API_TIMEOUT_MS=0`, `MCP_TIMEOUT=0`, and `MCP_TOOL_TIMEOUT=0` are not verified as safe unlimited values; zero may disable the timeout or cause immediate/undefined behavior.
- Removing `ECC_DISABLED_HOOKS` would re-enable suppressed plugin hooks, not remove hooks. Keep the current suppression list unless individual hooks are reviewed.
- Claude Code uses path-scoped `Read(...)` and `Edit(...)` rules; `Write(...)` is not the correct file-edit permission surface. However, `bypassPermissions` already supplies the requested unattended capability, so no global permission rewrite is needed.
- OpenCode official docs validate `permission."*"`, `doom_loop`, and `external_directory`; retain these with explicit semantics.
- The actual Codex config is `~/.codex/config.toml`, not `~/.fable-5.toml`.
- The actual Kimi Code config is `~/.kimi-code/config.toml`, not `~/.fable-5-code/config.toml`. `fable-5` is a configured model/provider name, not the CLI product name.
- Kimi retries should remain at 5 for maximum resilience; reducing them conflicts with the stated goal.
- Pi’s 77 direct MCP tools are the observed source of timeout risk. Proxy mode or a curated direct subset must be evaluated before changing compaction values.
## What Changes

- Claude Code: retain tested generous finite timeouts, retain `ECC_DISABLED_HOOKS`, and document high-turn/high-host-timeout invocation defaults instead of changing global timeout semantics.
- agy: no changes; current headless full-permission invocation is already correct.
- OpenCode: use official global permission syntax, preserve `doom_loop` as an operational guard, and allow the workspace via documented `external_directory` syntax.
- Pi: optimize MCP registration first; preserve full capability through proxy mode or a curated direct tool set. Increase compaction only after measurement.
- Codex: add `approval_policy = "never"` to the actual `~/.codex/config.toml` only after validating config semantics.
- Kimi Code: retain `default_permission_mode = "auto"`, five retries, and current context reserve; use plan mode and larger reserves as explicit task profiles rather than mandatory global defaults.

## Impact

- Agent behavior: maximum normal tool autonomy without invalid settings or accidental hook re-enablement.
- No production impact: user-level configuration and orchestration guidance only.

## Non-Goals

- Credential/security hardening (explicitly excluded by the user).
- Installing or upgrading agents.
- Editing Hermes framework internals.
