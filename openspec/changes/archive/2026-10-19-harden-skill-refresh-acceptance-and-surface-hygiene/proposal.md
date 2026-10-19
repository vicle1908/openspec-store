# Proposal

## Why

The DBOS daily skill-refresh step (`shb-schedule:step_skills_refresh`) omits `--accept-refresh` and `--recover-from-snapshot` before running `--check`, and `sync-workspace-agent-skills.py:check_workspace_agent_surface` ignores non-dot directories (`~/Developer/agent/skills` and `~/Developer/data/skills`), allowing stray `Eve` and `AstrBot` skill trees to persist on disk and causing the next real upstream skill update in DBOS to fail parity verification. Remediating these three `/ponytail-review` findings aligns DBOS with the Bash maintenance runner, removes and forbids non-dot project skill trees (`agent/skills` and `data/skills`), and eliminates duplicate `manifest.json` serialization in snapshot writes.

## What Changes

- Update `step_skills_refresh` in `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` so that after `skills update -y` runs, it invokes `sync-workspace-agent-skills.py --accept-refresh` when `failed == 0` (setting `failed = 1` and invoking `--recover-from-snapshot` if acceptance fails) and invokes `--recover-from-snapshot` when `failed > 0`, before running `sync-workspace-agent-skills.py --check`.
- Update `check_workspace_agent_surface` in `/Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` to detect and reject non-dot project skill trees (`~/Developer/agent`, `~/Developer/agent/skills`, and `~/Developer/data/skills`) in addition to root `skills/` and unallowlisted dot-directories, while preserving unrelated subdirectories under `~/Developer/data/` (`updates/`, `quarantine/`, `capture-spool/`, `state_store.db/`, `stream_store/`).
- Prune the stray `/Users/androidteam/Developer/agent` (`temporal-developer`, `temporal-ops` duplicates) and `/Users/androidteam/Developer/data/skills` (`gws-*` and `temporal-*` symlinks) trees so `skills` CLI (`cli.mjs:1479,1672`) no longer falsely detects `AstrBot` or `Eve` as installed project agents in `~/Developer/`.
- Simplify `accept_or_bootstrap_snapshot` in `scripts/sync-workspace-agent-skills.py` to compute `total_bytes` over the snapshotted skill files and `skills-lock.json` and write `manifest.json` once instead of serializing and writing it twice.

## Non-Goals

- Modifying `/Users/androidteam/Developer/data/updates/` or any non-skill subdirectory inside `/Users/androidteam/Developer/data/`.
- Changing the 13-case `_classify_skills_refresh_output` / `classify_refresh` parser regexes (`F01`–`F13`).
- Editing any archived OpenSpec change under `openspec/changes/archive/` (`2026-10-19-adopt-ponytail-agent-skills` and `2026-10-19-reconcile-ponytail-agent-skills` remain immutable).

## Affected Ownership Boundaries

- **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: `scripts/sync-workspace-agent-skills.py`, `tests/test_ponytail_skill_reconciliation.py`, and delta specifications for `ecosystem-tooling-and-skills-upgrade` and `workspace-topology-and-hygiene`.
- **External Repository (`/Users/androidteam/Developer/shb/shb-schedule`)**: `src/shb_schedule/workflows/workstation_update.py` (`step_skills_refresh`) and `tests/test_workstation_update_workflow.py` (governed by an External Repository Execution Packet).
- **External Host Workspace (`/Users/androidteam/Developer`)**: Removal of stray `/Users/androidteam/Developer/agent` and `/Users/androidteam/Developer/data/skills` trees and refresh of `/Users/androidteam/Developer/.agents/.skill-snapshots/{current,previous}/` (governed by an External Host Execution Packet).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ecosystem-tooling-and-skills-upgrade`: Require the DBOS `step_skills_refresh` workflow step to execute `--accept-refresh` on healthy refreshes and `--recover-from-snapshot` on failed refreshes prior to `--check` parity verification.
- `workspace-topology-and-hygiene`: Require `check_workspace_agent_surface` to reject non-dot project skill trees (`~/Developer/agent`, `~/Developer/agent/skills`, and `~/Developer/data/skills`) while preserving legitimate `~/Developer/data/updates/` telemetry directories.

## Impact

- Upstream skill updates executed by the 08:00 AM DBOS `workstation-daily-update` job promote `.skill-snapshots/{current,previous}/` and `.agents/skills-lock.json` before running `--check`, preventing false `DEGRADED` parity failures on real updates.
- Removing `~/Developer/agent` and `~/Developer/data/skills` stops `/opt/homebrew/bin/skills` from targeting uninstalled `AstrBot` and `Eve` agents during project skill updates.
- Snapshot writes perform one `manifest.json` serialization and disk write per generation.
