# Execution Evidence: `harden-skill-refresh-acceptance-and-surface-hygiene`

## 1. Central Store Surface Hygiene and Single-Pass Snapshot Write (`Task 1.1`)

- **Changes**:
  - Updated `check_workspace_agent_surface` in `/Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py:383-405` to reject `skills`, `agent`, `agent/skills`, and `data/skills` while allowing `data/updates/`.
  - Removed the duplicate `description_raw_bytes` key and duplicate `manifest.json` serialization/write in `accept_or_bootstrap_snapshot` (`sync-workspace-agent-skills.py:615-672`).
- **Unit Test Verification**:
  - Command: `python3 -m unittest -v /Users/androidteam/Developer/platform/openspec-store/tests/test_ponytail_skill_reconciliation.py`
  - Output:
    ```text
    test_all_13_canonical_fixtures ... ok
    test_bootstrap_accept_refresh_drift_detection_and_recovery ...
      surface_violations=agent,data/skills
      ok
    test_hermes_symlink_reconciliation_and_non_destructive_preservation ... ok
    test_block_scalar_variants_and_budget_helper ... ok
    test_real_ponytail_skill_md_byte_measurements ... ok
    ----------------------------------------------------------------------
    Ran 5 tests in 2.155s
    OK
    ```

## 2. DBOS `step_skills_refresh` Post-Refresh Acceptance Wiring (`Task 2.1`)

- **External Repository Execution Packet**:
  - Path: `openspec/changes/harden-skill-refresh-acceptance-and-surface-hygiene/external-repo-packet-shb-schedule.json`
  - Validation: `External Execution Packet: VALID (conforms to schema and contract)`
- **Test Verification (`shb/shb-schedule`)**:
  - Command: `/opt/homebrew/bin/uv run --project /Users/androidteam/Developer/shb/shb-schedule pytest /Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py`
  - Output: `37 passed in 46.21s` (including `test_step_skills_refresh_accept_and_recover_when_snapshot_exists` verifying `--accept-refresh` $\to$ `--check` on healthy updates and `--recover-from-snapshot` $\to$ `--check` on failed updates).

## 3. External Host Stray Directory Pruning and Verification (`Task 3.1`)

- **External Host Execution Packet**:
  - Path: `openspec/changes/harden-skill-refresh-acceptance-and-surface-hygiene/external-host-packet.json`
  - Validation: `External Execution Packet: VALID (conforms to schema and contract)`
- **Pruning & Verification Output**:
  ```text
  PRUNED_DATA_SKILLS_OK
  PRUNED_AGENT_SKILLS_OK
  DATA_UPDATES_PRESERVED_OK
  accept_refresh=ok
  canonical_direct_roots=111 containers=2 codex_selected=66 claude_selected=25 hermes_selected=6 openspec_targets=12 claude_commands=12 check=True
  malformed_entries=0
  snapshot_check=ok
  ```
- **Skills Update Verification**:
  - `/opt/homebrew/bin/skills update ponytail -y` exited `0` (`✓ All project skills are up to date`), `Eve` is completely eliminated from the `Updating for:` banner, and `~/Developer/data/skills` and `~/Developer/agent` remain absent after update while `~/Developer/data/updates/2026-10-19.json` is preserved.
