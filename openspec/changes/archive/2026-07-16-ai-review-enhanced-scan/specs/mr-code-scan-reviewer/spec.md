# mr-code-scan-reviewer Specification

## Purpose

Define how code-daily-scan integrates into the ai-review MR pipeline as a reviewer.

## ADDED Requirements

### Requirement: CodeScanReviewer SHALL be configurable via ENABLE_CODE_SCAN env var

The `ENABLE_CODE_SCAN` environment variable SHALL control whether the code scan reviewer
is active. When unset or set to `true`, the reviewer SHALL be included in the run plan.
When set to `false`, the reviewer SHALL be excluded.

The two-tier fallback pattern SHALL be used: `AI_REVIEW_ENABLE_CODESCAN` takes precedence,
with `ENABLE_CODE_SCAN` as fallback (default: `true`).

#### Scenario: Code scan is enabled by default

- **WHEN** `ENABLE_CODE_SCAN` is not set or set to `true`
- **THEN** `CodeScanReviewer` SHALL be instantiated and added to the reviewer run plan
- **AND** the reviewer SHALL execute alongside LLM reviewers

#### Scenario: Code scan is disabled via env var

- **WHEN** `ENABLE_CODE_SCAN` is set to `false`
- **THEN** `CodeScanReviewer` SHALL NOT be added to the reviewer run plan
- **AND** LLM reviewers SHALL continue without code scan

### Requirement: CodeScanReviewer SHALL invoke MrScanOrchestrator with MR context

The reviewer SHALL invoke `code_daily_scan.orchestrator_mr.MrScanOrchestrator` with parameters
derived from the review context: `repo_path`, `changed_files`, `platform`, and `source_branch`.

For ai-review integration, `MrScanOrchestrator` SHALL reuse the exact-SHA worktree prepared by `ReviewContextResolver`; standalone callers MAY continue to use its internal `WorktreeManager` lifecycle.

#### Scenario: Scan executes successfully

- **WHEN** `CodeScanReviewer.review()` is called with valid MR context
- **THEN** it SHALL create `MrScanOrchestrator` with:
  - `repo_path`: Path to the local repo (from `ReviewContext.repo_path` or `local_repo_paths`)
  - `changed_files`: Set of changed file paths from `ReviewContext.changed_files`
  - `platform`: "android" or "ios" (derived from project ID or repo path)
  - `source_branch`: Branch name from `ReviewContext.source_branch`
- **AND** it SHALL invoke `orchestrator.run()` and receive `(findings, phase3_report)`
- **AND** findings SHALL be serialized to markdown and posted to the GitLab MR

#### Scenario: Verified scan finds no issues

- **WHEN** `MrScanOrchestrator` completes with no findings
- **AND** the scan execution report proves the checkout matches the reviewed commit SHA
- **AND** at least one supported, existing changed file was scanned
- **AND** at least one rule was loaded
- **AND** the execution report contains no degradation reasons
- **THEN** `CodeScanReviewer` SHALL return a `ReviewResult` with `status=COMPLETED` and output "No code scan issues found"
- **AND** it SHALL post a comment indicating "No code scan issues found"

#### Scenario: MR has no changed files

- **WHEN** the review context contains no changed files
- **THEN** `CodeScanReviewer` SHALL publish an informational skipped result
- **AND** it SHALL NOT claim that no code scan issues were found

#### Scenario: No changed file is eligible for platform scanning

- **WHEN** changed files exist but none have an extension supported by the selected platform plugin
- **THEN** `CodeScanReviewer` SHALL publish an informational skipped result that identifies the unsupported file count
- **AND** it SHALL NOT claim that no code scan issues were found

#### Scenario: Eligible changed files are absent from the checkout

- **WHEN** one or more extension-eligible changed files do not exist in the scan checkout
- **THEN** the scan execution report SHALL identify those files and the reason they were skipped
- **AND** `CodeScanReviewer` SHALL publish a degraded result when at least one eligible file remains scannable
- **OR** a failed result when no eligible file can be scanned
- **AND** it SHALL NOT publish a clean result

#### Scenario: No rules are loaded

- **WHEN** the scanner loads zero rules across all configured categories
- **THEN** `CodeScanReviewer` SHALL return `status=FAILED`
- **AND** it SHALL publish an error result instead of "No code scan issues found"

### Requirement: CodeScanReviewer SHALL scan the reviewed commit revision

The review context SHALL propagate the prepared `worktree_path` and reviewed `commit_sha` through the metadata sidecar. Before scanning, `CodeScanReviewer` SHALL verify that the scan checkout exists and its Git `HEAD` resolves to the reviewed commit SHA.

#### Scenario: Prepared worktree matches reviewed revision

- **WHEN** the metadata sidecar includes a prepared worktree path and commit SHA
- **AND** the worktree `HEAD` equals that commit SHA
- **THEN** `CodeScanReviewer` SHALL invoke `MrScanOrchestrator` against that worktree
- **AND** it SHALL include the verified revision in structured logs

#### Scenario: Prepared worktree does not match reviewed revision

- **WHEN** the worktree `HEAD` does not equal the reviewed commit SHA
- **THEN** `CodeScanReviewer` SHALL NOT invoke the scanner against that checkout
- **AND** it SHALL return `status=FAILED`
- **AND** it SHALL post an error comment that does not claim the MR is clean

#### Scenario: Exact revision metadata is unavailable

- **WHEN** `worktree_path` or `commit_sha` is absent from the metadata sidecar
- **THEN** `CodeScanReviewer` SHALL return `status=FAILED`
- **AND** it SHALL log which required field is missing
- **AND** it SHALL NOT silently fall back to the long-lived repository checkout

### Requirement: MR scan execution SHALL return structured evidence

`MrScanOrchestrator` SHALL return structured execution evidence in its report so callers can distinguish a meaningful zero-finding scan from a scan that did not evaluate eligible code.

#### Scenario: Execution report records scan scope

- **WHEN** an MR scan completes
- **THEN** its report SHALL include requested changed-file count, extension-eligible file count, existing eligible file count, scanned file count, loaded-rule count, findings before Phase 3, and findings after Phase 3
- **AND** counts SHALL be suitable for structured logging and automated assertions

#### Scenario: Files are skipped

- **WHEN** requested changed files are unsupported, excluded, test-only, or missing from the checkout
- **THEN** the report SHALL include counts and machine-readable skip reasons
- **AND** missing eligible files SHALL be distinguishable from intentionally unsupported files

#### Scenario: Post-processing is degraded

- **WHEN** Phase 3 reports timeout, stale or unavailable GitNexus context, token-budget cutoff, or another degradation reason
- **THEN** the execution report SHALL preserve those degradation reasons separately from detector execution evidence
- **AND** the caller SHALL classify the scan as degraded even when findings are returned
- **AND** it SHALL NOT publish the exact phrase "No code scan issues found" for a zero-finding degraded result

#### Scenario: Existing return contract remains compatible

- **WHEN** execution evidence is added to `MrScanOrchestrator.run()`
- **THEN** the method SHALL continue returning exactly `(findings, report)`
- **AND** existing Phase 3 report keys SHALL remain available during migration
- **AND** new evidence SHALL be added within the report dictionary rather than as an additional tuple element

### Requirement: Active runtimes SHALL expose code-scan deployment provenance

The launchd ai-review runtime and Docker scheduler runtime SHALL make it possible to prove which `ai_review` and `code_daily_scan` source copies are imported after deployment.

#### Scenario: Launchd runtime is verified

- **WHEN** ai-review is deployed
- **THEN** deployment verification SHALL run under the launchd runtime virtual environment
- **AND** it SHALL prove that imported `ai_review` and `code_daily_scan` modules resolve under `deployments/ai-review`
- **AND** source/runtime snapshots SHALL include the copied `code-daily-scan` dependency

#### Scenario: Scheduler runtime is verified

- **WHEN** `code-daily-scan` scanner code is changed
- **THEN** the scheduler service SHALL be rebuilt or restarted so its long-running Python process reloads the bind-mounted source
- **AND** scheduler health and in-container module provenance SHALL be verified
- **AND** the unused `~/deployments/code-daily-scan/app` copy SHALL NOT be treated as evidence that either active runtime was updated

### Requirement: CodeScanReviewer SHALL emit outcome evidence to operations logs

Every completed, skipped, degraded, or failed code scan SHALL emit one structured summary event containing MR identity, reviewed SHA, checkout SHA, execution counts, outcome, and degradation or skip reasons.

#### Scenario: Operator investigates an MR scan

- **WHEN** an operator searches logs by project and MR IID
- **THEN** one summary event SHALL show whether the scan was clean, had findings, was skipped, was degraded, or failed
- **AND** the event SHALL include enough counts to determine whether any eligible files and rules were evaluated

### Requirement: CodeScanReviewer SHALL serialize findings to FindingParser-compatible format

Findings SHALL be formatted as markdown list items in the pattern `- [severity] file:line - message`
to ensure compatibility with `FindingParser` and the existing summary comment builder.

Severity mapping: `P0`/`P1` → `critical`, `P2` → `high`, `P3` → `medium`, informational → `suggestion`.

#### Scenario: Findings are formatted correctly

- **WHEN** scan completes with `Finding` objects
- **THEN** each finding SHALL be serialized as `- [severity] {file_path}:{line} - {message}`
- **AND** the finding's `message` field SHALL be used for the description
- **AND** the finding's `rule_id` SHALL be included as a prefix if present

### Requirement: CodeScanReviewer SHALL post findings as a separate MR comment

Scan findings SHALL be posted to the GitLab MR using a dedicated `<!-- code-scan-review -->`
marker to keep findings distinct from LLM review comments.

#### Scenario: Findings are posted with correct marker

- **WHEN** scan completes with findings
- **THEN** findings SHALL be posted using `GitLabReviewPoster.post_or_update()` with marker `<!-- code-scan-review -->`
- **AND** the comment SHALL include the serialized findings in markdown format

#### Scenario: Separate from LLM comments

- **WHEN** scan findings are posted
- **THEN** the comment marker SHALL be `<!-- code-scan-review -->` (not `<!-- mr-auto-review -->`)
- **AND** LLM review comments SHALL continue to use the existing `<!-- mr-auto-review -->` marker

### Requirement: CodeScanReviewer SHALL run in parallel with LLM reviewers

`ReviewOrchestrator` SHALL execute `CodeScanReviewer` concurrently with other reviewers
(kimi, claude, codex, pi) in the shared `ThreadPoolExecutor`.

#### Scenario: Reviewers execute concurrently

- **WHEN** `ReviewOrchestrator.run_sync()` is invoked
- **THEN** `CodeScanReviewer` SHALL be added to the thread pool alongside other reviewers
- **AND** the overall review SHALL complete when all reviewers finish (or timeout)

### Requirement: CodeScanReviewer SHALL handle errors gracefully

When scan execution fails, the reviewer SHALL catch exceptions, log the error,
post an error comment, and SHALL NOT prevent LLM reviewers from completing.

#### Scenario: Scan fails with exception

- **WHEN** `MrScanOrchestrator.run()` raises an exception (e.g., `RuntimeError`, `ValueError`)
- **THEN** `CodeScanReviewer` SHALL catch the exception
- **AND** it SHALL log the error with full traceback at ERROR level
- **AND** it SHALL return a `ReviewResult` with `status=FAILED` and error message
- **AND** LLM reviewers SHALL continue to completion

#### Scenario: Scan timeout

- **WHEN** scan exceeds the configured timeout (default: 120 seconds)
- **THEN** `CodeScanReviewer` SHALL raise `subprocess.TimeoutExpired`
- **AND** it SHALL be caught and converted to `ReviewResult` with `status=FAILED`

#### Scenario: Worktree creation fails

- **WHEN** `WorktreeManager` raises `RuntimeError("worktree creation failed")`
- **THEN** `CodeScanReviewer` SHALL catch the exception
- **AND** it SHALL return a `ReviewResult` with `status=FAILED` and descriptive error

### Requirement: CodeScanReviewer SHALL use tdt_core for GitLab operations

All GitLab API calls SHALL use `tdt_core.clients.gitlab.GitLabClientFactory.from_env()`.

#### Scenario: GitLab client is used correctly

- **WHEN** `GitLabReviewPoster` posts comments
- **THEN** it SHALL use `GitLabClientFactory.from_env()` to create the client
- **AND** it SHALL NOT use raw `requests` or `python-gitlab` SDK directly

### Requirement: CodeScanReviewer SHALL be added to get_enabled_clis()

The `Settings.get_enabled_clis()` method SHALL include "codescan" when `enable_codescan` is True.

#### Scenario: Code scan is included in enabled CLIs list

- **WHEN** `Settings.get_enabled_clis()` is called with `enable_codescan=True`
- **THEN** the returned list SHALL include "codescan"
- **AND** `ReviewOrchestrator._build_reviewers()` SHALL instantiate `CodeScanReviewer`

### Requirement: Settings SHALL include enable_codescan field

The `Settings` dataclass SHALL include `enable_codescan: bool` with two-tier env var fallback:
`AI_REVIEW_ENABLE_CODESCAN` → `ENABLE_CODE_SCAN` (default: `True`).

#### Scenario: Settings loads enable_codescan correctly

- **WHEN** `Settings.from_env()` is called
- **THEN** `enable_codescan` SHALL be set from `AI_REVIEW_ENABLE_CODESCAN` if set
- **OR** from `ENABLE_CODE_SCAN` if `AI_REVIEW_ENABLE_CODESCAN` is not set
- **OR** to `True` if neither is set
