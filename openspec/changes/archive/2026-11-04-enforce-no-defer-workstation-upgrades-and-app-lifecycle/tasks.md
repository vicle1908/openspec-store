# Tasks: Enforce Zero-Deferral Workstation Upgrades and Comprehensive Application Lifecycle

## 1. Zero-Deferral Implementation in `shb-schedule`

- [x] 1.1 In `shb_schedule.workflows.workstation_update.step_mas_update`: eliminate `skipped_running` and `skipped_large_bundle` deferrals, implement graceful POSIX teardown for running App Store applications, upgrade via `mas upgrade <app_id>` (with 1800s timeout for large bundles like Xcode), and relaunch active apps in background post-upgrade.
- [x] 1.2 In `shb_schedule.workflows.workstation_update.step_homebrew_update`: ensure all outdated casks are upgraded via `terminate_cask_processes()` POSIX teardown, `stdin=subprocess.DEVNULL`, and `CASK_RELAUNCH_APPS` background relaunching, maintaining zero entries in `casks_skipped_running`.
- [x] 1.3 Update sequential runner `workstation-daily-update.sh` (and openspec-store mirror) to include `mas outdated` / `mas upgrade` application updates, ensuring complete upgrade parity between scheduled DBOS runs and native fallback runs.

## 2. Specification & Validation

- [x] 2.1 Author delta specification in `specs/workstation-toolchain-inventory/spec.md` codifying zero-deferral across Homebrew formulae, Homebrew casks, Mac App Store applications, Bun globals, uv tools, npm globals, and agent CLIs.
- [x] 2.2 Validate change artifacts via `openspec validate enforce-no-defer-workstation-upgrades-and-app-lifecycle --store openspec-store --strict`.

## 3. End-to-End Verification & Archival

- [x] 3.1 Run `shb-schedule` test suite (`env -u PYTHONPATH uv run pytest -q`) and verify all tests pass.
- [x] 3.2 Run `openspec-store` test suite (`pytest`) and verify all 234+ tests pass.
- [x] 3.3 Verify live system state (`brew outdated --greedy --json=v2`, `mas outdated`, `tcc_provenance.py --bundles`).
- [x] 3.4 Archive OpenSpec change, commit all repositories, and persist memories to AgentMemory, Notion, and OMP.
