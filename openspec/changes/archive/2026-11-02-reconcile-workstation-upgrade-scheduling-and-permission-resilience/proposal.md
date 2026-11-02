# Proposal: Reconcile Workstation Upgrade Scheduling and Permission Prompt Resilience

## Why

Operational verification on `2026-11-01` identified two critical gaps between scheduled maintenance and real workstation upgrade realities:
1. **Uncovered Greedy Casks & Incomplete CLI Self-Updaters in `shb-schedule`**: The scheduled daily DBOS maintenance pipeline in `shb_schedule.workflows.workstation_update` executes `brew outdated --json=v2`, which omits casks specifying `auto_updates: true` (e.g., `docker-desktop`, `chatgpt`, `tailscale-app`, `zed`, `google-drive`, `cloudflare-warp`). Furthermore, `ntn update` only queries the latest version without installing, leaving CLI upgrades unapplied.
2. **Interactive & System-Prompt Interruption during Upgrades**: Inter-process terminations using `osascript -e 'quit app ...'` trigger `kTCCServiceAppleEvents` permission prompts in macOS TCC for unentitled runners. Upgrades to system extension casks (`cloudflare-warp`) invoke interactive prompts in vendor uninstallers unless patched or bypassed. And uncoordinated Docker daemon upgrades fail without pre-flight stack draining.

## What Changes

1. **Greedy Cask Inspection with Safe Process Protection in `shb-schedule`**:
   - Update `workstation_update.py` in `shb-schedule` to pass `--greedy` to `brew outdated --json=v2` so auto-updating casks are visible to automated audits.
   - Expand `CASK_PROCESS_NAMES` dictionary to cover all primary GUI casks (`zed`, `onedrive`, `google-drive`, `cloudflare-warp`, `tailscale-app`, `chatgpt`, `docker-desktop`, `sourcetree`, `lark`).
   - Maintain the safe deferral rule: running applications are recorded in `casks_skipped_running` and skipped during unattended runs.
   - For `docker-desktop`, automate pre-flight compose stack draining and post-upgrade startup via `~/Developer/scripts/docker-service.sh`.
2. **Non-Interactive Self-Update for `ntn`**:
   - Update `STATIC_AGENT_COMMANDS["ntn"]` to execute the official installer pipe `curl -fsSL https://ntn.dev/install.sh | bash` with user local bin destination.
3. **AppleEvents & Permission Prompt Elimination**:
   - Standardize app termination routines on POSIX `pkill -TERM` / `pkill -KILL` instead of `osascript` AppleEvents, eliminating `kTCCServiceAppleEvents` permission requests.
   - Codify non-interactive flags for vendor uninstallers (such as `cloudflare-warp`).
4. **Update OpenSpec Specifications**:
   - Update delta specifications for `workstation-toolchain-inventory` and `workstation-remote-and-agent-permissions` to define the greedy cask audit contract, POSIX signal process drain standard, and non-interactive upgrade resilience.

## Capabilities

### Modified Capabilities
- `workstation-toolchain-inventory`: Require `brew outdated` inventory auditing to support `--greedy` detection with running process safety gates.
- `workstation-remote-and-agent-permissions`: Mandate POSIX signal-based process termination over AppleEvents automation to prevent `kTCCServiceAppleEvents` runtime authorization prompts.

## Non-Goals
- Force-quitting active user applications during scheduled unattended 08:00 runs without a configured drain policy.
- Bypassing macOS System Extensions security dialogs for casks that register kernel or network extensions.
