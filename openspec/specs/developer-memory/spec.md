# developer-memory Specification

## Purpose
Persistent cross-session memory for AI coding agents. All 7 supported agents
remember platform decisions across sessions, eliminating the first-5-minutes
re-derivation of architectural conventions, past resolutions, and team idioms.

## Requirements

> **Status**: IMPLEMENTED. Agentmemory server installed and wired to Cursor, Claude Code, Codex, OpenCode, pi; Go deps unchanged.

### Requirement: Agentmemory server as developer-memory layer

> **Status**: IMPLEMENTED. Agentmemory server installed; wired to Cursor, Claude Code, Codex, OpenCode, pi.

The project SHALL adopt `rohitg00/agentmemory` (Apache-2.0) as the developer-memory
layer for the microservices monorepo.

#### Scenario: Agentmemory server is installed locally
- **WHEN** a developer runs `make agentmemory-bootstrap && make agentmemory-up`
- **THEN** the server starts on `localhost:3111` (REST+MCP) and
  `localhost:3113` (viewer, loopback-only), with B+ feature flags enabled
- **AND** `make agentmemory-doctor` reports 0 red rows

#### Scenario: Agentmemory is wired to Cursor
- **WHEN** Cursor starts with the agentmemory MCP server configured
- **THEN** the Cursor MCP tool palette shows ≥ 11 agentmemory tools

#### Scenario: Agentmemory is wired to Claude Code
- **WHEN** Claude Code starts with the agentmemory hooks configured
- **THEN** the Claude Code hooks fire on SessionStart, PreToolUse, PostToolUse,
  PreCompact, and Stop events
- **AND** the `memory_smart_search` function returns memories tagged with the
  correct `agentId`

#### Scenario: Agentmemory is wired to Codex CLI
- **WHEN** Codex CLI starts with the agentmemory MCP server configured
- **THEN** Codex CLI hooks fire on SessionStart, UserPromptSubmit, PreToolUse,
  PostToolUse, PreCompact, and Stop
- **AND** Codex Desktop (which ignores plugin-local hooks.json) uses the mirrored
  hooks in `~/.codex/hooks.json` via the `#16430` workaround

#### Scenario: Agentmemory is wired to OpenCode
- **WHEN** OpenCode starts with the agentmemory MCP server configured
- **THEN** the OpenCode tool list includes the agentmemory tools

#### Scenario: Agentmemory is wired to pi
- **WHEN** pi starts with the agentmemory extension installed
- **THEN** the extension registers `memory_health`, `memory_search`, and
  `memory_save` tools
- **AND** the `before_agent_start` hook injects relevant memories into the
  system prompt

### Requirement: No Go service code is modified

> **Status**: IMPLEMENTED. Agentmemory integration is in developer tooling only; Go dependency graph unchanged.

The developer-memory integration SHALL NOT modify any Go service code, package
structure, or dependency graph. The integration is entirely in developer tooling.

#### Scenario: Go dependency graph is unchanged
- **WHEN** `go list -m all` runs against the `platform/` module
- **THEN** no agentmemory package appears in the dependency closure

## Verification

| ID | Capability | Scenario | Tier | Target | Command | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| DM-001 | developer-memory | Agentmemory server is installed locally | e2e | scripts/agentmemory-doctor.sh | bash scripts/agentmemory-doctor.sh | artifacts/verification/doctor.out |
| DM-002 | developer-memory | Agentmemory is wired to Cursor | e2e | .cursor/mcp.json | grep agentmemory ~/.cursor/mcp.json | artifacts/verification/cursor-mcp.out |
| DM-003 | developer-memory | Agentmemory is wired to Claude Code | e2e | .claude/settings.json | grep agentmemory ~/.claude/settings.json | artifacts/verification/claude-code.out |
| DM-004 | developer-memory | Agentmemory is wired to Codex CLI | e2e | .codex/config.toml | grep agentmemory ~/.codex/config.toml | artifacts/verification/codex.out |
| DM-005 | developer-memory | Agentmemory is wired to OpenCode | e2e | .config/opencode/opencode.jsonc | grep agentmemory ~/.config/opencode/opencode.jsonc | artifacts/verification/opencode.out |
| DM-006 | developer-memory | Agentmemory is wired to pi | e2e | .pi/agent/extensions/agentmemory | test -f ~/.pi/agent/extensions/agentmemory/index.js | artifacts/verification/pi.out |
| DM-007 | developer-memory | Go dependency graph is unchanged | unit | go.mod | go list -m all \| grep -i agentmemory | artifacts/verification/go-deps.out |
