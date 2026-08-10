# Proposal: Add Prime Agent Coding CLI Skill

## Why

Prime Agent v0.7.1 is installed and verified with 3 providers (shopapikey, giaoduc, cockpit) and 5 models. No Hermes skill exists to delegate coding tasks to it. The workspace has 11 other skills (including claude-code, codex, pi, opencode, goose, grok, antigravity, kimi-code, hermes-agent, computer-use, opencode-config) following a consistent pattern. Adding `prime-agent` completes the coding-agent surface.

## What Changes

- Create `~/.hermes/skills/autonomous-ai-agents/prime-agent/SKILL.md` following the established coding CLI skill pattern.
- The skill covers: verified local setup, readiness, preferred orchestration (print mode), provider selection, tool/extension/skill configuration, session management, ACP mode, complexity-adaptive limits, verification checklist, and official sources.

## Non-Goals

- No provider configuration changes (covered by archived `prime-agent-three-provider-integration`).
- No source code changes to Prime Agent.
- No OpenSpec spec deltas (`skip_specs: true`).

## Ownership

- **Skill file:** `~/.hermes/skills/autonomous-ai-agents/prime-agent/SKILL.md`
- **Runtime:** `~/.prime/agent/models.json` (already configured, verified)
- **Binary:** `/opt/homebrew/bin/prime-agent` v0.7.1
