# shb-agent-skills Specification

## Purpose
Establishes a unified catalog of specialized autonomous agent skills, architectural audit routines, and banking compliance guidelines for the Saigon - Hanoi Bank (SHB) agent ecosystem.

## Requirements

### Requirement: Canonical Agent Skills Catalog
The `shb-agent-skills` repository SHALL provide a discoverable catalog of prompt-based skills, operational runbooks, and architectural evaluators formatted according to the standard skill definition contract with YAML frontmatter.

#### Scenario: Agent loads engineering skill
- **WHEN** an autonomous coding agent requests the hexagonal architecture or code review skill
- **THEN** the skill system resolves the canonical `SKILL.md` from `shb-agent-skills` and injects its procedural guidance into the agent context

### Requirement: Architectural and Code Quality Verification Routines
The system SHALL provide executable verification routines that inspect codebases for clean architecture compliance, circular dependencies, and database migration safety.

#### Scenario: Hexagonal compliance check
- **WHEN** the architectural audit skill evaluates a service codebase
- **THEN** it inspects import boundaries and flags any direct leakage of concrete adapters into domain models

### Requirement: Banking Domain Prompt and Policy Guidelines
The skills catalog SHALL incorporate banking data safety policies, PCI-DSS compliance checkpoints, and sanitized fixture generators for secure banking agent development.

#### Scenario: Sensitive data handling verification
- **WHEN** a skill evaluates banking code diffs containing API payloads
- **THEN** it verifies that PAN numbers, CVV codes, and customer passwords are masked and never persisted in plain text
