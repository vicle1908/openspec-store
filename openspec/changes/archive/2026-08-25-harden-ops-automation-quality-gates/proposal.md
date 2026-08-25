# Proposal: Harden Operations Automation Quality Gates

## Why

The cron-reliability implementation is complete and integrated, but the repository's quality contract is not documented in its user-facing README. The current test suite passes with deprecations treated as errors, Ruff is clean, and mypy is clean; these guarantees should be explicit and repeatable.

## What Changes

- Document setup and canonical quality commands in the repository README.
- Record the timezone-aware UTC timestamp contract for execution models.
- Add a follow-up quality-gates spec covering tests, lint, type checking, and warning-free execution.
- Preserve generated `graphify-out/` changes and all unrelated worktree changes.

## Scope

Documentation and OpenSpec governance only. No runtime behavior change is proposed beyond the already-integrated UTC timestamp correction.

## Non-Goals

- No changes to cron definitions.
- No generated graph cleanup.
- No dependency upgrades.
- No broad pre-existing refactoring.

## Acceptance

The change is ready when the README contains reproducible commands, the new spec validates strictly, the review record is complete, and the change is archived after commit.

## Rollback

Revert the documentation/OpenSpec commit. No runtime rollback is required because this change adds no new runtime mutation.
