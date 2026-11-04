# Evidence: Enforce Zero-Deferral Workstation Upgrades and Comprehensive Application Lifecycle

## 1. Live Operational Verification Evidence

### 1.1 Complete Zero-Deferral Implementation
- **Mac App Store (`step_mas_update`)**:
  - Eliminated passive skipping of running applications (`skipped_running`) and unconditional skipping of large packages (`skipped_large_bundle`).
  - Added graceful POSIX termination via `terminate_cask_processes((candidate,), timeout=6.0)` for running target applications (e.g. `Telegram 2`, `Slack`).
  - Set generous timeout (`1800s` for large bundles like Xcode `497799835`, `300s` for standard packages) to allow unattended completion.
  - Automatically relaunches active applications post-upgrade in background mode (`open -a "<app_name>" --background`).
  - Returns `restarted` in step telemetry while maintaining backwards-compatible empty lists for `skipped_running` and `skipped_large_bundle`.
- **Homebrew Casks (`step_homebrew_update`)**:
  - Strictly upgraded all outdated casks (`brew upgrade --cask -- <cask>` with `stdin=subprocess.DEVNULL`).
  - Actively terminates running processes using POSIX signals (zero AppleEvents).
  - Automatically relaunches persistent utilities registered in `CASK_RELAUNCH_APPS`.
  - Zero entries recorded in `casks_skipped_running`.
- **Sequential Runner Parity (`workstation-daily-update.sh`)**:
  - Added Mac App Store upgrade automation (`mas outdated` / `mas upgrade`) to both `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh`.
  - Enforced POSIX signal process termination, standard input decoupling (`< /dev/null`), and background relaunching across both Python DBOS and Bash runners.

## 2. Test Suite & Verification Records

### 2.1 `shb-schedule` Test Suite
```bash
cd ~/Developer/shb/shb-schedule && env -u PYTHONPATH uv run pytest -q tests/test_workstation_update_workflow.py
```
Output:
```
..........................................                               [100%]
42 passed in 23.51s
```

Full test suite:
```bash
cd ~/Developer/shb/shb-schedule && env -u PYTHONPATH uv run pytest -q
```
Output:
```
........................................................................ [ 59%]
..................................................                       [100%]
122 passed in 144.10s (0:02:24)
```

### 2.2 `platform/openspec-store` Test Suite
```bash
cd ~/Developer/platform/openspec-store && pytest
```
Output:
```
================== 234 passed, 2 skipped in 104.16s (0:01:44) ==================
```

### 2.3 Live System State & TCC Invariants
- `brew outdated --greedy --json=v2`: `{"formulae": [], "casks": []}` (0 outdated).
- `tcc_provenance.py --bundles`: `status: CLEAN` across all 8 canonical bundles (`client_type = 0`).
- Shell scripts: `bash -n` clean, `diff -u` verified identical parity.

### 2.4 Strict OpenSpec Validation
```bash
openspec validate enforce-no-defer-workstation-upgrades-and-app-lifecycle --type change --store openspec-store --strict
```
Result: strictly valid.
