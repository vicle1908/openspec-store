# workstation-temporal-toolchain Specification

## Purpose

Defines workstation contracts for the official Temporal CLI toolchain and agent skills, establishing local binary availability, non-root development server capabilities, and multi-agent skill discoverability across developer workspaces.

## ADDED Requirements

### Requirement: Workstation Temporal CLI binary availability

The workstation environment SHALL maintain the official `temporal` CLI binary installed at `/opt/homebrew/bin/temporal` and present in the user execution `PATH`. The binary MUST report a semantic version of at least `1.9.1` and support standard non-interactive command execution across developer shells and automated agent runtimes.

#### Scenario: CLI version and runtime identity
- **WHEN** an agent or developer executes `temporal --version`
- **THEN** the command exits with status code 0
- **AND** output contains `temporal version 1.9.1`

### Requirement: Canonical Temporal agent skill distribution

The workspace environment SHALL maintain official `temporal-developer` and `temporal-ops` skill manifests in `~/Developer/.agents/skills/`. The manifests MUST conform to standard Agent Skills frontmatter and remain discoverable across configured agent harnesses without malformed entry markers.

#### Scenario: Temporal skills discoverability across agent harnesses
- **WHEN** `sync-workspace-agent-skills.py --check` executes against the workspace
- **THEN** the script reports zero malformed entries and confirms canonical direct roots include `temporal-developer` and `temporal-ops`
- **AND** the skill entry points resolve strictly to canonical `SKILL.md` files

### Requirement: Local inner-loop development server execution

The workstation Temporal toolchain SHALL support starting a user-scoped, ephemeral local Temporal development server and web UI via `temporal server start-dev`. The development server MUST bind to standard localhost ports without requiring administrative elevation.

#### Scenario: Local development server invocation syntax
- **WHEN** an agent queries development server options via `temporal server start-dev --help`
- **THEN** the command exits with status code 0
- **AND** the help output details port, namespace, and persistence configuration options
