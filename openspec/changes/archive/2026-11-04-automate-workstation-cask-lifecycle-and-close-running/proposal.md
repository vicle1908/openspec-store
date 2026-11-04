# Proposal: Automate Workstation Cask Lifecycle and Close Running Applications

## Why
Workstation updates in `workstation_update.py` and `workstation-daily-update.sh` historically deferred running casks to `casks_skipped_running` to prevent file locking or abrupt user disruption. However, critical background daemons (such as `tailscale-app`, `docker-desktop`, `cloudflare-warp`, `google-drive`, `onedrive`, and `orca`) run 24/7 on developer workstations. Passively skipping active processes means these tools are never updated during the daily 08:00 AM scheduled run, causing severe version lag and security drift unless an operator intervenes manually.

## What
Transition the maintenance runner from passive process deferral to an **Active Graceful Lifecycle (Teardown, Upgrade, Relaunch)**:
1. For any outdated cask, detect if related processes are active.
2. If active, terminate them gracefully via POSIX `pkill -TERM` with a bounded poll loop (falling back to `pkill -KILL`), avoiding `osascript` to prevent `kTCCServiceAppleEvents` prompts.
3. For `docker-desktop`, coordinate stack draining (`docker-service.sh stop`) and post-upgrade restoration (`docker-service.sh start && up`).
4. Upgrade the cask non-interactively (`brew upgrade --cask -- <cask> < /dev/null`).
5. For daemon/background casks in `CASK_RELAUNCH_APPS`, relaunch them automatically in background mode (`open -a "<App>" --background`).
6. Update telemetry to record updated and restarted casks.
