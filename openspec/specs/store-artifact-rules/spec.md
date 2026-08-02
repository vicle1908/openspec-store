# store-artifact-rules Specification

## Purpose
Defines per-artifact rules in `openspec/config.yaml` that enforce quality
constraints on AI-generated proposals, specs, designs, and tasks.
## Requirements
### Requirement: config.yaml SHALL include a rules section with per-artifact constraints

The store's `openspec/config.yaml` SHALL include a `rules` block with entries
for at least `proposal`, `specs`, `design`, and `tasks` artifacts.

#### Scenario: Proposal rules enforce scope clarity

- **GIVEN** `config.yaml` contains `rules.proposal`
- **WHEN** a proposal is generated via `/opsx:propose`
- **THEN** the generated proposal SHALL include a one-sentence problem statement, explicit non-goals, and affected ownership boundaries

#### Scenario: Spec rules enforce requirement quality

- **GIVEN** `config.yaml` contains `rules.specs`
- **WHEN** delta specs are generated
- **THEN** every requirement SHALL use SHALL/MUST keywords and include at least one GIVEN/WHEN/THEN scenario

#### Scenario: Design rules enforce pattern reuse

- **GIVEN** `config.yaml` contains `rules.design`
- **WHEN** a design document is generated
- **THEN** the design SHALL reference existing patterns before proposing new ones

#### Scenario: Task rules enforce verifiability

- **GIVEN** `config.yaml` contains `rules.tasks`
- **WHEN** a task list is generated
- **THEN** tasks SHALL use hierarchical numbering and each implementation task SHALL have a corresponding verification step

