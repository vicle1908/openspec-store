# Spec Delta: pi-agent-harness-config

## MODIFIED Requirements

### Requirement: Subagent Discovery Exclusion Boundaries and Role Routing

The `subagents` configuration in `~/.pi/agent/settings.json` SHALL exclude skill and snapshot directories (`~/.agents/skills`, `~/.agents/.skill-snapshots`, `/Users/androidteam/Developer/.agents/skills`, `/Users/androidteam/Developer/.agents/.skill-snapshots`) via `agentExcludeDirs`, SHALL set `defaultProvider` to `"omniroute-responses"`, `defaultModel` to `"gemini-4-hydrogen"`, and `defaultThinkingLevel` to `"high"`, and SHALL configure role-based `agentOverrides` for `scout`, `researcher`, `reviewer`, `oracle`, and `worker` with explicit `model`, `thinking`, and `"advertise": true` fields while keeping `~/.pi/agent/models.json` untouched and retaining `gemini-3.8-flash-high` in `models.json` and `modelThinkingLevels`.

#### Scenario: Skill snapshots and skill directories are excluded from subagent discovery
- **WHEN** `discoverAgents("/Users/androidteam/Developer", "both")` or `subagent({ action: "list" })` is executed from `/Users/androidteam/Developer`
- **THEN** zero skills or skill snapshots from `.agents/skills` or `.agents/.skill-snapshots` (such as `agent-onboarding`, `bright-data-mcp`, or `ponytail-audit`) SHALL appear as `(project)` subagents
- **AND** all 13 builtin subagents (`claude-code`, `claude-code-writer`, `codex-exec`, `codex-exec-writer`, `cursor-agent`, `cursor-agent-writer`, `delegate`, `evidence-auditor`, `oracle`, `researcher`, `reviewer`, `scout`, `worker`) SHALL remain discoverable and visible in `subagent({ action: "list" })` without shadowing or RTK line stripping

#### Scenario: Subagent role overrides route specialist agents without changing startup defaults
- **WHEN** `subagents` in `~/.pi/agent/settings.json` and `models.json` are inspected
- **THEN** top-level `defaultProvider` and `subagents.defaultProvider` SHALL be `"omniroute-responses"`, top-level `defaultModel` and `subagents.defaultModel` SHALL be `"gemini-4-hydrogen"`, and top-level `defaultThinkingLevel` SHALL be `"high"`
- **AND** `agentOverrides.oracle` SHALL set `"model": "omniroute-responses/gemini-4-argon-high"`, `"thinking": "high"`, and `"advertise": true`
- **AND** `scout` (`"thinking": "medium"`), `researcher` (`"thinking": "high"`), and `worker` (`"thinking": "high"`) SHALL set `"model": "omniroute-responses/gemini-4-hydrogen"`, while `reviewer` (`"thinking": "xhigh"`) SHALL set `"model": "omniroute-responses/gemini-4-hydrogen-xhigh"` directly without modifying `~/.pi/agent/models.json`
- **AND** `modelThinkingLevels` SHALL map `"omniroute-responses/gemini-4-hydrogen"` to `"high"` and `"omniroute-responses/gemini-4-hydrogen-xhigh"` to `"xhigh"`, while `"omniroute-responses/gemini-3.8-flash-high"` remains present in `~/.pi/agent/models.json` and `modelThinkingLevels` as fallback

### Requirement: Pi Release Hygiene, Package Update Coverage, and Documentation Parity

The `~/.pi/agent/` directory SHALL retain only the active managed release (`1.4.0`) without stale `.bak*` or orphaned `pi-hermes-memory` directories, `workstation-daily-update.sh` SHALL update both Pi core and managed packages via `pi update --all` and truncate `~/.pi-lens/*.log` files exceeding 5 MB (`5242880` bytes), and the Hermes Pi skill and Notion-synced Wiki entity SHALL match the live Pi v1.4.0 configuration (`omniroute-responses/gemini-4-hydrogen` default, `omniroute-responses/gemini-3.8-flash-high` retained fallback).

#### Scenario: Superseded releases, backup files, and orphaned memory directories are absent
- **WHEN** `~/.pi/agent/` is inspected
- **THEN** `~/.pi/agent/install/releases/1.3.0`, `~/.pi/agent/skills.bak-20261004164935`, `~/.pi/agent/backups`, `~/.pi/agent/models.json.bak*`, `~/.pi/agent/settings.json.bak*`, `~/.pi/agent/memory`, `~/.pi/agent/tdt`, and `~/.pi/agent/projects-memory` SHALL NOT exist
- **AND** `/Users/androidteam/Developer/.agentmemory` SHALL NOT exist

#### Scenario: Workstation daily update script invokes pi update --all and maintains mirror parity
- **WHEN** `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh` are inspected
- **THEN** `AGENT_CLI_COVERED` SHALL specify `pi:Pi:update --all`
- **AND** the script SHALL truncate any `~/.pi-lens/*.log` file whose size exceeds `5242880` bytes (5 MB)
- **AND** both script files SHALL have identical SHA-256 digests

#### Scenario: Hermes Pi orchestration skill and Wiki/Notion documentation reflect Pi v1.4.0
- **WHEN** `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` and `~/Developer/wiki/entities/pi.md` are inspected
- **THEN** both documents SHALL reference Pi `1.4.0`, binary `~/.pi/agent/bin/pi`, default model `omniroute-responses/gemini-4-hydrogen` (`defaultThinkingLevel: "high"`, with `gemini-3.8-flash-high` retained fallback), and built-in MCP `"exposure": "codemode"`
- **AND** `wiki/entities/pi.md` SHALL be synchronized to Notion page `3efc4b21-deb4-8129-b9c3-d7c22a453212`
