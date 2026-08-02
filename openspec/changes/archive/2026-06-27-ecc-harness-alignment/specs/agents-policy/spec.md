# Agents Policy Specification

## Purpose

Define which ECC agents are surfaced in our installation. Apply a 3-bucket classification (domain reviewers, generic specialists, cross-domain/alpha) with a TDT-domain filter.

## ADDED Requirements

### Requirement: Domain-reviewer agents MUST match repos we actively edit

The system SHALL keep only domain-reviewer agents whose language/framework matches a repo under `~/Developer/tdt/`.

#### Scenario: Domain reviewer keep-list

- **WHEN** an ECC agent has type `domain-reviewer` for language `L`
- **THEN** the agent SHALL be classified `keep-default` iff at least one TDT repo uses language `L`; otherwise `disabled-default:stack-irrelevant`

The current keep-list from this rule:

- `python-reviewer` — `keep-default` (repos: tdt-core, webhook-receiver, ai-review, agent-core, jira-*)
- `swift-reviewer` — `keep-default` (repos: poems-mobile3-ios)
- `kotlin-reviewer` — `keep-default` (repos: poems-mobile3-android)
- `typescript-reviewer` — `keep-default` (frontend work)
- `react-reviewer` — `keep-default` (frontend work)

The current discard-list from this rule:

- `cpp-reviewer`, `csharp-reviewer`, `dart-build-resolver`, `fsharp-reviewer`, `go-build-resolver`, `go-reviewer`, `java-build-resolver`, `java-reviewer`, `php-reviewer`, `rust-build-resolver`, `rust-reviewer` — `disabled-default:stack-irrelevant` until a TDT repo in that language exists.

### Requirement: Generic-specialist agents SHALL all be `keep-default`

The system SHALL keep all agents in the generic-specialist bucket without per-agent review.

#### Scenario: Generic specialist keep-list

- **WHEN** an ECC agent falls into the generic-specialist bucket (cross-cutting concerns)
- **THEN** it SHALL be classified `keep-default`

Generic-specialist bucket (final):

- `architect`, `code-architect`, `code-explorer`, `code-reviewer`, `code-simplifier`, `comment-analyzer`, `conversation-analyzer`, `doc-updater`, `e2e-runner`, `generalPurpose`, `planner`, `pr-test-analyzer`, `refactor-cleaner`, `security-reviewer`, `silent-failure-hunter`, `tdd-guide`, `type-design-analyzer`, `build-error-resolver`

### Requirement: Cross-domain and alpha agents MUST be domain-filtered

The system SHALL classify cross-domain/alpha agents based on whether they match a TDT operating vertical.

#### Scenario: Cross-domain classification

- **WHEN** an ECC agent targets a vertical `V` (e.g., `healthcare`, `homelab`, `network`, `defi`)
- **THEN** the agent SHALL be classified `keep-optional` if TDT operates in `V`; otherwise `disabled-default:domain-irrelevant`

Current decisions from this rule:

- `healthcare-reviewer` — `keep-optional` (POEMS Mobile 3 is a clinical app)
- `homelab-architect`, `network-architect`, `network-config-reviewer`, `network-troubleshooter` — `disabled-default:domain-irrelevant`
- `gan-planner`, `gan-generator`, `gan-evaluator`, `marketing-agent`, `recsys-pipeline-architect`, `prediction-market-*`, `defi-*`, `ito-*` — `disabled-default:domain-irrelevant`

### Requirement: Every agent classification MUST be defensible

The system SHALL record, for each agent, the bucket it belongs to and the rule that drove its classification.

#### Scenario: Audit trail

- **WHEN** `audit/agents-disposition.md` is published
- **THEN** each row SHALL include `bucket` and `rule` columns