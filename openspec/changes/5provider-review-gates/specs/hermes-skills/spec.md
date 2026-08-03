# Delta for Hermes Skills (Alignment Focus) — REVISED

## ADDED Requirements

### Requirement: Plan Review Skill (Alignment, Revised)

The system SHALL provide a plan review skill that orchestrates 5-provider review of OpenSpec change artifacts for alignment across specs, code, documentation, skills, and tests.

#### Scenario: Alignment review after propose

- GIVEN a change with completed artifacts (proposal, specs, design, tasks)
- AND a `review-scope.yaml` defining affected repos, specs, docs, skills
- WHEN the user invokes `/openspec-plan-review {change-name}`
- THEN the skill reads scope from `review-scope.yaml`
- AND reads change artifacts via `openspec status --change <name> --json`
- AND reads context files from `openspec instructions apply --json`
- AND collects sanitized context bundle (allowlisted, redacted)
- AND spawns 5 parallel review subagents with read-only constraints
- AND each subagent checks assigned alignment edges
- AND consolidates feedback into `review-plan.md` with 8-edge alignment matrix
- AND reports summary: PASS/PARTIAL/FAIL per edge with evidence

#### Scenario: Trust boundary enforcement

- GIVEN 5 reviewers spawned for review
- WHEN each reviewer executes
- THEN reviewers are read-only (no write tools, no shell, no network)
- AND reviewers receive sanitized context bundle only
- AND reviewers cannot access credentials or keychains
- AND reviewers cannot spawn nested agents
- AND only the orchestrator writes the final report

#### Scenario: Provider failure isolation

- GIVEN 5 providers configured for review
- WHEN one provider fails or times out
- THEN the remaining 4 providers complete their reviews
- AND the failed provider's edges are marked `UNKNOWN` or `NOT_REVIEWED`
- AND the alignment matrix is still useful with partial results
- AND critical findings from other providers are preserved

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
  - Spec ↔ Tests
  - Code ↔ Tests
  - Security
- AND each edge has status: PASS, PARTIAL, FAIL, N/A, UNKNOWN, NOT_REVIEWED
- AND each edge has evidence: file paths, line numbers, specific findings
- AND includes provider-specific findings for each alignment edge
- AND includes recommended alignment fixes

#### Scenario: Evidence-based review

- GIVEN a completed plan review
- WHEN the review finishes
- THEN each finding includes supporting evidence
- AND evidence includes file paths, line numbers, code snippets
- AND evidence includes spec IDs, requirement text, scenario text
- AND evidence includes doc paths, section references
- AND evidence includes skill paths, command references

### Requirement: Code Review Skill (Alignment, Revised)

The system SHALL provide a code review skill that orchestrates 5-provider review of implementation code for alignment across specs, code, documentation, skills, and tests.

#### Scenario: Alignment review after apply

- GIVEN a change with implemented code and completed tasks
- AND a `review-scope.yaml` defining affected repos, specs, docs, skills
- WHEN the user invokes `/openspec-code-review {change-name}`
- THEN the skill reads scope from `review-scope.yaml`
- AND reads change artifacts and git diff
- AND reads existing docs, skills, and specs for context
- AND collects sanitized context bundle (allowlisted, redacted)
- AND spawns 5 parallel review subagents with read-only constraints
- AND each subagent checks assigned alignment edges
- AND consolidates feedback into `review-code.md` with 8-edge alignment matrix
- AND reports summary: PASS/PARTIAL/FAIL per edge with evidence

#### Scenario: Code-specs alignment check

- GIVEN delta specs defining requirements
- WHEN code review runs
- THEN each requirement is checked against the implementation
- AND verified requirements are listed with evidence
- AND gaps (unimplemented or incorrectly implemented) are flagged as FAIL
- AND extra features not in specs are flagged as FAIL
- AND test coverage for requirements is checked

#### Scenario: Code-docs alignment check

- GIVEN AGENTS.md and README.md documenting patterns
- WHEN code review runs
- THEN implementation is checked against documented patterns
- AND undocumented behavior changes are flagged as FAIL
- AND documentation updates needed are listed
- AND evidence includes doc paths and section references

#### Scenario: Code-skills alignment check

- GIVEN Hermes skills that reference code APIs
- WHEN code review runs
- THEN skill assumptions are checked against implementation
- AND broken skill imports or outdated commands are flagged as FAIL
- AND new capabilities that skills should document are identified
- AND evidence includes skill paths and command references

#### Scenario: Test alignment check

- GIVEN scenarios in delta specs
- WHEN code review runs
- THEN scenarios with test coverage are identified and marked PASS
- AND scenarios missing coverage are marked FAIL
- AND test execution evidence is collected:
  - Python: `uv run pytest --cov` output
  - Go: `make check-coverage` output
- AND coverage reports are included as evidence

#### Scenario: Security audit check

- GIVEN the implementation and delta specs
- WHEN code review runs
- THEN Claude Code performs security audit
- AND checks for: auth bypass, data exposure, injection, trust boundaries
- AND security findings are marked FAIL until disproved
- AND security evidence includes file paths, line numbers, threat models

## MODIFIED Requirements

### Requirement: OpenSpec Workflow Integration (Alignment, Revised)

The system SHALL support optional multi-provider alignment review gates in the OpenSpec workflow.

#### Scenario: Plan review gate (alignment)

- GIVEN the OpenSpec workflow: propose → apply → verify → archive
- WHEN plan review is invoked after propose
- THEN the workflow becomes: propose → plan-review → apply → verify → archive
- AND plan review checks alignment across 8 edges
- AND plan review does not block implementation (user can skip)

#### Scenario: Code review gate (alignment)

- GIVEN the OpenSpec workflow: propose → apply → verify → archive
- WHEN code review is invoked after apply
- THEN the workflow becomes: propose → apply → code-review → verify → archive
- AND code review checks alignment across 8 edges
- AND code review does not block archiving (user can skip)

#### Scenario: Relationship to /opsx:verify (alignment)

- GIVEN both code-review and /opsx:verify available
- WHEN user runs code-review
- THEN /opsx:verify can still be run afterward
- AND code-review provides deeper 5-provider alignment analysis
- AND /opsx:verify provides quick single-agent alignment check
