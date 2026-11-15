# Spec Delta

## MODIFIED Requirements

### Requirement: Pi Release Hygiene, Package Update Coverage, and Documentation Parity

The `~/.pi/agent/` directory SHALL retain active managed release `1.5.2` (with optional `N-1` previous release `1.5.1` fallback under `~/.pi/agent/install/releases/` and zero stale `.bak*` or orphaned `pi-hermes-memory` directories), `~/.pi/agent/settings.json` SHALL record `"lastChangelogVersion": "1.5.2"`, `workstation-daily-update.sh` SHALL update both Pi core and managed packages via `pi update --all` and truncate `~/.pi-lens/*.log` files exceeding 5 MB (`5242880` bytes), and the Hermes Pi skill and Notion-synced Wiki entity SHALL match the live Pi v1.5.2 configuration (`omniroute-responses/gemini-4-hydrogen` default, `omniroute-responses/gemini-3.8-flash-high` retained fallback).

#### Scenario: Superseded releases, backup files, and orphaned memory directories are absent
- **WHEN** `~/.pi/agent/` is inspected
- **THEN** `~/.pi/agent/install/releases/1.3.0`, `~/.pi/agent/install/releases/1.4.0`, `~/.pi/agent/skills.bak-20261004164935`, `~/.pi/agent/backups`, `~/.pi/agent/models.json.bak*`, `~/.pi/agent/settings.json.bak*`, `~/.pi/agent/memory`, `~/.pi/agent/tdt`, and `~/.pi/agent/projects-memory` SHALL NOT exist
- **AND** `~/.pi/agent/install/current-version` SHALL resolve to `1.5.2` (`releases/1.5.2/`, with at most `N-1` release `1.5.1/` retained) and `~/.pi/agent/settings.json` SHALL set `"lastChangelogVersion": "1.5.2"`
- **AND** `/Users/androidteam/Developer/.agentmemory` SHALL NOT exist

#### Scenario: Workstation daily update script invokes pi update --all and maintains mirror parity
- **WHEN** `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh` are inspected
- **THEN** `AGENT_CLI_COVERED` SHALL specify `pi:Pi:update --all`
- **AND** the script SHALL truncate any `~/.pi-lens/*.log` file whose size exceeds `5242880` bytes (5 MB)
- **AND** both script files SHALL have identical SHA-256 digests

#### Scenario: Hermes Pi orchestration skill and Wiki/Notion documentation reflect Pi v1.4.0
- **WHEN** `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` and `~/Developer/wiki/entities/pi.md` are inspected
- **THEN** both documents SHALL reference Pi `1.5.2`, binary `~/.pi/agent/bin/pi`, active release path `~/.pi/agent/install/releases/1.5.2/` (`wiki/entities/pi.md` explicitly documenting `releases/{1.5.1,1.5.2}/` `N-1` retention and `install/current-version == 1.5.2`), default model `omniroute-responses/gemini-4-hydrogen` (`defaultThinkingLevel: "high"`, with `gemini-3.8-flash-high` retained fallback), and built-in MCP `"exposure": "codemode"`
- **AND** `wiki/entities/pi.md` SHALL be synchronized to Notion page `3efc4b21-deb4-8129-b9c3-d7c22a453212`
