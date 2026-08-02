# Skills Disposition Specification

## Purpose

Define the classification rubric and final disposition for every skill shipped in `ecc@everything-claude-code` v2.0.0 (262 skills). Enable repeatable execution on every future ECC release via the release-audit playbook.

## ADDED Requirements

### Requirement: Every ECC v2.0.0 skill SHALL have exactly one classification

The system SHALL classify every entry in `~/.claude/plugins/cache/everything-claude-code/ecc/<version>/skills/` against the canonical classification enum defined in the design spec.

#### Scenario: Skill classification is exhaustive

- **WHEN** an audit runs against an ECC release
- **THEN** every skill in the release appears exactly once in `audit/skills-disposition.md` with a non-null classification

#### Scenario: Classification enum is closed

- **WHEN** a classifier assigns a value
- **THEN** the value SHALL be one of: `keep-load-bearing`, `keep-optional`, `disabled-default`, `redundant-to-tdt-skill`, `stack-irrelevant`, `domain-irrelevant`, `no-evidence`

### Requirement: Classification MUST be reproducible from declared evidence

The system SHALL record, for each skill, the evidence that drove its classification.

#### Scenario: Every classification row carries evidence

- **WHEN** `audit/skills-disposition.md` is published
- **THEN** each row SHALL have at minimum: `evidence` (description excerpt or usage log reference) and `notes` (rationale)

### Requirement: `redundant-to-tdt-skill` entries MUST cite a real TDT skill path

The system SHALL verify that every skill classified as `redundant-to-tdt-skill:<tdt-skill-name>` references a skill file that exists under `tdt-meta/.agents/skills/<tdt-skill-name>/SKILL.md`.

#### Scenario: TDT skill path is validated

- **WHEN** a row is classified `redundant-to-tdt-skill:foo`
- **THEN** the system SHALL fail-fast if `tdt-meta/.agents/skills/foo/SKILL.md` does not exist

### Requirement: `investigate` entries MUST be resolved before archive

The system SHALL resolve every entry initially marked `investigate` to a final classification before the OpenSpec change can be archived.

#### Scenario: Zero `investigate` rows at archive time

- **WHEN** `/opsx:archive` is invoked on this change
- **THEN** the system SHALL refuse to archive if any row in `audit/skills-disposition.md` is still classified `investigate`

### Requirement: Classification preference order MUST prefer TDT overlay

The system SHALL prefer the TDT overlay over ECC equivalents when both cover the same domain.

#### Scenario: TDT equivalent wins

- **WHEN** a TDT skill at `tdt-meta/.agents/skills/<x>/SKILL.md` exists with overlapping description to an ECC skill `<y>`
- **THEN** ECC skill `<y>` SHALL be classified `redundant-to-tdt-skill:x`, regardless of which was authored first