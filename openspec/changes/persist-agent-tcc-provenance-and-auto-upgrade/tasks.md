# Tasks: Persist Agent TCC Provenance Across Automated Toolchain Upgrades

- [x] 1. Investigate TCC bypass feasibility <!-- id: 1 -->
  - [x] 1.1 Verify whether root/sudo or programmatic injection can write to TCC.db (confirmed blocked by SIP) <!-- id: 1.1 -->
  - [x] 1.2 Verify whether synthetic GUI automation / computer use can grant TCC permissions (confirmed blocked by SecurityAgent) <!-- id: 1.2 -->
  - [x] 1.3 Audit code-signing designated requirements and `client_type = 1` realpath vs `client_type = 0` bundle attribution across `claude`, `omp`, `goose`, `python3`, and `org.python.python` <!-- id: 1.3 -->
- [ ] 2. Establish persistent local code-signing authority and align target binaries <!-- id: 2 -->
  - [x] 2.1 Generate self-signed Code Signing Certificate (`CN=Developer Agent Code Signing`) <!-- id: 2.1 -->
  - [x] 2.2 Import into macOS login keychain and establish trust (`H"65340d85afd298131c682d8463087891292a2b59"`) <!-- id: 2.2 -->
  - [ ] 2.3 Restore `/opt/homebrew/bin/goose` Cellar symlink (`brew link --overwrite block-goose-cli`), sign target binaries/bundles (`Python.app`, `omp`, `claude`, `goose`), and verify `python3 scripts/tcc_provenance.py --json` under an FDA-authorized supervisor <!-- id: 2.3 -->
- [ ] 3. Harden workspace skill surface hygiene and refresh snapshots <!-- id: 3 -->
  - [ ] 3.1 Update `scripts/sync-workspace-agent-skills.py` (`--accept-refresh` and `--bootstrap-snapshot`) to prune unallowlisted `~/Developer/data/skills` and `~/Developer/agent/skills` directories recreated by `skills update -y`, then run `python3 scripts/sync-workspace-agent-skills.py --bootstrap-snapshot` <!-- id: 3.1 -->
  - [ ] 3.2 Verify `python3 scripts/sync-workspace-agent-skills.py --check` exits `0` with zero `surface_violations` and confirm `.agents/.skill-snapshots/{current,previous}/manifest.json` omits `"description_raw_bytes"` <!-- id: 3.2 -->
- [ ] 4. Wire post-upgrade re-signing, skill pruning, and LaunchAgent TCC handling into both runners <!-- id: 4 -->
  - [ ] 4.1 Add `sign_agent_binary()` / post-`skills update` `data/skills` pruning and non-FDA `TCC.db` `SKIPPED` handling into `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh`, synchronize `/Users/androidteam/Developer/scripts/workstation-daily-update.sh`, and update `/Users/androidteam/Developer/platform/openspec-store/config/script-provenance-manifest.tsv` <!-- id: 4.1 -->
  - [ ] 4.2 Add post-upgrade signing, `data/skills` pruning in `step_skills_refresh()`, and non-FDA `TCC.db` handling in `step_integrity_and_store_validation()` inside `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (with unit tests in `tests/test_workstation_update_workflow.py`) <!-- id: 4.2 -->
  - [ ] 4.3 Verify `bash ~/Developer/scripts/workstation-daily-update.sh --check`, `uv run --project ~/Developer/shb/shb-schedule pytest ~/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py`, and `uv run pytest scripts/test-version-authority-governance.py` pass with zero regressions <!-- id: 4.3 -->
- [x] 5. Complete delta specification and validation <!-- id: 5 -->
  - [x] 5.1 Author delta spec in `specs/portable-workstation-toolchain/spec.md` <!-- id: 5.1 -->
  - [x] 5.2 Validate change via `openspec validate persist-agent-tcc-provenance-and-auto-upgrade --strict --json --store openspec-store` <!-- id: 5.2 -->
