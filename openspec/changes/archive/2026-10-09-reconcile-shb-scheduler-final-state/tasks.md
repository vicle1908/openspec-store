# Tasks

## 1. Evidence and Archive Reconciliation

- [x] 1.1 Capture final immutable identities and working-tree status for `shb-schedule`, `shb-agent-skills`, and `openspec-store`; record the final scheduler commit, skills commit, archive path, and the fact that `git diff --name-only -- openspec/changes/archive` is empty.
- [x] 1.2 Produce value-blind corrective evidence comparing archived evidence/review claims with final live implementation facts, explicitly marking stale commit IDs, historical test counts, pre-Task-7 review language, and the final verification commands/results.

## 2. Canonical Specification Conformance

- [x] 2.1 Refactor only the overlong first requirement in `openspec/specs/shb-schedule-engine/spec.md` into behavior-preserving normative requirements/scenarios; verify scenario headings and semantic coverage remain intact.
- [x] 2.2 Run `openspec validate shb-schedule-engine --strict --json --store openspec-store` and the corrective change strict validation; record exit codes and issue-free JSON results.

## 3. Curated Documentation Reconciliation

- [x] 3.1 Update `wiki/entities/shb-schedule.md` to describe Docker Compose/PostgreSQL 18.6 deployment, PostgreSQL advisory-lock ownership for containers, and local SQLite/`fcntl.flock` fallback; remove obsolete LaunchAgent/systemd generator guidance.
- [x] 3.2 Update `wiki/entities/shb.md` to describe the final scheduler architecture without removing the documented local SQLite development fallback; verify no unrelated wiki files changed.
- [x] 3.3 Re-read both wiki entities and verify they contain no obsolete host-service installation instructions and accurately name the Compose/PostgreSQL operational path.

## 4. Exact Host Cleanup

- [x] 4.1 Verify `/Users/androidteam/Library/LaunchAgents/com.shb.schedule.plist` is the exact obsolete scheduler target, inspect launchd/process state, and record the bounded pre-change result; if active ownership is ambiguous, leave the plist in place and record the blocker.
- [x] 4.2 If task 4.1 establishes safe removal, unlink only `/Users/androidteam/Library/LaunchAgents/com.shb.schedule.plist`; verify the exact path is absent and unrelated LaunchAgent files remain unchanged.
- [x] 4.3 Verify `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/service/` contains no source files and only residual bytecode; remove only the residual cache directory and verify scheduler source paths remain intact.

## 5. Final Verification and Delivery

- [x] 5.1 Run the canonical scheduler verification commands supported by the repository (`uv run pytest tests/`, `uv run ruff check .`, and `uv run mypy src`) and record exact exit statuses without changing generated Graphify artifacts.
- [x] 5.2 Verify `git status`, changed-path boundaries, archive immutability, and corrective evidence consistency across all affected roots; preserve unrelated dirty/untracked paths.
- [x] 5.3 Commit only the corrective OpenSpec artifacts, canonical spec, approved wiki files, and exact cleanup changes; do not commit Graphify outputs, unrelated active changes, or secrets. Do not push.
- [x] 5.4 Run final strict validation and archive-readiness checks for the corrective change; archive it only after every task has truthful evidence and the immutable original archive remains untouched.
