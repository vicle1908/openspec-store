# Tasks

## 1. Diff Hunk Gate & Finding Filtering

- [x] 1.1 Implement `HunkGate` and binary range search (`bisect`) in `shb_review/validation/hunk_gate.py` to filter findings against git diff modified lines
- [x] 1.2 Implement finding fingerprinting and discussion deduplication in `shb_review/validation/deduplicator.py`
- [x] 1.3 Add comprehensive unit tests for `HunkGate` covering modified lines, context lines, deleted lines, and unrepresented files in `tests/test_hunk_gate.py`

## 2. Isolated Git Worktree Lifecycle

- [x] 2.1 Implement `GitWorktreeManager` in `shb_review/worktree/manager.py` supporting detached branch checkouts, stale worktree pruning, and fail-safe removal context managers
- [x] 2.2 Add unit tests for worktree lifecycle, merge-base checkout, and error cleanup in `tests/test_worktree.py`

## 3. GitLab MR Client & Discussion Publisher

- [x] 3.1 Declare `python-gitlab>=8.5.0` in `shb-ai-review/pyproject.toml` dependencies, run `uv sync`, and implement GitLab MR client in `shb_review/gitlab/client.py` using `python-gitlab` to fetch MR details, changes, and existing discussions
- [x] 3.2 Implement discussion publisher in `shb_review/gitlab/posting.py` mapping hunk-gated findings to inline discussion notes, enforcing comment caps (default 15), and publishing markdown summaries with fingerprint markers
- [x] 3.3 Add unit tests with mock GitLab API fixtures verifying discussion generation, deduplication, and resolution tracking in `tests/test_gitlab_posting.py`

## 4. MR Review Coverage Scanner (`mr-coverage`)

- [x] 4.1 Implement `CoverageScanner` and `CoverageGap` in `shb_review/coverage/scanner.py` evaluating `--rows-json` MR state snapshots to detect missing, stale, or failed reviews
- [x] 4.2 Expose the `mr-coverage` Typer CLI command in `shb_review/coverage/cli.py` (with `scan`, `status`, `health` subcommands) and register `mr-coverage = "shb_review.coverage.cli:app"` in `shb-ai-review/pyproject.toml`
- [x] 4.3 Add unit tests for `mr-coverage` verifying gap detection, row JSON parsing, and exit code 0/1 contracts in `tests/test_coverage_scanner.py`
## 5. Review Orchestrator Integration & End-to-End Verification

- [x] 5.1 Integrate `GitWorktreeManager`, `HunkGate`, and `GitLabReviewPublisher` into `shb_review/orchestrator.py`
- [x] 5.2 Add `shb-ai-review review-mr --project <id> --mr <iid>` subcommand in `shb_review/cli.py`
- [x] 5.3 Run full test suite with `uv run pytest` across `shb/shb-ai-review` and record pass verification

## 6. Changed-Line Test Coverage Gating (`mr-coverage diff`)

- [x] 6.1 Implement `PatchCoverageCalculator` and `calculate_patch_coverage` in `shb_review/coverage/patch.py` evaluating git diffs against Cobertura XML
- [x] 6.2 Integrate `mr-coverage diff` CLI subcommand in `shb_review/coverage/cli.py` with exit code 0/1/2 contracts
- [x] 6.3 Add unit tests for patch coverage calculation and CLI in `tests/test_patch_coverage.py` and `tests/test_coverage_scanner.py`

## 7. AI Review Provider & Strict Prompt Isolation

- [x] 7.1 Implement `AiReviewer` in `shb_review/ai/reviewer.py` using Pydantic AI v2 with tools disabled and outbound credential redaction
- [x] 7.2 Integrate opt-in `--ai` review flag into `shb-ai-review review-mr` and `shb-ai-review scan` CLI commands
- [x] 7.3 Add unit tests for credential redaction and structured output mapping in `tests/test_ai_reviewer.py`

## 8. Defect Remediation & Review Gate Hardening

- [x] 8.1 Harden HunkGate path normalization, nested same basename preservation, and side-aware line filtering in `shb_review/validation/hunk_gate.py`
- [x] 8.2 Harden GitWorktreeManager with git ref validation and safe stale pruning in `shb_review/worktree/manager.py`
- [x] 8.3 Harden GitLab client and publisher with snapshot reuse, per-action race checks, and author ownership in `shb_review/gitlab/client.py` and `posting.py`
- [x] 8.4 Enforce thread resolution safety gates (never resolve on failure, partial, capped, or unchanged files) in `shb_review/validation/deduplicator.py`
