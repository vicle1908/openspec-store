# Proposal

## Why

Host disk utilization on `/System/Volumes/Data` reached 97% (15 GiB free), dropping below the mandatory 30 GiB safeguard threshold established in `docker-resource-access`. In parallel, LaunchAgent `com.agentmemory.watchdog` was executing spurious `launchctl kickstart` restarts every 5 minutes because its healthcheck probe (`~/.hermes/scripts/agentmemory-healthcheck.sh`) lacked Bearer token authorization against `~/.agentmemory/secret`. Addressing both operational debts restores workstation disk headroom and stabilizes the persistent memory server.

## What Changes

- **Safe Volume-Preserving Disk Reclamation**:
  - Execute `~/Developer/scripts/docker-disk-guard.sh --prune` to reclaim dangling images, dangling BuildKit cache, and anonymous volumes while strictly preserving all named volumes (`omniroute-data`, `redis-data`).
  - Restore host free disk space to 27 GiB, bringing the system back into compliance with the 30 GiB headroom operational guideline.
- **AgentMemory Watchdog Healthcheck Authorization**:
  - Patch `~/.hermes/scripts/agentmemory-healthcheck.sh` to check for readable `~/.agentmemory/secret` and supply `Authorization: Bearer <token>` on all `/agentmemory/health` probes.
  - Eliminate the false-positive 401 Unauthorized restart loop and verify consecutive healthy passes.
- **Snapshot Store Repack Memory Bounding Guidelines**:
  - Document that Git-backed snapshot stores containing massive single-file JSON histories (`state.json` ~55 MB) must bound pack memory (`-c pack.windowMemory=1g -c pack.threads=2`) and limit delta depth to prevent APFS swap thrashing on 16 GB developer machines.

## Capabilities

### Modified Capabilities
- `docker-resource-access`: Reconcile automated safe pruning execution and storage headroom recovery evidence.
- `agentmemory-provider-stability`: Mandate bearer token authorization in launchd healthcheck watchdogs when server secrets are present.

## Non-Goals

- Running unconstrained `docker system prune -a --volumes` which would destroy stateful named volumes.
- Deleting loose Git snapshot objects directly via `rm -rf` (prohibited by `snapshot-store-growth-bounds`).
- Removing third-party Homebrew CLI tools without explicit authority approval.

## Affected Ownership Boundaries

- **Workstation Safeguards**: `~/Developer/scripts/docker-disk-guard.sh`.
- **Hermes & AgentMemory Tools**: `~/.hermes/scripts/agentmemory-healthcheck.sh`.
- **Snapshot Store Storage**: `~/.agentmemory/snapshots`.
