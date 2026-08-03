# Final Provider-Aware CLI Verification

Date: 2026-08-03

## Evidence classifications

- **Verified runtime:** exercised successfully against the currently configured provider/model.
- **Provider-limited:** the CLI exposes the capability, but the configured provider/model did not honor or support it.
- **Surface verified:** current CLI help/configuration exposes the capability, but this pass did not execute its complete runtime behavior.
- **Not configured:** the CLI supports the feature, but no corresponding local configuration exists.

A successful result in this report applies to the installed binary and configured provider/model on the verification date. It is not a universal guarantee for every provider or model.

## Provider and version inventory

### Antigravity

- CLI: `agy 1.1.10`.
- Authentication/provider: Google Antigravity account/session.
- Settings default: human-readable Gemini model alias.
- Automation model pinned for verification: `gemini-3.6-flash-low`, selected from `agy models`.
- Configured MCP server: `mcp-router`.
- Imported plugins: none.
- Custom agents listed: none.

### Claude Code

- CLI: `2.1.212`.
- Installation health: no issues.
- Authentication: active token authentication (`oauth_token`).
- Provider: configured first-party-compatible custom HTTPS endpoint, not `api.anthropic.com`.
- Model: `fable-5[1m]` through the configured endpoint.
- Standalone MCP servers: none configured.
- Native Agent View: live; one idle interactive session observed.
- Remote Control: unavailable because the active endpoint/auth is not Anthropic subscription/API routing.

### Codex

- CLI: `0.146.0`.
- Authentication: active API-key authentication.
- Provider: custom Responses API provider `codex_local_access`, not the default OpenAI endpoint.
- Model: `gpt-5.6-luna`.
- Stable local surfaces include multi-agent, hooks, plugins, browser/computer-use integrations, and unified execution.
- Several MCP servers are configured; inventory output is secret-bearing and was handled without recording inline environment values.

No credential values are included in this evidence.

## Fresh common coding fixture

Three identical committed Git repositories were created under `/tmp/coding-cli-provider-final-20260803`. Each contained an incorrect `clamp()` implementation and four unit tests. Baseline results were identical: two of four tests failed.

Shared instruction: fix only `clamp.py`, preserve the function signature, leave tests/README unchanged, and run `python3 -m unittest -v`.

### Antigravity coding result

- Provider-backed JSON print run: exit `0`, status `SUCCESS`.
- Duration: approximately 9.22 seconds; one turn.
- Independent tests: four of four passed.
- `git diff --check`: passed.
- Tracked scope: one insertion and one deletion in `clamp.py` only.
- Fix: `max(minimum, min(value, maximum))`.
- Classification: **Verified runtime**.

### Claude Code coding result

- Direct settings-owned endpoint invocation: exit `0`, terminal reason `completed`.
- Five turns; no permission denials.
- Duration: approximately 10.59 seconds; reported cost approximately USD 0.040274.
- Independent tests: four of four passed.
- `git diff --check`: passed.
- Tracked scope: one insertion and one deletion in `clamp.py` only.
- Fix: `min(max(value, minimum), maximum)`.
- Classification: **Verified runtime**.

### Codex coding result

- Noninteractive `exec`, custom provider, `approval_policy="never"`, workspace-write sandbox: exit `0`.
- Independent tests: four of four passed.
- `git diff --check`: passed.
- Tracked scope: one insertion and one deletion in `clamp.py` only.
- Fix: `min(max(value, minimum), maximum)`.
- Classification: **Verified runtime**.

The three implementations are behaviorally equivalent. Test-generated `__pycache__` artifacts were disposable and removed with the fixtures.

## Machine-readable output, structured output, and sessions

| Feature | Antigravity | Claude Code | Codex |
|---|---|---|---|
| Noninteractive JSON transport | Verified runtime | Verified runtime | Verified runtime (JSONL) |
| Schema-constrained output | Verified runtime | Provider-limited | Verified runtime |
| Noninteractive session continuation | Verified runtime | Verified runtime | Verified runtime |

Detailed structured/resume evidence was rechecked immediately before this consolidation:

- Antigravity returned schema-valid `structured_output`, resumed by conversation ID, recovered the hidden nonce, and retained prior schema state in the resumed envelope.
- Claude resumed by session ID and recovered the hidden nonce. Its configured endpoint/model ignored `--json-schema` in normal, safe-mode, and legitimate code-analysis probes; it returned no schema-valid `structured_output`.
- Codex returned an exact schema-valid final message and resumed by thread ID. A schema must be supplied again on resumed turns when structured output is required.

## MCP verification

### Antigravity

- Existing `mcp-router/get_usage_stats` was invoked exactly once in stream-JSON mode.
- Tool state reached `DONE`; result status was `SUCCESS`.
- No shell, file, or web tools were requested by the prompt.
- Classification: **Verified runtime**.

### Claude Code

- `claude mcp list` reports no standalone MCP servers configured.
- CLI commands/configuration surface exists, but no runtime server was available for a fair call.
- Classification: **Not configured** (CLI surface verified).

### Codex

- Existing `mcp-router/get_usage_stats` was invoked exactly once through the custom provider.
- MCP event completed successfully and the turn completed.
- A first attempt outside Git was blocked locally until `--skip-git-repo-check` was supplied; this was a trust precondition, not provider/MCP failure.
- `codex mcp list --json` can expose inline environment values. Raw inventory must be redacted before logging or storing.
- Classification: **Verified runtime**.

## Additional feature surfaces

These were verified from current live help/configuration but not fully runtime-exercised in this consolidation:

| Capability | Antigravity | Claude Code | Codex |
|---|---|---|---|
| Interactive TUI | Surface verified | Surface verified | Surface verified |
| Native/custom agents | Surface verified; none configured | Agent View runtime visible; custom/team execution not re-run | Stable multi-agent surface verified; runtime delegation not re-run |
| Plugins | Surface verified; none imported | Configured plugins present; individual plugin behavior not audited | Stable plugins surface and configured plugins present; behavior not audited |
| Hooks | Surface verified | Surface verified | Stable surface verified |
| Worktree automation | No top-level native creation | Surface verified (`--worktree`) | Manual Git worktrees required in CLI |
| Sandbox/permissions | Surface + coding runtime verified | Surface + bounded permissions runtime verified | Surface + workspace-write runtime verified |
| Web/browser | Surface only in this pass | Surface only in this pass | Stable surfaces/configuration present; not exercised here |

No destructive permission, payment, OAuth, remote-control, browser, or experimental feature action was performed.

## Skill reconciliation

- Antigravity skill updated to distinguish settings display aliases from runtime model slugs.
- Claude Code skill updated to attribute exact-output refusal conservatively to the configured provider/model rather than unproven plugin behavior.
- Codex skill updated to identify custom-provider verification limits and to treat raw MCP JSON inventory as secret-bearing.
- Stale guidance scan found no positive claims that print mode requires PTY/tmux, Codex requires Git absolutely, or Antigravity uses invalid legacy paths/model names.

## Final conclusion

All three CLIs are verified for the core Hermes delegation workflow with their current configured providers:

1. noninteractive execution;
2. tool-enabled code modification;
3. independent passing tests and scoped diffs;
4. machine-readable transport;
5. resumable sessions.

Antigravity and Codex additionally pass provider-backed schema-constrained output and configured MCP calls. Claude coding and resume pass, but schema-constrained output is provider-limited and standalone MCP is not configured. Interactive, agent-team, plugin, hook, browser, and other advanced capabilities remain explicitly surface-verified unless stated otherwise.
