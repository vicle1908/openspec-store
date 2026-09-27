# shb-review-and-quality Specification

## Purpose
Provides automated merge request code reviews, static code analysis, and test coverage gating for Saigon - Hanoi Bank (SHB) engineering repositories.

## Requirements

### Requirement: Automated Code Review Orchestration
The `shb-ai-review` service SHALL intake code diffs from GitLab merge requests, dispatch them across configured AI review providers, and publish structured evaluation comments.

#### Scenario: Merge request review dispatch
- **WHEN** a webhook or manual trigger targets an open merge request
- **THEN** the review engine extracts the diff, invokes review providers, and posts an aggregated summary back to the merge request

### Requirement: Test Coverage Calculation and Gating
The system SHALL calculate diff coverage metrics for merge requests and enforce compliance against configured minimum coverage thresholds.

#### Scenario: Merge request coverage check
- **WHEN** an MR coverage check command is invoked via `mr-coverage`
- **THEN** the CLI evaluates covered versus uncovered lines and returns a pass or fail exit status

### Requirement: Command-Line Interface Entrypoint
The package SHALL provide executable command-line interfaces named `shb-ai-review` and `mr-coverage` for standalone execution and continuous integration pipelines.

#### Scenario: Standalone code scan execution
- **WHEN** an engineer executes `shb-ai-review scan --repo <path>`
- **THEN** the CLI runs static rules and outputs detected quality findings
