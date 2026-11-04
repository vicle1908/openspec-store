# Tasks: Automate Workstation Cask Lifecycle and Close Running Applications

## 1. Workstation Update Implementation

- [x] 1.1 Add `terminate_cask_processes(process_names: tuple[str, ...], timeout: float = 6.0)` POSIX signal helper to `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`.
- [x] 1.2 Implement `CASK_RELAUNCH_APPS` mapping and background relaunch loop (`open -a "<App>" --background`) for running casks post-upgrade in `workstation_update.py`.
- [x] 1.3 Update `workstation-daily-update.sh` (and openspec-store mirror) with graceful POSIX termination and stdin decoupling (`< /dev/null`).

## 2. OpenSpec Delta Specification & Validation

- [x] 2.1 Author delta specification in `specs/workstation-toolchain-inventory/spec.md` defining active cask lifecycle, graceful POSIX termination, and automated background relaunching.
- [x] 2.2 Validate change artifacts via `openspec validate automate-workstation-cask-lifecycle-and-close-running --store openspec-store --strict`.

## 3. End-to-End Verification & Archival

- [x] 3.1 Execute `shb-schedule` unit and workflow tests via `env -u PYTHONPATH uv run pytest -q` and assert all pass.
- [x] 3.2 Execute live verification: run dry-run or targeted update verification, verify TCC bundle provenance, toolchain health, and commit all changes.
