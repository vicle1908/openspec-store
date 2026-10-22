# Proposal: Remediate SHB Post-Archive Drift, Stale Scheduler Container, and Archive Evidence Gaps

## Why

Post-archive runtime verification on `2026-10-22` revealed four concrete drift and governance gaps across the SHB banking ecosystem, the `shb-schedule` Docker container, and recent OpenSpec archives that cause runtime schedule divergence, stale code graphs, and failing archive-readiness range checks.

Specifically:
1. **Stale `shb-schedule-scheduler-1` Container Image (`D1`)**: The running `shb-schedule-scheduler-1` Docker container (`sha256:cd2483ce1782...`, built `2026-10-17T03:09:23Z`) lags 8 commits behind `shb/shb-schedule` `main` (`ebd9695` through `7ed905d`), so `GET /scheduler/schedules/workstation-daily-update` still returns HTTP `200` without `execution_target` or `persisted` fields.
2. **Uncommitted Post-Archive Jev Fixes & Stale Code Graphs Across 8 SHB Repositories (`D9`)**: After `2026-10-21-agent-core-integrate-jev-system-one` (`714f6ac3`) was archived, 24 tracked source and test files were modified across 8 SHB repositories (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`) to fix `_resolve_model_gateway_key` `OMNIROUTE_API_KEY` fallback, `tool_plain` guardrail/Jev dependency binding, and real CLI entrypoints, leaving all 8 working trees uncommitted and `10/13` GitNexus + `13/13` Graphify indexes `STALE` (plus 8 dirty index/ignore files in `tdt/agent-core`).
3. **Archive Range-Readiness & Immutability Ledger Gaps (`D7` & `D10`)**: `python3 scripts/validate-archive-readiness.py --range HEAD~35..HEAD --strict` fails with `exit code 3` because `2026-10-20-reconcile-dev-tooling-and-hermes-runtime` (`804a8968`) was archived without `evidence.md`, while commit `a3eb1fda` modified `openspec/changes/archive/2026-10-20-upgrade-omniroute-to-v3-8-52/evidence.md` 73 minutes after archive commit `52d5474e`.

## What Changes

1. **Rebuild and Verify `shb-schedule-scheduler-1` Container (`D1`)**:
   - Rebuild and recreate `shb-schedule-scheduler-1` from current `shb/shb-schedule` `main` (`7ed905d`+) via `docker compose -f ~/Developer/shb/shb-schedule/compose.yaml up -d --build scheduler` and verify `GET /scheduler/schedules/workstation-daily-update` exposes `execution_target: "host"` and `persisted: false` (and `POST .../trigger` returns HTTP `409`).
2. **Commit Post-Archive Jev Runtime/CLI Fixes & Refresh Code Graphs Across SHB Repositories (`D9`)**:
   - Run `uv run pytest`, `uv run ruff check`, and `uv run mypy --strict` across the 8 modified `shb/shb-*` repositories, commit the 24 verified files cleanly, clean or commit the index/ignore metadata in `tdt/agent-core`, and refresh GitNexus and Graphify indexes so all 13 `shb/shb-*` repositories report `FRESH` in `knowledge-status.sh`.
3. **Remediate Archive Range-Readiness and Codify Immutability Enforcement (`D7` & `D10`)**:
   - Record the retrospective verification ledger for `2026-10-20-reconcile-dev-tooling-and-hermes-runtime` (`804a8968`) and the corrective audit note for `a3eb1fda` (`2026-10-20-upgrade-omniroute-to-v3-8-52`), and update `scripts/validate-archive-readiness.py` so `--range` mode both enforces post-archive immutability (`git diff` on pre-existing `openspec/changes/archive/` directories) and supports forward-remediated archive exceptions registered in the store.

## Non-Goals

- Re-opening or moving archived directories under `openspec/changes/archive/` back to `openspec/changes/`.
- Modifying `tdt/agent-core` Python source or test files (frozen at `5085b45`).
- Changing `shb-schedule` Postgres schema or host LaunchAgent schedule definitions.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shb-scheduler-docker-lifecycle`: Require container image parity with `shb/shb-schedule` `main` after workflow or API commits so live `/scheduler/schedules` endpoints match committed code.
- `jev-decision-runtime`: Require clean committed working trees and `FRESH` GitNexus/Graphify indexes across all 13 `shb/shb-*` repositories following Jev runtime and CLI integration.
- `openspec-runtime-governance`: Enforce archive immutability in `validate-archive-readiness.py --range` and define forward-remediation ledger handling for historical archive gaps (`804a8968` and `a3eb1fda`).

## Impact

- **Ownership Boundaries**:
  - **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Owns `scripts/validate-archive-readiness.py`, `openspec/specs/`, and corrective audit evidence.
  - **SHB Banking Ecosystem (`/Users/androidteam/Developer/shb/shb-*`)**: Owns the 8 repositories with uncommitted Jev runtime/CLI fixes (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`) and the `shb/shb-schedule` Docker Compose stack.
  - **TDT Agent Core (`/Users/androidteam/Developer/tdt/agent-core`)**: Owns working-tree hygiene for `.gitnexusignore`, `.graphifyignore`, and `graphify-out/`.
