# platform-extensibility Specification (delta)

## Purpose
TBD - to be filled after the change is archived.

## ADDED Requirements

### Requirement: The developer-experience memory layer is an OpenSpec-managed capability
The agentmemory integration (5 capabilities: `developer-memory`, `agentmemory-host-runtime`, `agentmemory-mcp-wiring`, `agentmemory-feature-flags`, `agentmemory-bootstrap-script`) SHALL be treated as first-class OpenSpec capabilities, SHALL be authored in `openspec/changes/<change>/specs/`, and SHALL be archived into `openspec/specs/` per the standard OpenSpec workflow. Any change to the agentmemory contract (tool list, hook payload, env template, MCP wiring, doctor rows) SHALL go through a new OpenSpec change rather than a direct edit to a config file.

#### Scenario: New agentmemory capability goes through OpenSpec
- **WHEN** a developer wants to add a 6th capability (e.g., a `agentmemory-team-share` workflow that shares memories across team members)
- **THEN** they create a new OpenSpec change (e.g., `2026-XX-XX-agentmemory-team-share`) and add a new `specs/<name>/spec.md` rather than editing the existing 5 capability specs in place

#### Scenario: env template is a contract surface
- **WHEN** a developer wants to change a default in `infrastructure/agentmemory.env.template`
- **THEN** the change goes through OpenSpec (e.g., a delta to `agentmemory-feature-flags`) with a corresponding task in `tasks.md` and an entry in `verification/traceability.yaml`

#### Scenario: Makefile target list is a contract surface
- **WHEN** a developer wants to add, remove, or rename a `make agentmemory-*` target
- **THEN** the change goes through OpenSpec (e.g., a delta to `agentmemory-host-runtime` or `agentmemory-bootstrap-script`) and the `help` target's output is updated in the same PR

### Requirement: The agentmemory ADR documents the 5-point admission test
A new ADR SHALL be authored at `docs/adr/0007-developer-memory-layer.md` that documents the 5-point admission test for the developer-experience memory layer, mirroring the format of `order-service/docs/adr/0004-optional-infrastructure.md`. The five points SHALL be: (1) name the problem in one sentence, (2) name the platform-native alternative that was considered and why it was rejected (in this case, "no memory layer" vs "roll our own SQLite + BM25"), (3) name the owner (the platform team, not any individual service), (4) name the integration boundary (the MCP server on `localhost:3111` + per-agent config files at the repo root), and (5) name the failure mode and the compensating control (host process dies → `make agentmemory-up`; OTel-loggable via `~/.agentmemory/log/agentmemory.log`; rollback via `make agentmemory-reset` + revert the agent config PRs).

#### Scenario: ADR is referenced by the architecture test
- **WHEN** the architecture test for vendor-SDK admission runs against the agentmemory integration
- **THEN** it confirms `docs/adr/0007-developer-memory-layer.md` exists with the five required sections, otherwise the build fails with `adr 0007-developer-memory-layer.md: section "<missing-section>" is empty or absent`

#### Scenario: ADR is referenced by the README
- **WHEN** a new developer reads the root `README.md` "Developer Memory" section
- **THEN** the section includes a link to `docs/adr/0007-developer-memory-layer.md` so the architectural decision is discoverable from the entry point
