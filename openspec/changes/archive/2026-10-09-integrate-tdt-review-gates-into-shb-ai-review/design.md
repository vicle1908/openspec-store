# Design

## Context

See `proposal.md` — Why.

The `shb-ai-review` package currently implements standalone Pydantic models (`ReviewFinding`, `ReviewOutcome`) and a rudimentary local scanning orchestrator in `shb_review/orchestrator.py`. However, it lacks integration with GitLab Merge Request APIs, diff hunk filtering, deduplication across revision force-pushes, isolated worktrees, and test coverage calculation. The proven production architecture in `tdt/ai-review` provides working reference implementations for these gates, which will be adapted and modernized into `shb-ai-review`.

## Goals / Non-Goals

**Goals:**
- Provide a robust GitLab MR diff extractor and discussion publisher in `shb_review/gitlab/`.
- Provide `HunkGate` in `shb_review/validation/hunk_gate.py` using binary interval search (`bisect`) to ensure findings are strictly positioned on changed diff lines.
- Provide `ReviewDeduplicator` in `shb_review/validation/deduplicator.py` to prevent duplicate notes on re-runs.
- Provide `GitWorktreeManager` in `shb_review/worktree/manager.py` to isolate checkouts and protect workspace cleanliness.
- Provide standalone CLI `mr-coverage` and module `shb_review/coverage/scanner.py` for merge request review coverage and gap scanning.

**Non-Goals:**
- Do not build a complex multi-process background worker daemon or persistent Celery queue; operations run synchronously in CLI or CI environments.
- Do not introduce SaaS third-party code review platforms.
- Do not rewrite existing AST quality rules in `shb_review/models.py`.

## Decisions

### 1. Structure as Modular Subpackages Under `shb_review`
Align `shb-ai-review` with the mature modular design from `tdt/ai-review`:
- `shb_review/gitlab/`: `client.py` (GitLab API client via `python-gitlab`), `posting.py` (discussion publisher).
- `shb_review/validation/`: `hunk_gate.py` (diff hunk line filtering), `deduplicator.py` (fingerprint deduplication).
- `shb_review/worktree/`: `manager.py` (disposable git worktree management).
- `shb_review/coverage/`: `scanner.py` (MR review gap scanner), `cli.py` (`mr-coverage` entrypoint).

*Rationale*: Clean separation of concerns allows individual components to be unit tested in isolation without mocking entire CI runs.

### 2. Binary Range Search for Hunk Validation (`HunkGate`)
Parse unified git diffs into structured `changed_ranges_for_path: dict[str, list[tuple[int, int]]]`. For each file, sort ranges and use `bisect.bisect_right` to test line inclusion in $O(\log N)$ time.
- If a finding falls within a modified range $\rightarrow$ post as an inline discussion with line context.
- If a finding falls outside modified ranges or on an unmodified file $\rightarrow$ route into top-level summary report as an advisory warning.

*Alternative considered*: Regex scanning on raw patch strings per finding. Rejected because parsing once into range tuples is deterministic, faster, and immune to git context line drift.

### 3. Fingerprint-Based Discussion Deduplication
Compute a SHA-256 fingerprint for each finding based on `(file_path, rule_id, normalized_message)`. When publishing discussions:
- Fetch existing MR discussions with marker `<!-- shb-ai-review -->`.
- Extract existing fingerprints.
- Suppress new discussions whose fingerprints already match an open thread.
- If a previous violation no longer appears in the current review, resolve the discussion thread automatically.

### 4. Ephemeral Worktree Lifecycle
When reviewing a branch or MR, the reviewer creates `~/.shb/worktrees/mr-<id>` using `git worktree add --detach`.
- Auto-prune stale worktree registrations before creation when count exceeds threshold (16).
- Use `try ... finally` context manager to ensure `git worktree remove --force` executes even on evaluation errors.

## Risks / Trade-offs

- **GitLab API Rate Limits**: Posting dozens of individual inline comments can exhaust API tokens on large MRs.
  - *Mitigation*: Cap inline discussion posts to a configurable maximum (default 15 highest-severity findings); summarize the remainder in the top-level note.
- **Merge Base Ambiguity**: Worktree creation requires fetching both target and source branches to accurately compute the three-dot diff `git diff $(git merge-base target source)...source`.
  - *Mitigation*: `GitWorktreeManager` explicitly fetches both target and source refs before computing merge-base.
