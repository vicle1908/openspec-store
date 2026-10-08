# Spec Delta

## ADDED Requirements

### Requirement: Diff Hunk Gating for Inline Comments
The AI review engine SHALL attach line-level review discussions strictly to valid lines modified within the merge request's git diff hunks. Any finding targeting an unmodified line or an unrepresented file SHALL NOT be posted as an inline discussion and MUST be aggregated into the top-level merge request summary.

#### Scenario: Line within modified hunk posted inline
- **WHEN** an AI review finding references a line number and file path that falls within an added or modified diff hunk
- **THEN** the review engine SHALL post the finding as an inline discussion at that exact file and line position

#### Scenario: Line outside modified hunk folded into summary
- **WHEN** an AI review finding references an unmodified context line or a file outside the merge request diff
- **THEN** the review engine SHALL omit the inline discussion for that line
- **AND** the finding SHALL be included in the top-level markdown review note as an advisory finding

### Requirement: Discussion Deduplication Across Revisions
The review publisher SHALL prevent duplicate comments across multiple pipeline runs or merge request force-pushes by fingerprinting findings and matching against existing discussions.

#### Scenario: Duplicate finding suppressed on revised MR
- **WHEN** an AI review executes on a new commit of an open merge request
- **AND** an identical finding (matching file, line, and rule code) was already posted in an existing open discussion
- **THEN** the publisher SHALL NOT post a duplicate comment

#### Scenario: Resolved finding recognized
- **WHEN** a previously reported violation is fixed in the latest merge request revision
- **THEN** the review publisher SHALL mark the corresponding discussion thread as resolved

### Requirement: Isolated Git Worktree Execution
Review checkouts, AST parsers, and coverage engines SHALL operate within isolated temporary git worktrees to guarantee zero dirtying of local developer checkouts or persistent CI runner directories.

#### Scenario: Review executed in temporary worktree
- **WHEN** `shb-ai-review` executes a merge request evaluation
- **THEN** it SHALL instantiate an isolated worktree at a temporary path
- **AND** all file evaluations SHALL run against that worktree
- **AND** the worktree SHALL be pruned cleanly upon review completion or error

### Requirement: Standalone MR Review Coverage Scanner CLI
The package SHALL provide an executable command `mr-coverage` that evaluates review coverage across merge request state snapshots, detecting missing, stale, or failed review coverage.

#### Scenario: Full review coverage passes scan
- **WHEN** `mr-coverage scan` is invoked against review state rows where all open merge requests have matching reviewed SHAs and passing review verdicts
- **THEN** the command SHALL emit zero coverage gaps and exit with code 0

#### Scenario: Missing or stale review coverage fails scan
- **WHEN** `mr-coverage scan` detects an MR row with missing review records, commit SHA mismatches, or failed prior reviews
- **THEN** the command SHALL output `CoverageGap` entries identifying each unaddressed MR and exit with non-zero exit code 1

### Requirement: Patch Coverage Calculation and Gating
The `mr-coverage` tool SHALL calculate patch test coverage by evaluating modified executable addition lines in the git diff against Cobertura XML reports. Patch coverage SHALL enforce configured coverage percentage thresholds and fail closed upon missing source files, report tampering, invalid thresholds, or commit provenance mismatches.

#### Scenario: Patch coverage meets or exceeds configured threshold
- **WHEN** `mr-coverage diff` is invoked against git revisions and a Cobertura XML report with coverage meeting or exceeding the threshold
- **THEN** the CLI SHALL emit a passing result and exit with code 0

#### Scenario: Patch coverage fails threshold or measurement error
- **WHEN** `mr-coverage diff` detects coverage below threshold
- **THEN** the CLI SHALL exit with code 1
- **AND WHEN** input files or commit provenance fail validation
- **THEN** the CLI SHALL fail closed and exit with code 2

### Requirement: Configured AI Review Providers Dispatch
The `shb-ai-review` service SHALL support opt-in dispatch to configured AI review providers using structured output models with execution tools disabled. All reviewed diff and code content SHALL be treated as untrusted data, and outbound prompt content SHALL have sensitive credentials redacted prior to dispatch.

#### Scenario: AI review executed with valid provider
- **WHEN** `shb-ai-review review-mr --ai` or `shb-ai-review scan --ai` is invoked with a configured provider
- **THEN** the engine SHALL dispatch structured prompts with tools disabled and integrate generated findings

#### Scenario: Unconfigured AI provider fails closed
- **WHEN** AI review is requested but no provider is configured
- **THEN** the system SHALL fail closed with an error and exit with non-zero code without reporting false approval
