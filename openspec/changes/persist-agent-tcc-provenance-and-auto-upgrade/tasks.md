# Tasks: Persist Agent TCC Provenance Across Automated Toolchain Upgrades

- [x] 1. Investigate TCC bypass feasibility <!-- id: 1 -->
  - [x] 1.1 Verify whether root/sudo or programmatic injection can write to TCC.db (confirmed blocked by SIP) <!-- id: 1.1 -->
  - [x] 1.2 Verify whether synthetic GUI automation / computer use can grant TCC permissions (confirmed blocked by SecurityAgent) <!-- id: 1.2 -->
  - [x] 1.3 Audit code-signing designated requirements across active coding agent CLIs (`claude`, `omp`, `goose`) <!-- id: 1.3 -->
- [x] 2. Establish persistent local code-signing authority <!-- id: 2 -->
  - [x] 2.1 Generate self-signed Code Signing Certificate (`CN=Developer Agent Code Signing`) <!-- id: 2.1 -->
  - [x] 2.2 Import into macOS login keychain and establish trust (`H"65340d85afd298131c682d8463087891292a2b59"`) <!-- id: 2.2 -->
  - [x] 2.3 Test-sign target binaries (`goose`, `omp`, `claude`) and verify invariant Designated Requirements <!-- id: 2.3 -->
- [x] 3. Clean workspace surface hygiene <!-- id: 3 -->
  - [x] 3.1 Remove forbidden legacy `~/Developer/data/skills` directory <!-- id: 3.1 -->
  - [x] 3.2 Verify `sync-workspace-agent-skills.py --check` passes cleanly with zero violations <!-- id: 3.2 -->
- [ ] 4. Wire post-upgrade re-signing automation into maintenance runner <!-- id: 4 -->
  - [ ] 4.1 Add `sign_agent_binary()` helper into `~/Developer/scripts/workstation-daily-update.sh` Stage 5 / Stage 10 <!-- id: 4.1 -->
  - [ ] 4.2 Verify `workstation-daily-update.sh --check` executes without syntax or logic regressions <!-- id: 4.2 -->
- [ ] 5. Complete delta specification and validation <!-- id: 5 -->
  - [ ] 5.1 Author delta spec in `specs/portable-workstation-toolchain/spec.md` <!-- id: 5.1 -->
  - [ ] 5.2 Validate change via `openspec validate --store openspec-store --changes persist-agent-tcc-provenance-and-auto-upgrade` <!-- id: 5.2 -->
