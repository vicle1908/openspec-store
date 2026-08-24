## Problem Statement

There is no mechanism to know when a new upstream OmniRoute release is available. The current update approach requires the user to manually check Docker Hub, remember to update, and run the pull+up command — a process that relies entirely on human memory and provides no safety net.

## Why

The `standardize-omniroute-docker-deployment` change established on-demand Docker updates (`docker compose pull && up -d --no-build`) but did not add any tracking. The `harden-omniroute-docker-per-official-guide` change aligned with the official guide but the update workflow remained manual-only. A comparison of the running image digest against Docker Hub confirmed a new upstream version already exists (local `sha256:92c768c...` vs remote `sha256:2bf79cf...`) — invisible without explicit checking.

## What Changes

- **`~/Omniroute/scripts/check-upstream.sh`** — a lightweight check script that compares the running image digest against Docker Hub's registry API and writes a flag file (`~/.omniroute/update-available`) + macOS notification when a new version is detected. Idempotent, safe to run frequently, no side effects when up-to-date.
- **`~/Omniroute/scripts/update.sh`** — a manual update script that wraps the full lifecycle: snapshot current DB → pull new image → deploy → wait for healthy → verify endpoints → record new digest → clear flag → notify. Run when the user chooses to apply an available update.
- **`com.omniroute.update-check` LaunchAgent** — runs `check-upstream.sh` twice daily (43200s), logging to `~/.omniroute/update-check.log`. The user sees a macOS notification when an update is available; the actual update is always manual (the user decides when to apply).
- **`~/.omniroute/update-available` flag file** — ephemeral notification state: present = update available, absent = up-to-date. Checked by `update.sh` to gate the update flow.

## Non-Goals

- No auto-update (the user decides when to apply, per the previous on-demand decision).
- No CI/CD pipeline or webhook listener (single-machine deployment; polling is sufficient).
- No pre-deploy testing of the new image (the app handles DB migrations internally; rollback via snapshot is the safety net).
- No image pinning in the override (the user can pin `diegosouzapw/omniroute:3.x` in the override if stability is preferred over `latest`).

## Capabilities

### New Capabilities

None — operational tooling only.

### Modified Capabilities

None — no spec-level behavior changes.

**skip_specs: true** — Pure operational tooling. No API contracts, user-facing behavior, or spec-level requirements change.

## Impact

- **New files**: `~/Omniroute/scripts/check-upstream.sh` + `update.sh` (not tracked by git; deployment-owned scripts).
- **New LaunchAgent**: `~/Library/LaunchAgents/com.omniroute.update-check.plist` (runs twice daily).
- **New log files**: `~/.omniroute/update-check.log`, `~/.omniroute/update.log`, `~/.omniroute/snapshots/`.
- **New flag file**: `~/.omniroute/update-available` (ephemeral, present only when update exists).
- **Store config.yaml**: OmniRoute section updated to document the tracking mechanism.
