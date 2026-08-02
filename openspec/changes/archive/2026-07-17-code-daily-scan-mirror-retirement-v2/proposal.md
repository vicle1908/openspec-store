# Proposal: `code-daily-scan-mirror-retirement-v2` — CI Guard + Drift Allowlist

## Why

The `docs-repo-canonical-rule-source` change (v1) ships `check-docs-drift` as a **runtime-only** tool: operators can run it manually to detect when platform-repo mirrors have drifted from the canonical `poems-mobile3-docs` source. However, there is no automated enforcement — drift can accumulate silently between runs.

This change adds a **CI guard** that runs `check-docs-drift` on every pipeline for both `poems-mobile3-android` and `poems-mobile3-ios`, blocking merges when drift is detected.

## What Changes

### 1. GitLab CI job in `poems-mobile3-android`

Add a job to `.gitlab-ci.yml` (or the relevant CI config) that:

- Runs `code-daily-scan check-docs-drift --platform=android` in the repo root.
- Fails the pipeline (exit 1) when drift is detected.
- Runs after the `rules/` directory is cloned/checked out.

### 2. GitLab CI job in `poems-mobile3-ios`

Same as above, but `--platform=ios`.

### 3. Drift allowlist (`.drift-allowlist`)

Add a `.drift-allowlist` file in each platform repo's `docs/` directory. This file allows feature branches to temporarily opt out of drift detection when the drift is intentional (e.g., a long-running feature branch that will be resolved before merge).

Format:
```
# .drift-allowlist
# One entry per line: <category-stem> <reason> <YYYY-MM-DD>
# Example:
# state-mutation    intentionally modified for FEATURE-X 2026-07-31
```

The `check-docs-drift` CLI is updated to read `.drift-allowlist` from the mirror root and skip entries whose expiry date has not passed and whose branch matches the current context.

## Non-Goals

- This does NOT remove the local mirrors — that is handled by `android-docs-mirror-retirement` and `ios-docs-mirror-retirement`.
- This does NOT add real-time webhook-based invalidation — that is a future Stage 3 concern.

## Scope

- In scope: `code-daily-scan` (CLI update), `poems-mobile3-android`, `poems-mobile3-ios` (CI config).
- Out of scope: `tdt-core`, `webhook-receiver`, `ai-review`, docs repo itself.

## Files to Change

- `code-daily-scan/src/code_daily_scan/cli.py` — update `check-docs-drift` to read `.drift-allowlist`
- `poems-mobile3-android/.gitlab-ci.yml` — add drift-check job
- `poems-mobile3-ios/.gitlab-ci.yml` — add drift-check job
- `poems-mobile3-android/docs/.drift-allowlist` — create with header
- `poems-mobile3-ios/docs/.drift-allowlist` — create with header
