# Delta for Hermes Skills (Alignment Focus)

## ADDED Requirements

### Requirement: Plan Review Skill (Alignment)

The system SHALL provide a plan review skill that orchestrates 5-provider review of OpenSpec change artifacts for alignment across specs, code, documentation, and skills.

#### Scenario: Alignment review after propose

- GIVEN a change with completed artifacts (proposal, specs, design, tasks)
- WHEN the user invokes `/openspec-plan-review {change-name}`
- THEN the skill reads artifacts via `openspec show --json`
- AND reads existing specs, code patterns, docs, and skills for context
- AND spawns 5 parallel review subagents with alignment-focused lenses
- AND each subagent checks alignment across all 4 artifacts
- AND consolidates feedback into `review-plan.md` with alignment matrix
- AND reports summary: aligned edges, drifted edges, recommended fixes

#### Scenario: Provider failure isolation

- GIVEN 5 providers configured for review
- WHEN one provider fails or times out
- THEN the remaining 4 providers complete their reviews
- AND the output includes a note about the failed provider
- AND the alignment matrix is still useful with partial results

#### Scenario: Alignment matrix output

- GIVEN a completed plan review
- WHEN the review finishes
- THEN `review-plan.md` contains alignment matrix showing status of each edge:
  - Spec ↔ Code
  - Code ↔ Docs
  - Docs ↔ Skills
  - Skills ↔ Specs
  - Spec ↔ Docs
  - Code ↔ Skills
- AND includes provider-specific findings for each alignment edge
- AND includes recommended alignment fixes

### Requirement: Code Review Skill (Alignment)

The system SHALL provide a code review skill that orchestrates 5-provider review of implementation code for alignment across specs, code, documentation, and skills.

#### Scenario: Alignment review after apply

- GIVEN a change with implemented code and completed tasks
- WHEN the user invokes `/openspec-code-review {change-name}`
- THEN the skill reads artifacts and git diff
- AND reads existing docs, skills, and specs for context
- AND spawns 5 parallel review subagents with alignment-focused lenses
- AND each subagent checks implementation alignment across all 4 artifacts
- AND consolidates feedback into `review-code.md` with alignment matrix
- AND reports summary: verified alignments, broken alignments, recommended fixes

#### Scenario: Code-specs alignment check

- GIVEN delta specs defining requirements
- WHEN code review runs
- THEN each requirement is checked against the implementation
- AND verified requirements are listed with evidence
- AND gaps (unimplemented or incorrectly implemented) are flagged
- AND extra features not in specs are flagged

#### Scenario: Code-docs alignment check

- GIVEN AGENTS.md and README.md documenting patterns
- WHEN code review runs
- THEN implementation is checked against documented patterns
- AND undocumented behavior changes are flagged
- AND documentation updates needed are listed

#### Scenario: Code-skills alignment check

- GIVEN Hermes skills that reference code APIs
- WHEN code review runs
- THEN skill assumptions are checked against implementation
- AND broken skill imports or outdated commands are flagged
- AND new capabilities that skills should document are identified

#### Scenario: Skills-specs alignment check

- GIVEN skills implementing workflows
- WHEN code review runs
- THEN skill workflows are checked against spec requirements
- AND spec requirements not covered by skills are flagged
- AND skill-spec mismatches are identified

## MODIFIED Requirements

### Requirement: OpenSpec Workflow Integration (Alignment)

The system SHALL support optional multi-provider alignment review gates in the OpenSpec workflow.

#### Scenario: Plan review gate (alignment)

- GIVEN the OpenSpec workflow: propose → apply → verify → archive
- WHEN plan review is invoked after propose
- THEN the workflow becomes: propose → plan-review → apply → verify → archive
- AND plan review checks alignment across specs, code, docs, and skills
- AND plan review does not block implementation (user can skip)

#### Scenario: Code review gate (alignment)

- GIVEN the OpenSpec workflow: propose → apply → verify → archive
- WHEN code review is invoked after apply
- THEN the workflow becomes: propose → apply → code-review → verify → archive
- AND code review checks alignment across specs, code, docs, and skills
- AND code review does not block archiving (user can skip)

#### Scenario: Relationship to /opsx:verify (alignment)

- GIVEN both code-review and /opsx:verify available
- WHEN user runs code-review
- THEN /opsx:verify can still be run afterward
- AND code-review provides deeper 5-provider alignment analysis
- AND /opsx:verify provides quick single-agent alignment check
