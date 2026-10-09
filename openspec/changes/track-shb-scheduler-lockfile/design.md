# Design

## Context

See proposal.md for motivation. The scheduler's `.gitignore` currently ignores every `*.lock`, while `pyproject.toml` and the Dockerfile require a committed `uv.lock` for frozen, reproducible installs.

## Goals / Non-Goals

**Goals:**
- Track only the project dependency lockfile while retaining local runtime-state exclusions.
- Verify the lockfile is present, tracked, and accepted by `uv sync --frozen`.
- Keep the change limited to the scheduler repository's ignore policy and OpenSpec artifacts.

**Non-Goals:**
- No dependency upgrade or lockfile regeneration unless frozen verification proves the existing lockfile is stale.
- No changes to runtime lock paths, database files, Docker/Compose behavior, or generated Graphify output.

## Decisions

### 1. Use an explicit negation rule
Keep the broad `*.lock` rule for local runtime state and add `!uv.lock` immediately after it. Git's last matching rule then allows the dependency lockfile while continuing to ignore other lock files.

### 2. Verify tracked state before implementation
Before editing, confirm `git check-ignore -v uv.lock` identifies the broad rule and `git ls-files uv.lock` is empty. After editing, verify `git check-ignore -v uv.lock` no longer reports it as ignored and `git ls-files --error-unmatch uv.lock` succeeds after staging/commit.

### 3. Use frozen dependency verification
Run `uv sync --frozen --no-dev --no-editable` in the scheduler repository or the existing container build path. Do not regenerate `uv.lock`; a stale lockfile is a failure requiring explicit follow-up rather than silent update.

## Risks / Trade-offs

- Negation rules are order-sensitive; placing `!uv.lock` before `*.lock` would not work.
- Tracking the lockfile may expose a pre-existing stale dependency resolution; this is desirable because the build must fail visibly rather than drift.
- The existing generic rule may intentionally cover other project lock artifacts; the explicit exception is limited to the one required dependency lockfile.
