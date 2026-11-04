# Proposal: Enforce No-Defer Workstation Upgrades and Comprehensive Application Lifecycle

## Why
Automated workstation maintenance previously permitted passive deferral of running applications and large software packages:
1. `step_homebrew_update` previously deferred active GUI casks to `casks_skipped_running`.
2. `step_mas_update` deferred running Mac App Store applications (`skipped_running`) and unconditionally skipped large bundles such as Xcode (`skipped_large_bundle`).
3. Sequential fallback in `workstation-daily-update.sh` lacked Mac App Store maintenance.

Because background utilities, communication apps, and large IDEs run continuously on developer workstations, passive skipping allowed critical security patches and application updates to lag indefinitely until manual intervention occurred.

## What Changes
Enforce a strict **Zero-Deferral Maintenance Policy** across all workstation package managers and application tiers:
1. **Zero Cask Deferral**: Every outdated Homebrew cask is upgraded. Running processes are gracefully terminated via POSIX `SIGTERM` (with bounded polling and fallback `SIGKILL`), upgraded non-interactively with `stdin=subprocess.DEVNULL`, and background services are automatically relaunched post-upgrade.
2. **Zero Mac App Store Deferral**: Eliminate `skipped_running` and `skipped_large_bundle` in `step_mas_update`. If an outdated App Store application is running (e.g. Telegram 2), terminate it gracefully via POSIX signals, execute `mas upgrade <app_id>` (with generous 1800s timeout for large bundles like Xcode), and relaunch active apps in the background.
3. **Sequential Runner Parity**: Add Mac App Store upgrade automation to `workstation-daily-update.sh` so both DBOS scheduled runs and native fallback runners execute zero-deferral maintenance across Homebrew formulae, Homebrew casks, Mac App Store apps, Bun globals, uv tools, npm globals, and coding agent CLIs.
