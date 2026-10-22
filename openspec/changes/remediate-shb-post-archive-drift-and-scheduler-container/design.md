# Design: Remediate SHB Post-Archive Drift, Stale Scheduler Container, and Archive Evidence Gaps

## Context

Our `2026-10-22` five-axis audit of recent OpenSpec archives identified three operational and governance gaps outside the scope of `persist-agent-tcc-provenance-and-auto-upgrade` and `standardize-npm-bun-toolchain-and-config`:
1. **`D1` (`shb-schedule-scheduler-1` Stale Container Image)**: Commit `ebd9695` (`2026-10-18`) through `7ed905d` (`2026-10-21`) landed 8 commits on `shb/shb-schedule` `main`, but the running container `shb-schedule-scheduler-1` was never rebuilt after `2026-10-17T03:09:23Z` (`sha256:cd2483ce1782...`). Consequently, `GET http://127.0.0.1:9110/scheduler/schedules/workstation-daily-update` still omits `execution_target` and `persisted`.
2. **`D9` (Uncommitted Post-Archive Jev Fixes & Stale Code Graphs Across SHB Repos)**: Following archive commit `714f6ac3` (`2026-10-21-agent-core-integrate-jev-system-one`), 24 tracked files across 8 SHB repositories (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`) were modified on `2026-10-22` to wire `OMNIROUTE_API_KEY` fallback, `_bind_deps_to_tool_func` guardrail/Jev injection for `tool_plain` tools (`pay_bill`, `parse_vietqr`, `screen_beneficiary`), and real CLI entrypoints. Because those 8 repos are dirty, scheduled knowledge refresh skips them (`10/13` GitNexus `STALE`, `13/13` Graphify `STALE`), and `tdt/agent-core` also has 8 uncommitted `graphify-out/` and ignore files.
3. **`D7` & `D10` (Archive Range-Readiness & Immutability Gaps)**:
   - `2026-10-20-reconcile-dev-tooling-and-hermes-runtime` (`804a8968`) was archived with `11/11` checked tasks but no `evidence.md`, causing `validate-archive-readiness.py --range HEAD~35..HEAD --strict` to exit `3`.
   - Commit `a3eb1fda` (`2026-10-20 20:01:11 +0700`) directly edited `openspec/changes/archive/2026-10-20-upgrade-omniroute-to-v3-8-52/evidence.md` 73 minutes after archive commit `52d5474e`.

## Architectural Decisions

### 1. Container Rebuild & Live Endpoint Verification (`shb/shb-schedule`)
- Following existing Docker Compose lifecycle conventions in `shb/shb-schedule/compose.yaml`, rebuild and recreate `scheduler` via `docker compose -f /Users/androidteam/Developer/shb/shb-schedule/compose.yaml up -d --build scheduler`.
- Verify live container parity by inspecting the new image creation timestamp and probing `GET http://127.0.0.1:9110/scheduler/schedules/workstation-daily-update` (`execution_target: "host"`, `persisted: false`) and `POST .../trigger` (HTTP `409 Conflict`).

### 2. Multi-Repo SHB Verification, Atomic Commits, and Index Refresh (`shb/shb-*` & `tdt/agent-core`)
- For each of the 8 modified SHB repositories (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`):
  1. Run `uv run pytest`, `uv run ruff check`, and `uv run mypy --strict`.
  2. Commit the verified source and test changes with `GRAPHIFY_SKIP_HOOK=1` so commits are atomic and deterministic.
- In `tdt/agent-core`, restore `graphify-out/` and remove or commit `.gitnexusignore`/`.graphifyignore` without touching Python source/test files (`5085b45` invariant preserved).
- Refresh GitNexus (`gitnexus analyze`) and Graphify (`graphify update .`) across all stale `shb/shb-*` repositories and verify `knowledge-status.sh` reports `13/13` `FRESH`.

### 3. Forward-Remediated Archive Ledger & Immutability Check (`platform/openspec-store`)
- Preserve archive immutability (`git diff --name-only -- openspec/changes/archive` remains empty during apply).
- Record the complete verification evidence for `2026-10-20-reconcile-dev-tooling-and-hermes-runtime` (`804a8968`) and the immutability audit note for `2026-10-20-upgrade-omniroute-to-v3-8-52` (`a3eb1fda`) in this change's `evidence.md` and register a `FORWARD_REMEDIATED_ARCHIVES` mapping in `scripts/validate-archive-readiness.py` so `--range` mode passes once a forward-remediation ledger exists, while flagging any future post-archive edits in `audit_git_range()`.

## Transaction Boundaries

- **SHB Repositories (`/Users/androidteam/Developer/shb/shb-*`)**: Each of the 8 dirty repositories is tested and committed independently on its own `main` branch before refreshing GitNexus and Graphify indexes.
- **SHB Scheduler Runtime (`shb-schedule-scheduler-1`)**: Rebuilt from the clean committed `/Users/androidteam/Developer/shb/shb-schedule` checkout (`7ed905d`).
- **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: `scripts/validate-archive-readiness.py`, unit tests, and `evidence.md` are committed in `openspec-store` without mutating `openspec/changes/archive/`.
