# Design

## Context

During recent maintenance runs and cross-node audits between `iosteam-mac-mini` (`100.70.16.83`) and `macbook-pro-m5` (`100.106.143.78`), three specific system-level failure modes were diagnosed:

1. **Launchd AgentMemory Service Crash Loop via Missing `/usr/sbin/lsof`**:
   - In `@agentmemory/agentmemory@0.9.33`, when `com.agentmemory.server.plist` or `local.shb.agentmemory.worker.plist` runs via launchd, launchd provides a minimal system PATH unless overridden in `EnvironmentVariables.PATH`.
   - `readMacProcessExecutable()` in `@agentmemory/agentmemory/dist/cli.mjs` executes `lsof -a -p <pid> -d txt -Fpn`. On macOS, `lsof` resides in `/usr/sbin/lsof`. If `/usr/sbin` is omitted from PATH, `execSync('lsof ...')` throws `ENOENT`.
   - When `ENOENT` occurs, `composePidMatches()` returns `false`, causing the server process to exit with an error stating that the process identity does not match. Because `KeepAlive` is configured, launchd respawns the process every 10 seconds, creating a continuous crash loop and generating excessive system log entries.
   - Setting `AGENTMEMORY_URL` in the server plist causes internal self-directed loopback HTTP checks to fail or recurse, requiring `AGENTMEMORY_URL` to be strictly omitted from managed server plists.

2. **AgentMemory `iii` Engine Pinning & Mesh Patch Synchronization**:
   - When `@agentmemory/agentmemory` upgrades bump `IIPINNED_VERSION` (from `0.25.0` to `0.25.1`), an existing running `iii` engine process holds file descriptors and port bindings. A simple `launchctl kickstart` fails to cleanly terminate the orphaned daemon, leading to port collision. An explicit pre-upgrade stop (`agentmemory stop`) ensures clean handover.
   - Mesh replication requires three critical patches in `dist/index.mjs` across all cluster nodes:
     - **Fix #1 (`syncStartedAt`)**: Proper timestamp tracking to prevent premature mesh sync aborts.
     - **Fix #2 (`isAllowedUrl`)**: Stripping brackets from IPv6 tailnet addresses (`[fd7a:...]`) so URL parsing succeeds.
     - **Fix #3 (`pinGraphState`)**: Awaiting `pinGraphState(state)` in `mem::mesh-remove` and `DELETE /agentmemory/mesh/peers/:id` to prevent unhandled promise rejections during peer pruning.

3. **macOS `securityd` 100-Thread Exhaustion & Mid-Session Lock Cascade**:
   - macOS `/usr/sbin/securityd` has a hard-coded limit of 100 concurrent worker threads.
   - Background IDE processes (such as `~/.gemini/bin/agy --hub` continuously invoking `/usr/bin/security -i` and `find-generic-password`) and orphaned legacy `docker-agent serve api --pull-interval 60` / `docker-credential-osxkeychain` probers queue blocked XPC queries in `securityd`.
   - Once thread count approaches 100, `securityd` logs `securityd has reached its thread limit (100) - service deadlock is possible` and eventually crashes with `Probable bug: error destroying Mutex: 16 / EBUSY`.
   - When `securityd` restarts mid-session, the in-memory unlock key for `~/Library/Keychains/login.keychain-db` is dropped. Every subsequent keychain access blocks in `makeUnlocked()`, displaying modal `SecurityAgent` password dialogs and locking out automated tools.
   - Proactive termination of stale probers during daily maintenance ensures `securityd` threads remain at safe, baseline levels (< 15 threads).

4. **Cross-Node Toolchain & Muse Code Parity on `macbook-pro-m5`**:
   - `macbook-pro-m5` operates as a secondary workstation node on the tailnet (`100.106.143.78`).
   - Meta Muse Code (`muse-code 1.4.14-R7309.1`) must route completions to the central OmniRoute instance on `iosteam-mac-mini` (`http://100.70.16.83:20128/v1`).
   - Per Apple TN3137, file-backed credentials (`~/.config/muse/auth.json`, `schema_version: 1`, mode `0600`) completely bypass `login.keychain-db`, eliminating `SecurityAgent` prompts.
   - Key CLIs must align with canonical versions: `claude 2.1.322`, `ntn 0.23.28`, `pnpm 12.18.0`, `browser-use 1.0.0` GA, and `graphify 0.9.105`.

## Goals / Non-Goals

**Goals:**
- Ensure `com.agentmemory.server.plist` and `local.shb.agentmemory.worker.plist` include `/usr/sbin:/sbin` in `PATH` and omit `AGENTMEMORY_URL`.
- Enforce pre-upgrade `agentmemory stop` and verify Mesh Fixes #1, #2, #3 across `iosteam-mac-mini` and `macbook-pro-m5`.
- Align `macbook-pro-m5` CLI versions, `muse-code` OmniRoute routing, and file-backed credentials (`schema_version: 1`).
- Harden `workstation-daily-update.sh` and `workstation_update.py` to terminate orphaned keychain probers and prevent `securityd` thread exhaustion.

**Non-Goals:**
- Modifying OmniRoute container runtime patches or model routing combos.
- Altering TCC database grants or LaunchDaemon definitions outside the managed scope.

## Decisions

1. **Include `/usr/sbin:/sbin` in LaunchAgent Plists**:
   - *Rationale*: macOS command-line utilities such as `lsof` reside in `/usr/sbin`. Adding `/usr/sbin:/sbin` to `EnvironmentVariables.PATH` in the launchd plist resolves `lsof` directly without modifying vendor code in `@agentmemory/agentmemory`.
2. **Explicit Daemon Teardown on Engine Pin Updates**:
   - *Rationale*: When `IIPINNED_VERSION` changes, the running binary (`iii`) must be replaced. Running `agentmemory stop` terminates the existing engine and frees the listening port before launchd starts the updated binary.
3. **Proactive POSIX Termination of Stale Keychain Probers**:
   - *Rationale*: Stale processes querying the keychain block indefinitely if `securityd` is slow or if user interaction was dismissed. Sending `SIGTERM` / `SIGKILL` to orphaned `security find-generic-password -s gemini` and legacy `docker-agent` processes prior to maintenance prevents `securityd` thread accumulation.

## Risks / Trade-offs

- **[Risk]** Terminating background probers might interrupt an active IDE operation.
  - **Mitigation**: Targeted termination only targets stale `gemini` CLI find-generic-password calls and orphaned `docker-agent` / `docker-credential-osxkeychain` processes that have been orphaned or hanging.
- **[Risk]** Pinned mesh patches could be overwritten on global npm package updates.
  - **Mitigation**: Automated maintenance runners (`workstation-daily-update.sh` and `workstation_update.py`) detect npm global updates of `@agentmemory/agentmemory` and automatically re-apply the three mesh patches.
