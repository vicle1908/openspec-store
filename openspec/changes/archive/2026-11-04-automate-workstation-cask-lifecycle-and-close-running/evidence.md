# Evidence: Automate Workstation Cask Lifecycle and Active Process Teardown

## 1. Live Operational Verification Evidence

### 1.1 Root-Cause Validation & Policy Elimination
- **Defect in Passive Deferral**: When daemons and continuous developer tools (`Tailscale`, `Docker Desktop`, `OneDrive`, `Google Drive`, `Cloudflare WARP`, `Orca`, `Zed`) are running 24/7, skipping them via `casks_skipped_running` caused them to lag permanently behind upstream releases during unattended daily 08:00 AM runs.
- **Active Graceful Lifecycle Implemented**:
  1. Identified outdated casks (`tailscale-app` 1.104.4 -> 1.104.5, `droid` 1.2.0 -> 1.3.0).
  2. Targeted active process `Tailscale` (PID 61410).
  3. Terminated gracefully via POSIX `pkill -TERM -x Tailscale` with zero `osascript` calls, avoiding `kTCCServiceAppleEvents` prompts.
  4. Successfully executed non-interactive upgrade via `brew upgrade --cask tailscale-app droid < /dev/null`.
  5. Automatically relaunched `Tailscale` in the background (`open -a "Tailscale" --background`), restoring PID 43958.
  6. Verified `brew outdated --greedy --json=v2` returned zero outdated casks.

### 1.2 Automated Workflow Invariant Assertions
- Updated `shb_schedule.workflows.workstation_update.step_homebrew_update()`:
  - Calls `terminate_cask_processes(process_names, timeout=6.0)` using POSIX signals.
  - Automatically relaunches casks registered in `CASK_RELAUNCH_APPS`.
  - Captures `casks_restarted` in the returned telemetry dictionary.
- Updated shell fallback script `workstation-daily-update.sh` with identical POSIX termination, stdin decoupling (`< /dev/null`), and background utility relaunching.

## 2. Test Suite & Verification Records

### 2.1 `shb-schedule` Test Suite
```bash
cd ~/Developer/shb/shb-schedule && env -u PYTHONPATH uv run pytest -q
```
Result: **122 passed in 143.82s (100%)**

### 2.2 TCC Bundle Provenance
```bash
/opt/homebrew/opt/python@3.15/bin/python3.15 ~/Developer/platform/openspec-store/scripts/tcc_provenance.py --bundles --json
```
Result: **`status: CLEAN`** across all 8 canonical bundles (`client_type = 0`).

### 2.3 Strict OpenSpec Validation
```bash
openspec validate automate-workstation-cask-lifecycle-and-close-running --type change --store openspec-store --strict
```
Result: Change is strictly valid.
