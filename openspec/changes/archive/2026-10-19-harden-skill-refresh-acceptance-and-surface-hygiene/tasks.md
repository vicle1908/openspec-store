# Tasks

## 1. Central Store Surface Hygiene and Snapshot Lean Cleanup (`platform/openspec-store`)

- [x] 1.1 Update `check_workspace_agent_surface` and `accept_or_bootstrap_snapshot` in `/Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` to (a) detect and reject non-dot `agent`, `agent/skills`, and `data/skills` directories in the workspace root while allowing `data/updates/`, and (b) remove the duplicate `description_raw_bytes` key and write `manifest.json` in a single pass; verify with unit tests in `/Users/androidteam/Developer/platform/openspec-store/tests/test_ponytail_skill_reconciliation.py`.

## 2. DBOS `step_skills_refresh` Post-Refresh Acceptance Wiring (`shb/shb-schedule`)

- [x] 2.1 Prepare and validate an External Repository Execution Packet for `/Users/androidteam/Developer/shb/shb-schedule` scoping edits to `src/shb_schedule/workflows/workstation_update.py` and `tests/test_workstation_update_workflow.py`, then update `step_skills_refresh` so when `snap_manifest.is_file()` is true it invokes `sync-workspace-agent-skills.py --accept-refresh` when `failed == 0` (setting `failed = 1` and invoking `--recover-from-snapshot` if acceptance fails) and invokes `--recover-from-snapshot` when `failed > 0` before running `--check`; add `test_step_skills_refresh_accept_and_recover_when_snapshot_exists` and verify via `uv run --project /Users/androidteam/Developer/shb/shb-schedule pytest /Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py`.

## 3. External Host Stray Directory Pruning and Verification

- [x] 3.1 Prepare and validate an External Host Execution Packet scoping removal strictly to `/Users/androidteam/Developer/agent` and `/Users/androidteam/Developer/data/skills` (explicitly excluding `/Users/androidteam/Developer/data/updates/` and all other `~/Developer/data/*` subdirectories), remove those two stray skill trees, run `sync-workspace-agent-skills.py --accept-refresh` and `--check`, verify `/opt/homebrew/bin/skills update ponytail -y` reports `Updating for: Universal, Claude Code, Hermes Agent` (without `AstrBot` or `Eve`), and record verification in `evidence.md`.

## Workflow follow-up

- Validate the change strictly via `/Users/androidteam/.npm-global/bin/openspec validate harden-skill-refresh-acceptance-and-surface-hygiene --strict --json --store openspec-store`.
- Archive `harden-skill-refresh-acceptance-and-surface-hygiene` after all tasks and external execution gates are complete and verified.
