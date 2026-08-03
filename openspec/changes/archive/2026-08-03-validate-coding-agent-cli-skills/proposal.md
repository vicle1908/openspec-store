## Why

The Hermes coding-agent orchestration skills contained stale and contradictory CLI contracts that could misroute files, weaken automation controls, or fail unattended execution. The installed Antigravity, Claude Code, and Codex versions and their current official documentation now provide enough evidence to replace those assumptions with validated invocation and verification guidance.

## What Changes

- Audit official Google, Anthropic, and OpenAI CLI documentation against the locally installed binaries.
- Correct the Hermes Antigravity skill for model identifiers, process-CWD versus logical-project semantics, headless output, permissions, sandboxing, subagents, MCP, and plugin behavior.
- Correct the Hermes Claude Code skill for print-mode permissions, tool visibility versus authorization, bare mode, sessions, native background agents, worktrees, hooks, MCP storage, subagents, and agent teams.
- Correct the Hermes Codex skill for noninteractive execution, approval policy versus sandboxing, non-Git operation, JSONL and structured output, resumable execution, review, plugins, hooks, MCP, subagents, and manual CLI worktrees.
- Add externally verifiable invocation patterns and require independent file, diff, and test checks before accepting an agent self-report.
- Remove or replace false claims such as mandatory tmux/PTY for headless commands, invalid Antigravity model/display names and settings paths, fixed dialog key sequences, and Codex's former Git-only limitation.

## Capabilities

### New Capabilities

None. This is a tooling and documentation correction for local Hermes skills.

### Modified Capabilities

None. No runtime product requirement or shared platform behavior changes.

The change opts out of delta specs with `skip_specs: true`.

## Impact

- **Ownership boundary:** Active Hermes profile skill content under `~/.hermes/skills/autonomous-ai-agents/{antigravity,claude-code,codex}`.
- **OpenSpec ownership:** Shared, Git-tracked store at `~/Developer/openspec-store` records the completed change and verification evidence.
- **External interfaces:** No CLI configuration, credentials, repositories, APIs, or product code are modified.
- **Compatibility:** Guidance is version-qualified for local `agy 1.1.10`, `claude 2.1.212`, and `codex-cli 0.146.0`; installed help remains authoritative when documentation and binaries diverge.

## Non-Goals

- Changing Antigravity, Claude Code, or Codex account configuration or credentials.
- Enabling dangerous permission bypass globally.
- Adding a product capability spec for documentation-only skill maintenance.
- Modifying application repositories or their dependency graphs.
