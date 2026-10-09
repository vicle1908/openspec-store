# Design

## Context

See proposal.md for motivation. The scheduler's `.gitignore` currently ignores every `*.lock`, while `pyproject.toml` and the Dockerfile require a committed `uv.lock` for frozen, reproducible installs.

## Goals / Non-Goals

**Goals:**
- Track only the project dependency lockfile while retaining local runtime-state exclusions.
- Verify the lockfile is present, tracked, and accepted by `uv sync --frozen`.
- Keep runtime edits bounded to the seven source-lint diagnostics, retaining asynchronous reload tasks and reloader encapsulation without changing workflow semantics.

**Non-Goals:**
- No dependency upgrade or lockfile regeneration. Check metadata freshness with `uv lock --check`; frozen sync does not perform that check.
- No changes to runtime lock paths, database files, Docker/Compose behavior, or generated Graphify output.

## Decisions

### 1. Use an explicit negation rule
Keep the broad `*.lock` rule for local runtime state and add `!uv.lock` immediately after it. Git's last matching rule then allows the dependency lockfile while continuing to ignore other lock files.

### 2. Verify tracked state before implementation
Before editing, confirm `git check-ignore -v uv.lock` identifies the broad rule and `git ls-files uv.lock` is empty. After editing, verify `git check-ignore -v uv.lock` no longer reports it as ignored and `git ls-files --error-unmatch uv.lock` succeeds after staging/commit.

### 3. Use frozen dependency verification
Run `uv lock --check` to verify metadata freshness, and retain `uv sync --frozen --no-dev --no-editable` for installation from the unchanged lockfile. `--frozen` deliberately skips freshness validation; `--locked` or `uv lock --check` rejects stale metadata without rewriting the lockfile.

### 4. Source-lint gate extension approved during apply
Resolve the seven reported source diagnostics only: simplify equivalent boolean conditions in config/health, combine connection/cursor contexts in ownership, replace health's private-lock access with a public reloader idle-wait operation, and retain every pending signal-triggered task until completion. Do not add suppression directives, change permissions/ownership semantics, or bypass source lint. Preserve reload serialization, standby fencing, and shutdown ordering.

## Risks / Trade-offs

- Negation rules are order-sensitive; placing `!uv.lock` before `*.lock` would not work.
- Tracking the lockfile may expose a pre-existing stale dependency resolution; this is desirable because the build must fail visibly rather than drift.
- The existing generic rule may intentionally cover other project lock artifacts; the explicit exception is limited to the one required dependency lockfile.
