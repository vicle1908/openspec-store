## Why

Provider configuration currently accepts arbitrary extra arguments, including MCP, plugin, and permission-bypass options, while headless invocations inherit provider customizations that the harness does not control. A read-only flag alone therefore does not establish the documented isolated execution boundary.

## What Changes

- Replace arbitrary provider arguments with typed, provider-specific safe settings or a strict semantic allowlist.
- Make Claude headless execution non-persistent and customization-isolated through bare and safe modes, with explicit authentication and provider-managed-policy boundaries.
- Make Codex headless execution ephemeral and independent of user configuration and execution rules, reject active project configuration for the automated profile, and retain the read-only sandbox.
- Extend capability probing and support-tier classification to require the isolation guarantees used by the selected headless profile.
- Enforce one shared stdout-plus-stderr byte limit instead of one full allowance per stream.
- Preserve guided native-agent helpers, but classify customized headless execution as experimental rather than automated.
- **BREAKING**: Existing `extra_args` values outside the new safe configuration contract will be rejected, custom Claude agent selection will no longer be part of the automated profile, Claude automated execution will require bare-mode-compatible authentication, and Codex projects with active `.codex/config.toml` configuration will be downgraded.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `harness-workflow`: Tighten provider configuration, isolation, subprocess limits, capability probes, and automated support-tier requirements.

## Non-Goals

- Managing provider authentication or credentials.
- Adding providers beyond Claude Code and Codex CLI.
- Granting providers write authority or implementation capability.
- Replacing native CLIs with embedded SDK or agent-framework dependencies.

## Impact

- Repository: `ai-harness-skills`.
- Primary modules: typed configuration, Claude/Codex adapters, shared process runner, provider capabilities, doctor diagnostics, and provider tests/documentation.
- GitNexus reports CRITICAL upstream impact for `validate_config` (14 symbols and 15 execution processes), MEDIUM impact for `SafeProcessRunner.run`, and broad provider/CLI integration coverage.
- Installed Claude Code and Codex CLI versions must expose the required isolation flags or be downgraded from `automated`.
- No new external dependency is required.
