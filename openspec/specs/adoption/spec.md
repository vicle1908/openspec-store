# adoption Specification

## Purpose
TBD - created by archiving change ecc-harness-alignment. Update Purpose after archive.
## Requirements
### Requirement: Each adopted v2.0 feature SHALL have an integration plan

The system SHALL record, for each adopted feature, the integration plan.

#### Scenario: Integration plan completeness

- **WHEN** a feature is classified `adopted`
- **THEN** `audit/adoption.md` SHALL include: target location, TDT-skill or TDT-command it pairs with, what it must NOT shadow, and a one-paragraph "how to invoke" example

### Requirement: Candidate v2.0 features SHALL be evaluated against the TDT overlay

The system SHALL evaluate each candidate feature against the question "does TDT have an equivalent that already covers this?"

#### Scenario: Pre-adoption check

- **WHEN** an ECC feature is under consideration
- **THEN** the system SHALL first check `tdt-meta/.agents/skills/` and `tdt-meta/.agents/commands/` (when present) for an equivalent; if found, classify `redundant-to-tdt-skill` and skip

### Requirement: Orchestrator-family skills SHALL have explicit adoption status

The system SHALL classify every `orch-*` skill as either `adopted` (with integration plan in `audit/adoption.md`) or `keep-optional` (installed but not in active use).

#### Scenario: Orchestrator adoption states

- **WHEN** an `orch-*` skill is under consideration
- **THEN** it SHALL be classified `adopted` only if `audit/adoption.md` lists an integration plan pairing it with an OpenSpec workflow; otherwise `keep-optional`

### Requirement: `continuous-learning-v2` SHALL NOT shadow `agentmemory`

The system SHALL reject adoption of `continuous-learning-v2` if it would write to the same store as the agentmemory plugin.

#### Scenario: Store-conflict detection

- **WHEN** `continuous-learning-v2` writes to `~/.agentmemory/` or `~/.claude/session-data/`
- **THEN** the system SHALL classify it `redundant-to-tdt-skill:agentmemory` and not adopt

### Requirement: `healthcare-reviewer` adoption SHALL be domain-bounded

The system SHALL adopt `healthcare-reviewer` only if it is invoked against the clinical mobile app repos (`poems-mobile3-ios`, `poems-mobile3-android`).

#### Scenario: Healthcare reviewer scope

- **WHEN** `healthcare-reviewer` is invoked against a non-clinical repo
- **THEN** the system SHALL log the out-of-scope invocation and recommend the generic `code-reviewer` instead

### Requirement: `hookify-rules` adoption SHALL NOT shadow the installed `hookify` plugin

The system SHALL adopt `hookify-rules` only as a documentation/reference surface; rule authoring SHALL continue to use `hookify@claude-plugins-official`.

#### Scenario: Hookify scope separation

- **WHEN** a user invokes `hookify-rules` for rule authoring
- **THEN** the system SHALL redirect them to `hookify@claude-plugins-official`'s `hookify` command

### Requirement: Adoption list SHALL be auditable per release

The system SHALL append each new candidate feature to `audit/adoption.md` with its evaluation date and outcome.

#### Scenario: Audit trail

- **WHEN** a candidate is evaluated
- **THEN** `audit/adoption.md` SHALL record the candidate's name, evaluation date, decision (`adopted`/`redundant-to-tdt-skill`/`deferred`/`rejected`), and rationale

