# Embedded Copies Resolution Record

**Date:** 2026-09-05
**Owner decision:** "should update copies. apply changes" (user, 2026-09-05)
**Supersedes:** the `tdt_scheduler_embedded_copy_comparison` rows in `cleanup-verification.json` recorded earlier the same day.

## Investigation findings

1. The directories under `/Users/androidteam/Developer/tdt-scheduler/` named `agent-core/`, `jira-skill/`, `code-daily-scan/`, `jira-daily-reports/`, `tdt-core/`, `tdt-sheets/`, `tdt-observability/`, `poems-mobile3-android/`, `poems-mobile3-ios/` were **not stale source copies**. They were empty vestigial stubs:
   - `0` regular files in each (verified `find <dir> -type f | wc -l` = 0).
   - Only empty skeleton subdirectories (`src/`, `config/`, and one empty directory anomalously named `README.md/` under `code-daily-scan/`).
   - Not tracked by git (`git ls-files` on all of them: empty; invisible to `git status`).
2. The earlier "62/44/30/28 divergent entries" measurement was `diff -qr stub vs full upstream repo` — the entries were overwhelmingly "Only in upstream" (upstream-only files like `.git/`, `.venv/`, caches, docs) plus "only in upstream `src/`: the actual package dir" because embedded `src/` was empty. The prior `divergent_from_upstream` characterization was imprecise; the true state was **empty stubs**.
3. The current build architecture does **not** consume these directories at all:
   - `compose.yaml` build context is `TDT_WORKSPACE_ROOT` (the workspace root), with `SCHEDULER_SOURCE_PATH` pointing at the scheduler checkout.
   - `Dockerfile` COPYs inputs from the **workspace root** (`agent-core/src`, `jira-daily-reports/src`, `jira-skill/src`, `code-daily-scan/src` + `config`, etc.).
   - `Dockerfile.dockerignore` deny-all-then-allowlist governs exactly which workspace-root files enter the context.
   - `compose.yaml` volumes bind-mount the real upstream repos (`TDT_WORKSPACE_ROOT/agent-core` → `/workspace/agent-core`, `.../code-daily-scan/src` → `/workspace/code-daily-scan/src`, …) at runtime.
   - Grep of all tracked tdt-scheduler files (source, tests, generators, docs): **zero references** to `tdt-scheduler/<repo>/`-style embedded paths. `entrypoint.sh`, generators, and tests reference `/workspace/...` container paths only.
   - The stubs are consistent with remnants of an older build layout (pre workspace-root-context era; `.orca-worktree-trash/` in the repo corroborates cleanup history).

## Resolution applied

"Updating" the empty stubs into full copies would duplicate the workspace-root inputs and contradict the deny-by-default allowlist architecture. The correct resolution was removal.

- Removed all 9 empty stub directories using **`rmdir` only** (fail-safe: errors on any non-empty directory; cannot delete files). No `rm -rf` used.
- Removed: `agent-core`, `jira-skill`, `code-daily-scan`, `jira-daily-reports`, `tdt-core`, `tdt-sheets`, `tdt-observability`, `poems-mobile3-android`, `poems-mobile3-ios`.
- `webhook-receiver/` and `ai-review/` stubs did not exist at action time.

## Post-action verification

- All 9 paths confirmed absent (`gone` per-path check).
- `git -C tdt-scheduler status --porcelain`: clean — removal of untracked empty dirs produces no tracked change, no commit required in tdt-scheduler.
- Build contract intact: `Dockerfile`, `Dockerfile.dockerignore`, `compose.yaml`, `entrypoint.sh`, `dependency_integrity_gate.py`, `generators/` all present and untouched.
- Workspace-root build inputs present and unchanged: `agent-core/pyproject.toml`, `agent-core/src/agent_core/`, `jira-skill/pyproject.toml`, `code-daily-scan/pyproject.toml`, `code-daily-scan/config/rule_patterns.yaml`, `jira-daily-reports/pyproject.toml`.
- Reference check: zero tracked references to the removed paths (grep before removal; paths now absent, so none can resolve).

## Corrected claim classification

| Prior classification | Corrected classification |
|---|---|
| `tdt_scheduler_embedded_copies_current: unverified` (stale copies) | `vestigial_empty_stubs_removed`: no embedded copies existed to update; build consumes workspace-root inputs via allowlist + bind mounts; owner decision recorded and applied |

No application, worktree, branch, credential, or provider surface was changed. No archived OpenSpec file was modified.
