# Proposal

## Why

The `shb-ai-review` service currently only executes basic local regex and heuristic scans on local files, lacking automated GitLab Merge Request integration, line-level diff hunk gating, isolated worktree execution, and test coverage enforcement. Porting proven review gate architectures from `tdt/ai-review` into `shb-ai-review` closes this governance gap, enabling automated, zero-hallucination compliance and security review postings directly on Saigon - Hanoi Bank (SHB) GitLab merge requests.

## What Changes

- **Implement GitLab MR Review Client and Discussion Posting**: Port and modernize GitLab MR diff inspection and discussion posting from `tdt/ai-review/src/ai_review/gitlab/review_posting.py` into `shb-ai-review`, enabling automated posting of structured inline comments and discussion resolutions.
- **Implement Diff Hunk Gating (`HunkGate`)**: Port `hunk_gate.py` to ensure AI-generated review comments strictly attach to modified lines within valid git diff hunks, completely preventing off-diff hallucinated comments.
- **Implement Deduplication & Severity Classification**: Port `deduplicator.py` and `severity.py` to prevent duplicate review comments across repeated CI runs or updated MR revisions while classifying issues into `BLOCKING`, `MAJOR`, and `NIT`.
- **Implement Isolated Git Worktree Manager**: Port `worktree/manager.py` to allow the review engine to check out base and head commits in disposable temporary worktrees without dirtying developer or CI working directories.
- **Implement Diff Test Coverage CLI (`mr-coverage`)**: Provide the standalone `mr-coverage` entrypoint in `shb_review/coverage/` and `pyproject.toml` to calculate patch coverage on merge request diffs and fail CI when falling below thresholds.

## Capabilities

### Modified Capabilities

- `shb-review-and-quality`: Extends the existing specification to mandate line-level git diff hunk gating, isolated worktree evaluation, review deduplication across MR revisions, and the standalone `mr-coverage` CLI gatekeeper.

## Non-Goals

- Do not modify or replace the core banking AST and compliance rules in `shb_review/models.py`.
- Do not introduce external commercial SaaS review dependencies; all evaluations run via local static engines or authorized OmniRoute endpoints.
- Do not modify other SHB services (`shb-schedule`, `shb-core`, `shb-tools`) in this change.
