## Why

Pi coding agent (pi.dev) is a minimal, extensible terminal coding harness by Mario Zechner (earendil-works). It is installed locally at v0.83.0 with 15+ provider support, four built-in tools (read, write, edit, bash), and an extension/skill/theming system. Existing Hermes coding-agent skills cover Antigravity, Claude Code, and Codex but lack a Pi equivalent. Adding a `pi` skill enables Hermes to delegate bounded coding tasks to Pi in non-interactive print mode, matching the established orchestration pattern.

## What Changes

- Create a new Hermes skill at `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` modeled on the Claude Code and Codex skills.
- Document Pi's non-interactive orchestration contract: `pi -p` print mode, provider/model selection, tool scoping, session management, JSON output, thinking levels, and extension loading.
- Encode complexity-adaptive host-timeout bounds since Pi lacks a native `--max-turns` flag.
- Document Pi's intentional omissions (no built-in MCP, sub-agents, plan mode, permission popups) and extension-based alternatives.
- Record verified Pi v0.83.0 CLI behavior as the evidence baseline.

## Capabilities

### New Capabilities

- Hermes can delegate bounded coding tasks to Pi via `pi -p` non-interactive mode.
- Pi can be used as an alternative orchestration target alongside Antigravity, Claude Code, and Codex.

### Modified Capabilities

None. No existing skill, platform behavior, or shared configuration changes.

The change opts out of delta specs with `skip_specs: true`.

## Impact

- **Ownership boundary:** Active Hermes profile skill content under `~/.hermes/skills/autonomous-ai-agents/pi/`.
- **OpenSpec ownership:** Shared, Git-tracked store at `~/Developer/openspec-store` records the completed change.
- **External interfaces:** No CLI configuration, credentials, repositories, APIs, or product code are modified.
- **Compatibility:** Guidance is version-qualified for local Pi v0.83.0; installed help remains authoritative.

## Non-Goals

- Modifying Pi installation, credentials, or provider configuration.
- Enabling dangerous permission bypass globally.
- Adding a product capability spec for procedural skill documentation.
- Modifying application repositories.
