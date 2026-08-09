# TDT Config Consumer Alignment

## Why

The SDK consumer path already applied `ModelSettings` behavior defaults, but the
agent-core CLI path only consumed `model.primary` and `model.fallback`. CLI
review/propose/explore runs therefore ignored configured sampling, token,
service-tier, provider-specific, and thinking settings. The settings loader also
retained a legacy `gateway:` YAML fallback after the custom gateway subsystem was
removed.

## What Changes

- Make the CLI use the SDK's canonical model-settings and Thinking capability
  builders.
- Pass configured model settings to `BaseAgent.run(model_settings=...)`.
- Inject configured thinking through the public Thinking capability.
- Remove the legacy `gateway:` YAML fallback; only `model:` is canonical.
- Correct API-mode documentation and consolidate duplicate failover guidance.
- Add focused regression coverage for CLI propagation and clean-break loading.

## Scope

- `agent-core/src/agent_core/cli/utils.py`
- `agent-core/src/agent_core/foundation/settings.py`
- focused agent-core tests and configuration/provider documentation
- canonical `agent-core-model-resolution` specification

## Review Evidence

- Claude Code (`/Users/androidteam/.npm-global/bin/claude`): completed; found
  the CLI propagation gap and otherwise confirmed precedence, `TDT_HOME`, API-mode
  compatibility, and positional `FallbackModel` construction.
- Codex: completed; found the default API-mode documentation ambiguity and
  duplicate failover guidance; both findings were corrected.
- Antigravity: completed a post-fix review with no actionable findings.
- Goose (`/opt/homebrew/bin/goose`): invoked successfully but exhausted its
  action budget before a verdict; recorded as incomplete, not a pass.
- OpenCode: blocked by a read permission refusal; not counted as a review.
