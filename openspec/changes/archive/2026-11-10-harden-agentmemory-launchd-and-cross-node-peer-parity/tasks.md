# Tasks

## 1. AgentMemory LaunchAgent Hardening & Mesh Patch Parity

- [x] 1.1 Verify `/usr/sbin:/sbin` in `EnvironmentVariables.PATH` and omission of `AGENTMEMORY_URL` in `~/Library/LaunchAgents/com.agentmemory.server.plist` (`iosteam-mac-mini`) and `local.shb.agentmemory.worker.plist` (`macbook-pro-m5`) to prevent `readMacProcessExecutable()` `/usr/sbin/lsof` `ENOENT` crash loops.
- [x] 1.2 Verify `agentmemory stop` execution before kickstart during `IIPINNED_VERSION` engine upgrades (`0.25.0` -> `0.25.1`), ensuring the updated `iii` compose engine starts without port binding collisions or stale identity locks.
- [x] 1.3 Verify idempotent Mesh Fixes #1 (`syncStartedAt`), #2 (`isAllowedUrl` IPv6 bracket stripping), and #3 (`pinGraphState` in `mem::mesh-remove` and `DELETE /agentmemory/mesh/peers/:id`) in `@agentmemory/agentmemory@0.9.33` `dist/index.mjs` across both `iosteam-mac-mini` and `macbook-pro-m5`.

## 2. Cross-Node Toolchain & Meta Muse Code Alignment on macbook-pro-m5

- [x] 2.1 Verify coding CLI version alignment on `macbook-pro-m5` (`100.106.143.78`): `claude 2.1.322` (single authority), `ntn 0.23.28`, `pnpm 12.18.0`, `browser-use 1.0.0` GA, and `graphify 0.9.105` skill sync.
- [x] 2.2 Configure Meta Muse Code on `macbook-pro-m5` to route inference requests to the central OmniRoute instance at `http://100.70.16.83:20128/v1` via `~/.config/muse/settings.json`.
- [x] 2.3 Enforce mode-`0600` file-backed credentials (`~/.config/muse/auth.json`, `schema_version: 1`, `TBH_CREDENTIAL_BACKEND=file`) on `macbook-pro-m5` with zero keychain prompts.
- [x] 2.4 Verify Tailscale L4 TCP port `3111` bidirectional connectivity for AgentMemory mesh sync between `iosteam-mac-mini` and `macbook-pro-m5`.

## 3. Workstation Maintenance Hardening & Keychain Protection

- [x] 3.1 Enhance `workstation-daily-update.sh` and `workstation_update.py` to terminate stale keychain probers (`security find-generic-password -s gemini`, orphaned `docker-agent serve api`, `docker-credential-osxkeychain`) before touching keychain or running CLI updates.
- [x] 3.2 Ensure npm global update hooks in maintenance runners automatically check and re-apply AgentMemory mesh patches and verify plist `PATH` entries.
- [x] 3.3 Verify macOS `securityd` thread count remains safe (< 15 threads) without deadlock, crash, or `makeUnlocked()` drop.

## 4. Spec Validation & Readiness

- [x] 4.1 Author delta specs for `agentmemory-provider-stability`, `workstation-tailscale-connectivity`, and `workstation-remote-and-agent-permissions` with requirement body text under 450 characters.
- [x] 4.2 Validate change strict readiness via `openspec validate` and `validate-archive-readiness.py --strict`.
