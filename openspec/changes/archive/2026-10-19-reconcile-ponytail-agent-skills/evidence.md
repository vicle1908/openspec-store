# Execution Evidence: `reconcile-ponytail-agent-skills`

## 1. Claim-by-Claim Reconciliation Against Immutable Archive `2026-10-19-adopt-ponytail-agent-skills` (`c09d952a`)

| Archived Claim (`2026-10-19-adopt-ponytail-agent-skills`) | Audit Finding | Corrected Implementation & Verified Evidence |
|---|---|---|
| `evidence.md:36-41` reported regex-sliced description lengths (`ponytail=366`, `ponytail-audit=294`, `ponytail-debt=173`, `ponytail-gain=141`, `ponytail-help=75`, `ponytail-review=291`). | The regex dropped the final line of folded YAML (`>`) scalars and omitted trailing newlines. | `sync-workspace-agent-skills.py:measure_description_bytes` decodes YAML folded/literal scalars completely: `ponytail=367` (`366` trimmed), `ponytail-audit=347` (`346` trimmed), `ponytail-debt=202` (`201` trimmed), `ponytail-gain=161` (`160` trimmed), `ponytail-help=142` (`141` trimmed), `ponytail-review=371` (`370` trimmed) UTF-8 bytes—all within the 1,024-byte `skill-index-hygiene` ceiling. |
| `evidence.md:53-58` relied on `~/Developer/.hermes/skills/ponytail*` relative symlinks for Hermes discovery. | Hermes's native loader (`~/.hermes/hermes-agent/agent/skill_utils.py`) ignores `~/Developer/.hermes/skills/` because `~/Developer` has no `.git` and is not in `trusted_project_dirs`. | Added `config/hermes-user-skill-manifest.txt` and `user_hermes_skills` reconciliation in `sync-workspace-agent-skills.py`, creating `~/.hermes/skills/ponytail* -> /Users/androidteam/Developer/.agents/skills/ponytail*`. Verified via Hermes native `_skill_catalog()` probe from `/tmp`. |
| `evidence.md:34-35` recorded `skills-lock.json` (`14` entries) and `.agents/skills-lock.json` (`57` entries) before manual merge. | Native `skills` CLI (`cli.mjs:1093`) writes only `~/Developer/skills-lock.json`, leaving `.agents/skills-lock.json` stale on future updates and unable to recover bytes from `computedHash` alone. | Designated `~/Developer/skills-lock.json` as sole CLI writer, `.agents/skills-lock.json` as generated read-only replica, and initialized `/Users/androidteam/Developer/.agents/.skill-snapshots/current/` (`60` skills, `manifest.json`, `skills-lock.json`, and full `files/<skill>/SKILL.md` payloads) via `--bootstrap-snapshot` / `--accept-refresh` / `--recover-from-snapshot`. |
| `spec.md` Scenario 3.2 claimed graceful degradation on unreachable upstream without captured negative-test proof, and `shb-schedule:step_skills_refresh` double-counted `Updated N skill(s)`. | `step_skills_refresh` regex missed `Updated N skill(s)` and `Multiple current paths match`, and `workstation-daily-update.sh` missed `All global skills are up to date` and `Refreshing N` without completion. | Unified both `workstation-daily-update.sh:classify_refresh` and `shb-schedule:step_skills_refresh` on the 13-case fixture matrix (`F01`–`F13`, including `rc=1` clone failure, `rc=124` timeout, `stderr` `EACCES`, ambiguity-only, and partial-mutation rollback), verified by `unittest` and `pytest`. |

---

## 2. Central Store Verification (`Tasks 1.1–1.4`)

- **Manifest Check (`Task 1.1`)**:
  - `HERMES_MANIFEST_OK count=6 slugs=ponytail,ponytail-audit,ponytail-debt,ponytail-gain,ponytail-help,ponytail-review`
- **Unit Test Suite (`Tasks 1.2 & 1.3`)**:
  - Command: `python3 -m unittest -v /Users/androidteam/Developer/platform/openspec-store/tests/test_ponytail_skill_reconciliation.py`
  - Result: `Ran 5 tests in 1.630s — OK`
    - `test_all_13_canonical_fixtures` (`F01`–`F13` in `/bin/bash`)
    - `test_bootstrap_accept_refresh_drift_detection_and_recovery` (`--bootstrap-snapshot`, `--check` drift detection, `--accept-refresh` rotation `current` $\to$ `previous`, `--recover-from-snapshot` partial-mutation restoration)
    - `test_hermes_symlink_reconciliation_and_non_destructive_preservation`
    - `test_block_scalar_variants_and_budget_helper`
    - `test_real_ponytail_skill_md_byte_measurements` (`ponytail`: 367 raw / 366 trimmed; `ponytail-audit`: 347 / 346; `ponytail-debt`: 202 / 201; `ponytail-gain`: 161 / 160; `ponytail-help`: 142 / 141; `ponytail-review`: 371 / 370 UTF-8 bytes)

---

## 3. External Repository Gate Verification (`Tasks 2.1–2.2`)

- **Packet Validation**:
  - Command: `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/create-external-execution-packet.py validate /Users/androidteam/Developer/platform/openspec-store/openspec/changes/reconcile-ponytail-agent-skills/external-repo-packet-shb-schedule.json --strict`
  - Result: `External Execution Packet: VALID (conforms to schema and contract)`
- **`shb-schedule` Workflow Test Suite**:
  - Command: `/opt/homebrew/bin/uv run --project /Users/androidteam/Developer/shb/shb-schedule pytest /Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py`
  - Result: `36 passed in 38.79s` (including all 13 parametrized `F01`–`F13` canonical fixtures and ANSI/CR stripping).

---

## 4. External Host Gate & Snapshot Bootstrap Verification (`Tasks 3.1–3.2`)

- **Packet Validation**:
  - Command: `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/create-external-execution-packet.py validate /Users/androidteam/Developer/platform/openspec-store/openspec/changes/reconcile-ponytail-agent-skills/external-host-packet.json --strict`
  - Result: `External Execution Packet: VALID (conforms to schema and contract)`
- **Script Provenance Parity**:
  - `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh`: SHA-256 `72b348444b75e0651403409758a746aa1e64857143953f5b9c5e84ed684aa84a`
  - `/Users/androidteam/Developer/scripts/workstation-daily-update.sh`: SHA-256 `72b348444b75e0651403409758a746aa1e64857143953f5b9c5e84ed684aa84a` (`diff -u` exit `0`)
- **Synchronizer & Snapshot Bootstrap**:
  ```text
  user_hermes_skills: created=6 removed=0 conflicts=0 broken=0
  user_hermes_skills.created=ponytail,ponytail-audit,ponytail-debt,ponytail-gain,ponytail-help,ponytail-review
  bootstrap_snapshot=ok
  canonical_direct_roots=111 containers=2 codex_selected=66 claude_selected=25 hermes_selected=6 openspec_targets=12 claude_commands=12 check=True
  malformed_entries=0
  snapshot_check=ok
  ```
- **Snapshot Store**:
  - `/Users/androidteam/Developer/.agents/.skill-snapshots/current/manifest.json` (`56,834` bytes, `60` registry-tracked skills)
  - `/Users/androidteam/Developer/.agents/.skill-snapshots/current/skills-lock.json` (`14,522` bytes)

---

## 5. Native Hermes Loader Discovery & Archive Immutability (`Tasks 4.1–4.2`)

- **Native Hermes Catalog Probe from `/tmp` (Outside `/Users/androidteam/Developer`)**:
  ```text
  HERMES_SEARCH_ROOTS_FROM_TMP: [(1, '/Users/androidteam/.hermes/skills')]
  HERMES_NATIVE_LOADED ponytail load_name=ponytail path=/Users/androidteam/.hermes/skills/ponytail/SKILL.md
  HERMES_NATIVE_LOADED ponytail-audit load_name=ponytail-audit path=/Users/androidteam/.hermes/skills/ponytail-audit/SKILL.md
  HERMES_NATIVE_LOADED ponytail-debt load_name=ponytail-debt path=/Users/androidteam/.hermes/skills/ponytail-debt/SKILL.md
  HERMES_NATIVE_LOADED ponytail-gain load_name=ponytail-gain path=/Users/androidteam/.hermes/skills/ponytail-gain/SKILL.md
  HERMES_NATIVE_LOADED ponytail-help load_name=ponytail-help path=/Users/androidteam/.hermes/skills/ponytail-help/SKILL.md
  HERMES_NATIVE_LOADED ponytail-review load_name=ponytail-review path=/Users/androidteam/.hermes/skills/ponytail-review/SKILL.md
  LINKS_VERIFIED codex_agents 6/6 -> /Users/androidteam/Developer/.agents/skills/ponytail*
  LINKS_VERIFIED claude 6/6 -> /Users/androidteam/Developer/.agents/skills/ponytail*
  LINKS_VERIFIED hermes 6/6 -> /Users/androidteam/Developer/.agents/skills/ponytail*
  LINKS_VERIFIED grok 6/6 -> /Users/androidteam/Developer/.agents/skills/ponytail*
  LINKS_VERIFIED goose 6/6 -> /Users/androidteam/Developer/.agents/skills/ponytail*
  ```
- **Immutable Archive Verification**:
  - Command: `git -C /Users/androidteam/Developer/platform/openspec-store diff --name-only HEAD -- openspec/changes/archive`
  - Result: Empty (`0` modified files under `openspec/changes/archive/`, preserving `2026-10-19-adopt-ponytail-agent-skills` at commit `c09d952a`).
