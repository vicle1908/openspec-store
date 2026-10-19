# Design

## Context

See `proposal.md` — Why for motivation.

A `/ponytail-review` audit of the committed `reconcile-ponytail-agent-skills` implementation (`697a98d7` in `platform/openspec-store` and `ad9323b` in `shb/shb-schedule`) identified three concrete issues verified against the live filesystem:

1. **DBOS `step_skills_refresh` Missing `--accept-refresh` Before `--check`**:
   - In `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py:L625-642`, `step_skills_refresh` runs `skills update -y` and immediately invokes `sync-workspace-agent-skills.py --check`.
   - When an upstream skill updates (`refreshed > 0`), `skills update -y` modifies `~/Developer/.agents/skills/<name>/SKILL.md` and `~/Developer/skills-lock.json`, leaving `~/Developer/.agents/skills-lock.json` and `~/Developer/.agents/.skill-snapshots/current/` at the previous generation until `--accept-refresh` runs.
   - Because `--check` compares live files and lockfiles against `.skill-snapshots/current/manifest.json` (`sync-workspace-agent-skills.py:L947-958`), calling `--check` without calling `--accept-refresh` first guarantees `parity_valid = False` whenever any skill updates!
2. **Non-Dot `agent/skills` (`Eve`) and `data/skills` (`AstrBot`) Directories Bypassing `check_workspace_agent_surface`**:
   - On disk, `/Users/androidteam/Developer/agent/skills/{temporal-developer,temporal-ops}` and `/Users/androidteam/Developer/data/skills/{gws-*,temporal-*}` exist from earlier `skills add` runs on Oct 14–15.
   - Because `check_workspace_agent_surface` (`sync-workspace-agent-skills.py:L392`) skipped non-dot directories (`if not entry.name.startswith("."): continue`), both directories went undetected, causing `/opt/homebrew/bin/skills` (`cli.mjs:1479,7958`) to falsely detect `AstrBot` and `Eve` as active project agents in `~/Developer/`.
3. **Duplicate `manifest.json` Serialization in `accept_or_bootstrap_snapshot`**:
   - `sync-workspace-agent-skills.py:L615-617,L659-675` stores `desc_metrics["raw_bytes"]` under two identical keys (`description_bytes` and `description_raw_bytes`) and serializes/writes `manifest.json` twice just to include `len(manifest_bytes)` in `total_bytes`.

## Goals / Non-Goals

**Goals:**
- Wire `shb-schedule:step_skills_refresh` to invoke `sync-workspace-agent-skills.py --accept-refresh` on healthy `skills update -y` runs (and `--recover-from-snapshot` on failed runs or failed acceptance) before running `--check`.
- Extend `check_workspace_agent_surface` in `sync-workspace-agent-skills.py` to flag `agent`, `agent/skills`, and `data/skills` in `~/Developer/`, and remove the stray `/Users/androidteam/Developer/agent` and `/Users/androidteam/Developer/data/skills` trees while preserving `/Users/androidteam/Developer/data/updates/` and all other `~/Developer/data/` subdirectories.
- Simplify `accept_or_bootstrap_snapshot` to write `manifest.json` once and drop the duplicate `description_raw_bytes` key.

**Non-Goals:**
- Touching `/Users/androidteam/Developer/data/updates/` or any non-skill data in `/Users/androidteam/Developer/data/`.
- Modifying `openspec/changes/archive/`.

## Decisions

### Decision 1: Align `shb-schedule:step_skills_refresh` Post-Refresh Lifecycle with `workstation-daily-update.sh`
- **Choice:** In `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py:step_skills_refresh`:
  1. Define `snap_manifest = workspace_dir / ".agents" / ".skill-snapshots" / "current" / "manifest.json"`.
  2. After `skills update -y` completes and `_classify_skills_refresh_output` runs, if `parity_script.exists()` and `snap_manifest.is_file()`:
     - When `failed == 0`: invoke `["python3", str(parity_script), "--accept-refresh"]`. If `accept_proc.returncode != 0`, set `failed = max(failed, 1)`, append `"Post-refresh skill acceptance verification failed"` to `errors`, and invoke `["python3", str(parity_script), "--recover-from-snapshot"]`.
     - When `failed > 0`: invoke `["python3", str(parity_script), "--recover-from-snapshot"]`.
  3. Then invoke `["python3", str(parity_script), "--check"]` to compute `parity_valid`.
- **Rationale:** Matches `workstation-daily-update.sh:L204-219`, promotes the snapshot and `.agents/skills-lock.json` replica before `--check` runs whenever `.skill-snapshots/current/manifest.json` is present on the host, and preserves backward compatibility with unit tests that mock `step_skills_refresh` in a bare `tmp_path` without a snapshot store while adding `test_step_skills_refresh_accept_and_recover_when_snapshot_exists` for the full snapshot lifecycle.
- **Alternatives Considered:** Calling `--accept-refresh` even when no snapshot store or `skills-lock.json` exists in `tmp_path`. Rejected because bare `tmp_path` parser tests mock only `[skills update -y, sync-workspace-agent-skills.py --check]`.

### Decision 2: Reject Non-Dot `agent` and `data/skills` Trees in `check_workspace_agent_surface` and Prune Stray Host Copies
- **Choice:**
  1. In `sync-workspace-agent-skills.py:check_workspace_agent_surface(workspace)`, explicitly check for `workspace / "agent"`, `workspace / "agent" / "skills"`, and `workspace / "data" / "skills"` in addition to `workspace / "skills"` and unallowlisted dot-directories (`!<allowed>*/skills`).
  2. Under an External Host Execution Packet, remove `/Users/androidteam/Developer/agent/skills/{temporal-developer,temporal-ops}` (and the empty `/Users/androidteam/Developer/agent` directory) and `/Users/androidteam/Developer/data/skills/{gws-*,temporal-*}` (and the empty `/Users/androidteam/Developer/data/skills` directory), leaving `/Users/androidteam/Developer/data/updates/` and all other `/Users/androidteam/Developer/data/*` entries untouched.
- **Rationale:** Both `temporal-*` and `gws-*` are already canonically installed in `/Users/androidteam/Developer/.agents/skills/` and symlinked into `.claude/skills/` and `.hermes/skills/`. Removing the stray `agent` (`Eve`) and `data/skills` (`AstrBot`) trees satisfies `workspace-topology-and-hygiene` and stops `skills` CLI from detecting `AstrBot` and `Eve`.

### Decision 3: Single-Pass `manifest.json` Write in `accept_or_bootstrap_snapshot`
- **Choice:** Compute `total_bytes` as the sum of snapshotted skill file sizes plus `len(root_lock_bytes)`, remove the redundant `description_raw_bytes` key (retaining `description_bytes` and `description_trimmed_bytes`), and serialize/write `manifest.json` once.
- **Rationale:** Eliminates 12 lines of duplicate serialization and disk I/O with zero loss of information.

## Risks / Trade-offs

- **[Risk] Removing `~/Developer/data/skills` could accidentally affect `~/Developer/data/updates/` if scoped too broadly** → Mitigation: Scope removal strictly to `/Users/androidteam/Developer/data/skills` and `/Users/androidteam/Developer/agent`, and verify `/Users/androidteam/Developer/data/updates/2026-10-19.json` remains intact before and after.

## Migration Plan

1. **Central Store (`platform/openspec-store`)**:
   - Update `check_workspace_agent_surface` and `accept_or_bootstrap_snapshot` in `scripts/sync-workspace-agent-skills.py`.
   - Add unit test coverage in `tests/test_ponytail_skill_reconciliation.py` asserting that `agent/skills` and `data/skills` trigger `surface_violations` while `data/updates` is allowed.
2. **External Repository (`shb/shb-schedule`)**:
   - Update `step_skills_refresh` in `src/shb_schedule/workflows/workstation_update.py` and `tests/test_workstation_update_workflow.py` (testing both healthy `--accept-refresh` + `--check` and failed `--recover-from-snapshot` + `--check` call sequences).
3. **External Host (`/Users/androidteam/Developer`)**:
   - Remove `/Users/androidteam/Developer/data/skills` (8 symlinks + dir) and `/Users/androidteam/Developer/agent` (2 duplicate skill dirs + dir), re-run `sync-workspace-agent-skills.py --accept-refresh` and `--check`, and verify `/opt/homebrew/bin/skills update ponytail -y` prints `Updating for: Universal, Claude Code, Hermes Agent` (without `AstrBot` or `Eve`).
