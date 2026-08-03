# Delta for Hermes Skills

## ADDED Requirements

### Requirement: Plan Review Skill

The system SHALL provide a plan review skill that orchestrates 5-provider review of OpenSpec change artifacts.

#### Scenario: Review after propose

- GIVEN a change with completed artifacts (proposal, specs, design, tasks)
- WHEN the user invokes `/openspec-plan-review {change-name}`
- THEN the skill reads artifacts via `openspec show --json`
- AND spawns 5 parallel review subagents with specialized lenses
- AND consolidates feedback into `review-plan.md`
- AND reports summary with critical issues, warnings, and suggestions

#### Scenario: Provider failure isolation

- GIVEN 5 providers configured for review
- WHEN one provider fails or times out
- THEN the remaining 4 providers complete their reviews
- AND the output includes a note about the failed provider
- AND the review is still useful with partial results

#### Scenario: Structured output

- GIVEN a completed plan review
- WHEN the review finishes
- THEN `review-plan.md` contains sections for each provider
- AND includes consensus items (flagged by 3+ providers)
- AND includes divergent opinions (where providers disagreed)
- AND includes recommended actions

### Requirement: Code Review Skill

The system SHALL provide a code review skill that orchestrates 5-provider review of implementation code against specs.

#### Scenario: Review after apply

- GIVEN a change with implemented code and completed tasks
- WHEN the user invokes `/openspec-code-review {change-name}`
- THEN the skill reads artifacts and git diff
- AND spawns 5 parallel review subagents with specialized lenses
- AND consolidates feedback into `review-code.md`
- AND reports summary with verified requirements and gaps

#### Scenario: Spec-code alignment check

- GIVEN delta specs defining requirements
- WHEN code review runs
- THEN each requirement is checked against the implementation
- AND verified requirements are listed with evidence
- AND gaps (unimplemented or incorrectly implemented) are flagged

#### Scenario: Test coverage analysis

- GIVEN scenarios in delta specs
- WHEN code review runs
- THEN scenarios with test coverage are identified
- AND scenarios missing coverage are flagged as warnings

## MODIFIED Requirements

### Requirement: OpenSpec Workflow Integration

The system SHALL support optional multi-provider review gates in the OpenSpec workflow.

#### Scenario: Plan review gate

- GIVEN the OpenSpec workflow: propose → apply → verify → archive
- WHEN plan review is invoked after propose
- THEN the workflow becomes: propose → plan-review → apply → verify → archive
- AND plan review does not block implementation (user can skip)

#### Scenario: Code review gate

- GIVEN the OpenSpec workflow: propose → apply → verify → archive
- WHEN code review is invoked after apply
- THEN the workflow becomes: propose → apply → code-review → verify → archive
- AND code review does not block archiving (user can skip)

#### Scenario: Relationship to /opsx:verify

- GIVEN both code-review and /opsx:verify available
- WHEN user runs code-review
- THEN /opsx:verify can still be run afterward
- AND code-review provides deeper 5-provider analysis
- AND /opsx:verify provides quick single-agent validation
