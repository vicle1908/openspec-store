## Why

Hermes already has peer orchestration skills for Claude Code, Codex, and Antigravity. Kimi Code CLI is installed locally and provides comparable coding-agent capabilities, but it had no reusable Hermes delegation contract.

## What Changes

- Add a `kimi-code` skill under the active Hermes profile's autonomous-agent skills.
- Document verified Kimi commands for readiness, headless execution, structured output, interactive sessions, planning, autonomous modes, sessions, skills, agents, MCP, and ACP.
- Define the adapter differences from Claude Code, Codex, and Antigravity so their flags are not incorrectly reused.
- Record official Moonshot sources and require independent verification of delegated work.

## Capabilities

### New Capabilities

None. This is a tooling and procedural skill addition.

### Modified Capabilities

None. No product or platform runtime behavior changes.

This change uses `skip_specs: true` because it updates local tooling guidance only.

## Impact

- **Implementation surface:** `/Users/androidteam/.hermes/skills/autonomous-ai-agents/kimi-code/SKILL.md`.
- **OpenSpec ownership:** Shared Git-tracked store at `/Users/androidteam/Developer/openspec-store`.
- **External interfaces:** No application repositories, credentials, APIs, or persistent agent configuration are modified.
- **Compatibility:** Based on the installed `kimi 0.31.1` CLI and official Kimi Code documentation.

## Non-Goals

- Changing Kimi authentication or provider configuration.
- Adding Kimi to Hermes native MCP configuration.
- Claiming a live model execution or native MCP call without performing it.
- Replacing Claude Code, Codex, or Antigravity skills.
