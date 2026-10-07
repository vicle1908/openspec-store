# Tasks

## 1. Diff Hunk Gate & Finding Filtering

- [ ] 1.1 Implement `HunkGate` and binary range search (`bisect`) in `shb_review/validation/hunk_gate.py` to filter findings against git diff modified lines
- [ ] 1.2 Implement finding fingerprinting and discussion deduplication in `shb_review/validation/deduplicator.py`
- [ ] 1.3 Add comprehensive unit tests for `HunkGate` covering modified lines, context lines, deleted lines, and unrepresented files in `tests/test_hunk_gate.py`

## 2. Isolated Git Worktree Lifecycle

- [ ] 2.1 Implement `GitWorktreeManager` in `shb_review/worktree/manager.py` supporting detached branch checkouts, stale worktree pruning, and fail-safe removal context managers
- [ ] 2.2 Add unit tests for worktree lifecycle, merge-base checkout, and error cleanup in `tests/test_worktree.py`

## 3. GitLab MR Client & Discussion Publisher

- [ ] 3.1 Implement GitLab MR client in `shb_review/gitlab/client.py` using `python-gitlab` to fetch MR details, changes, and existing discussions
- [ ] 3.2 Implement discussion publisher in `shb_review/gitlab/posting.py` mapping hunk-gated findings to inline discussion notes, enforcing comment caps, and publishing markdown summaries
- [ ] 3.3 Add unit tests with mock GitLab API fixtures verifying discussion generation, deduplication, and resolution tracking in `tests/test_gitlab_posting.py`

## 4. Diff Test Coverage Gatekeeper (`mr-coverage`)

- [ ] 4.1 Implement patch coverage calculation in `shb_review/coverage/scanner.py` intersecting git diff changed lines with Cobertura/coverage XML reports
- [ ] 4.2 Expose the `mr-coverage` CLI command in `shb_review/coverage/cli.py` and register the console script entrypoint in `shb-ai-review/pyproject.toml`
- [ ] 4.3 Add unit tests for `mr-coverage` verifying threshold evaluation, table formatting, and exit code 0/1 contracts in `tests/test_coverage_gate.py`

## 5. Review Orchestrator Integration & End-to-End Verification

- [ ] 5.1 Integrate `GitWorktreeManager`, `HunkGate`, and `GitLabReviewPublisher` into `shb_review/orchestrator.py`
- [ ] 5.2 Add `shb-ai-review review-mr --project <id> --mr <iid>` subcommand in `shb_review/cli.py`
- [ ] 5.3 Run full test suite with `uv run pytest` across `shb/shb-ai-review` and record pass verification
