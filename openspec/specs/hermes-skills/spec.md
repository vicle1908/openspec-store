# Hermes Skills

## Purpose

Hermes skills for OpenSpec workflow integration, including multi-provider review capabilities.

## Requirements

### Requirement: Plan Review Skill

The system SHALL provide a plan review skill that orchestrates 5-provider review of OpenSpec change artifacts for alignment across specs, code, documentation, skills, and tests.

#### Scenario: Alignment review after propose

- GIVEN a change with completed artifacts (proposal, specs, design, tasks)
- AND a `review-scope.yaml` defining affected repos, specs, docs, skills
- WHEN the user invokes `/openspec-plan-review {change-name}`
- THEN the skill reads scope from `review-scope.yaml`
- AND validates scope (reject escapes, symlinks, malformed files)
- AND reads change artifacts via `openspec status --change <name> --json`
- AND reads context files from `openspec instructions apply --json`
- AND runs tests and collects coverage (orchestrator responsibility)
- AND runs linting (orchestrator responsibility)
- AND bundles all results as string data
- AND validates no secrets in bundle
- AND spawns 5 parallel review subagents with string data
- AND each subagent checks assigned alignment edges
- AND consolidates feedback into `review-plan.md` with 9-edge alignment matrix
- AND reports summary with ALL statuses: PASS/PARTIAL/FAIL/N/A/UNKNOWN/NOT_REVIEWED

#### Scenario: Trust boundary enforcement

- GIVEN 5 reviewers spawned for review
- WHEN each reviewer executes
- THEN reviewers receive string data only (not file paths)
- AND reviewers are constrained by delegate_task (no write, no shell, no network)
- AND reviewers cannot access credentials or keychains
- AND reviewers cannot spawn nested agents
- AND only the orchestrator writes the final report
- AND orchestrator validates outputs before writing

#### Scenario: Provider failure isolation

- GIVEN 5 providers configured for review
- WHEN one provider fails or times out
- THEN the remaining 4 providers complete their reviews
- AND the failed provider's edges are marked `UNKNOWN` or `NOT_REVIEWED`
- AND the alignment matrix is still useful with partial results
- AND critical findings from other providers are preserved
- AND summary includes counts for ALL statuses

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
  - Knowledge ↔ Code
- AND Security is reported as a lens across all edges (not a separate edge)
- AND each edge has status: PASS, PARTIAL, FAIL, N/A, UNKNOWN, NOT_REVIEWED
- AND each edge has evidence: repository, command, exit code, timestamp, tool version
- AND summary includes counts for ALL statuses
- AND includes provider-specific findings for each alignment edge
- AND includes recommended alignment fixes

#### Scenario: Evidence-based review

- GIVEN a completed plan review
- WHEN the review finishes
- THEN each finding includes supporting evidence
- AND evidence includes repository path, base/head revisions
- AND evidence includes command, working directory, exit code
- AND evidence includes timestamp, tool version
- AND evidence includes output artifact path
- AND evidence includes status: collected, skipped, blocked, unavailable

### Requirement: Code Review Skill

The system SHALL provide a code review skill that orchestrates 5-provider review of implementation code for alignment across specs, code, documentation, skills, and tests.

#### Scenario: Alignment review after apply

- GIVEN a change with implemented code and completed tasks
- AND a `review-scope.yaml` defining affected repos, specs, docs, skills
- WHEN the user invokes `/openspec-code-review {change-name}`
- THEN the skill reads scope from `review-scope.yaml`
- AND validates scope (reject escapes, symlinks, malformed files)
- AND reads change artifacts and git diff
- AND reads existing docs, skills, and specs for context
- AND runs tests and collects coverage (orchestrator responsibility)
- AND runs linting (orchestrator responsibility)
- AND bundles all results as string data
- AND validates no secrets in bundle
- AND spawns 5 parallel review subagents with string data
- AND each subagent checks assigned alignment edges
- AND consolidates feedback into `review-code.md` with 9-edge alignment matrix
- AND reports summary with ALL statuses: PASS/PARTIAL/FAIL/N/A/UNKNOWN/NOT_REVIEWED

#### Scenario: Code-specs alignment check

- GIVEN delta specs defining requirements
- WHEN code review runs
- THEN each requirement is checked against the implementation
- AND verified requirements are listed with evidence
- AND gaps (unimplemented or incorrectly implemented) are flagged as FAIL
- AND extra features not in specs are flagged as FAIL
- AND test coverage for requirements is checked
- AND evidence includes repository, command, exit code, timestamp

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
- AND test execution evidence is collected by orchestrator:
  - Python: `uv run pytest --cov` output
  - Go: `make check-coverage` output
- AND coverage reports are included as evidence
- AND coverage threshold is checked (default 80%)

#### Scenario: Security audit check

- GIVEN the implementation and delta specs
- WHEN code review runs
- THEN Claude Code performs security audit across ALL edges
- AND checks for: auth bypass, data exposure, injection, trust boundaries
- AND security findings are marked FAIL until disproved
- AND security evidence includes file paths, line numbers, threat models
- AND security is reported as a lens, not a separate edge
