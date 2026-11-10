# Proposal

## Why

Two critical stability issues and cross-node operational drifts were uncovered during recent workstation operations across `iosteam-mac-mini` (`100.70.16.83`) and `macbook-pro-m5` (`100.106.143.78`):

1. **AgentMemory LaunchAgent Crash-Loops & Upstream Engine Upgrades**:
   - In `@agentmemory/agentmemory` (`0.9.33`), `readMacProcessExecutable()` inside `/dist/cli.mjs` executes `/usr/sbin/lsof -a -p <pid> -d txt -Fpn` to verify the process identity of the running `iii` compose engine. When `com.agentmemory.server.plist` (or `local.shb.agentmemory.worker.plist` on `macbook-pro-m5`) lacks `/usr/sbin:/sbin` in its `EnvironmentVariables.PATH`, `lsof` fails with `ENOENT`. This causes `composePidMatches()` to return `false`, resulting in a continuous launchd crash loop every 10 seconds (`KeepAlive: { SuccessfulExit: false }`) with the diagnostic error:
     `Compose metadata points to PID N, but its process identity does not match the saved engine/file/namespace.`
   - Managed server launchd plists must also omit `AGENTMEMORY_URL` so worker daemons do not crash-loop on self-directed HTTP loopback probes.
   - When global npm upgrades bump the engine pin `IIPINNED_VERSION` (such as `0.25.0` -> `0.25.1`), running daemons must be stopped via `agentmemory stop` prior to `launchctl kickstart` to avoid port collisions and stale engine identity locks.
   - Additionally, bidirectional mesh synchronization requires strict parity for Mesh Fixes #1 (`syncStartedAt`), #2 (`isAllowedUrl` IPv6 bracket stripping), and #3 (`pinGraphState` in `mem::mesh-remove` and `DELETE /agentmemory/mesh/peers/:id`) across both cluster peers.

2. **Cross-Node Toolchain & Meta Muse Code Parity on `macbook-pro-m5`**:
   - `macbook-pro-m5` (`100.106.143.78`) requires strict toolchain parity with `iosteam-mac-mini`: `claude 2.1.322` (single version authority), `ntn 0.23.28`, `pnpm 12.18.0`, `browser-use 1.0.0` GA, and `graphify 0.9.105` skill sync.
   - Meta Muse Code (`muse-code 1.4.14-R7309.1`) on `macbook-pro-m5` must route inference requests across Tailscale to the central OmniRoute gateway at `http://100.70.16.83:20128/v1` via `~/.config/muse/settings.json`, utilizing mode-`0600` file-backed credentials (`~/.config/muse/auth.json`, `schema_version: 1`, `TBH_CREDENTIAL_BACKEND=file`) to avoid macOS keychain prompts.

3. **macOS `securityd` 100-Thread Exhaustion & Mid-Session Lock Cascades**:
   - macOS `securityd` enforces a strict 100-thread ceiling (`securityd has reached its thread limit (100) - service deadlock is possible`).
   - Orphaned background IDE helpers (e.g. `~/.gemini/bin/agy --hub` spawning `/usr/bin/security -i` and `find-generic-password`) and orphaned legacy `docker-agent serve api --pull-interval 60` / `docker-credential-osxkeychain` processes accumulate hanging calls.
   - When `securityd` hits 100 threads, it deadlocks or crashes/restarts, dropping the in-memory unlock state of `login.keychain-db` (`makeUnlocked()`), causing an unlock prompt cascade across all background processes.
   - Workstation daily update runners must proactively terminate these stale probers (`pkill -9 -f "security find-generic-password -s gemini"`, orphaned `docker-credential-osxkeychain`, etc.) to keep thread count well below 100.

## What Changes

- **Harden AgentMemory LaunchAgent Plists & Upgrade Lifecycle**:
  - Ensure `/usr/sbin:/sbin` is present in `EnvironmentVariables.PATH` and `AGENTMEMORY_URL` is omitted in `~/Library/LaunchAgents/com.agentmemory.server.plist` (`iosteam-mac-mini`) and `~/Library/LaunchAgents/local.shb.agentmemory.worker.plist` (`macbook-pro-m5`).
  - Standardize pre-kickstart daemon shutdown (`agentmemory stop`) during engine pin updates.
  - Enforce Mesh Fixes #1, #2, and #3 parity across `@agentmemory/agentmemory@0.9.33` on both nodes.
- **Enforce Cross-Node CLI & Muse Code Parity on `macbook-pro-m5`**:
  - Configure `muse-code 1.4.14-R7309.1` on `macbook-pro-m5` to route to `http://100.70.16.83:20128/v1` with mode-`0600` `~/.config/muse/auth.json` (`schema_version: 1`).
  - Synchronize toolchain versions across `macbook-pro-m5`: `claude 2.1.322`, `ntn 0.23.28`, `pnpm 12.18.0`, `browser-use 1.0.0` GA, and `graphify 0.9.105` skill sync.
- **Prevent `securityd` Thread Exhaustion in Workstation Maintenance**:
  - Update `workstation-daily-update.sh` and `shb_schedule.workflows.workstation_update` to terminate stale `security find-generic-password` and orphaned `docker-credential-osxkeychain` probers prior to keychain operations.

## Non-Goals

- Modifying OmniRoute container runtime patches or model routing combos.
- Altering TCC database tables (`TCC.db`) or `tcc_provenance.py` bundle definitions.
- Changing the primary Tailscale mesh topology or routing preferences.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `agentmemory-provider-stability`: Adds requirements and scenarios for LaunchAgent `PATH` inclusion (`/usr/sbin:/sbin`), `AGENTMEMORY_URL` omission, engine pin upgrade stopping, and mesh patch parity across peers.
- `workstation-tailscale-connectivity`: Adds requirements and scenarios for cross-node Meta Muse Code and coding CLI parity on `macbook-pro-m5`, Tailscale L4 port `3111` mesh reachability, and unified toolchain alignment.
- `workstation-remote-and-agent-permissions`: Updates keychain hygiene requirement with an added scenario requiring workstation maintenance to terminate orphaned keychain probers and prevent `securityd` 100-thread exhaustion.

## Impact

- **Services**:
  - `com.agentmemory.server` LaunchAgent (`iosteam-mac-mini`)
  - `local.shb.agentmemory.worker` LaunchAgent (`macbook-pro-m5`)
  - `securityd` daemon stability on macOS Darwin 27.0.0 (`arm64`)
- **Workstations**:
  - `iosteam-mac-mini` (`100.70.16.83`)
  - `macbook-pro-m5` (`100.106.143.78`)
- **Specifications**:
  - `agentmemory-provider-stability`
  - `workstation-tailscale-connectivity`
  - `workstation-remote-and-agent-permissions`
