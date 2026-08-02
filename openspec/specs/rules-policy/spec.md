# rules-policy Specification

## Purpose
TBD - created by archiving change ecc-harness-alignment. Update Purpose after archive.
## Requirements
### Requirement: Only language rule dirs matching TDT repos SHALL be surfaced

The system SHALL surface only language rule dirs whose language matches at least one repo under `~/Developer/tdt/`.

#### Scenario: Language match rule

- **WHEN** an ECC rule dir `rules/<L>/` exists for language `L`
- **THEN** it SHALL be classified `surface` iff at least one TDT repo uses language `L`; otherwise `disabled-default:stack-irrelevant`

Initial surface list from this rule:

- `rules/python/` — `surface` (tdt-core, webhook-receiver, ai-review, agent-core, jira-*)
- `rules/swift/` — `surface` (poems-mobile3-ios)
- `rules/kotlin/` — `surface` (poems-mobile3-android)
- `rules/typescript/` — `surface` (web frontend if any)
- `rules/react/` — `surface` (web frontend if any)

Initial discard list from this rule:

- `rules/cpp/`, `rules/csharp/`, `rules/dart/`, `rules/fsharp/`, `rules/golang/`, `rules/java/`, `rules/perl/`, `rules/php/`, `rules/ruby/`, `rules/rust/`, `rules/arkts/`, `rules/angular/`, `rules/web/` — `disabled-default:stack-irrelevant` until a TDT repo in that language exists

### Requirement: `rules/common/` SHALL be evaluated independently

The system SHALL classify `rules/common/` based on whether its contents are globally useful regardless of language.

#### Scenario: Common rules evaluation

- **WHEN** `rules/common/` contains rules that apply to any language
- **THEN** it SHALL be classified `surface`; otherwise `disabled-default:no-applicable-content`

### Requirement: New language repos SHALL trigger a rules-policy update

The system SHALL update `audit/rules-policy.md` whenever a new language repo is added under `~/Developer/tdt/`.

#### Scenario: New-language trigger

- **WHEN** a new TDT repo with primary language `L` is created
- **THEN** the system SHALL re-evaluate `rules/<L>/` for `surface` classification within the same change

