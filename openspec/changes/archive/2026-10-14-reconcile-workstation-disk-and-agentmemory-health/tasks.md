# Tasks

## 1. Safe Volume-Preserving Disk Reclamation

- [x] 1.1 Inspect initial disk headroom on `/System/Volumes/Data` via `df -h`.
- [x] 1.2 Run `docker-disk-guard.sh --prune` and verify BuildKit cache, dangling images, and anonymous volumes are pruned while preserving named volumes (`omniroute-data`, `redis-data`).
- [x] 1.3 Verify post-prune available disk space increases to >24 GiB.

## 2. AgentMemory Healthcheck Authentication Repair

- [x] 2.1 Patch `~/.hermes/scripts/agentmemory-healthcheck.sh` to read `~/.agentmemory/secret` and supply `Authorization: Bearer` on `/agentmemory/health` probes.
- [x] 2.2 Verify probe returns `status: healthy` without 401 error.
- [x] 2.3 Verify `watchdog.log` records consecutive `OK (uptime=...)` entries and eliminates false `launchctl kickstart` restarts.

## 3. Snapshot Store Bounds & Governance Verification

- [x] 3.1 Document memory bounding constraints (`-c pack.windowMemory=1g -c pack.threads=2 --window=10 --depth=10`) for 55MB snapshot history repacking in `docs/runbooks/snapshot-store-growth-management.md`.
- [x] 3.2 Validate change strictly via `openspec validate --strict --json --store openspec-store`.
