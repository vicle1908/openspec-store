# Design

## Context

See `proposal.md - Why` for motivation. Technical constraints and observed workstation state:
- **Storage Headroom**: Host APFS volume `/System/Volumes/Data` reached 97% capacity (only 15 GiB available), triggering warnings from `docker-disk-guard.sh`. Low disk headroom caused high swap thrashing and APFS write delays during automated toolchain operations.
- **AgentMemory Supervisor**: LaunchAgent `com.agentmemory.watchdog` executes `~/.hermes/scripts/agentmemory-healthcheck.sh` every 5 minutes. The script probed `/agentmemory/health` unauthenticated, receiving `401 Unauthorized` and erroneously concluding the server was dead, issuing cyclic `launchctl kickstart` restarts.
- **Git Snapshot Store**: `~/.agentmemory/snapshots` contains 923 commits of a 55 MB `state.json` file. Repacking with unconstrained depth/window on 16 GB Apple Silicon Macs causes swap thrashing.

## Goals / Non-Goals

**Goals:**
- Restore host free disk space from 15 GiB to >24 GiB without touching stateful named volumes.
- Authenticate healthcheck probes against `/agentmemory/health` using `~/.agentmemory/secret` to permanently stop false restart loops.
- Formally document memory bounds for offline snapshot store repacking.

**Non-Goals:**
- Deleting named Docker database volumes (`omniroute-data`, `redis-data`).
- Deleting loose snapshot Git objects via `rm -rf`.
- Disabling the agentmemory supervisor watchdog.

## Decisions

### D1: Safe Volume-Preserving Pruning via `docker-disk-guard.sh --prune`
*Alternative considered*: Running `docker system prune -a --volumes` without guards.
*Decision*: Use `docker-disk-guard.sh --prune`, which executes:
1. `docker image prune -a --filter "until=24h" -f` (removes images unused for >24h).
2. `docker builder prune -f` (purges dangling BuildKit build cache).
3. `docker volume prune -f` (prunes strictly anonymous unreferenced volumes).
*Rationale*: Reclaimed 5.57 GB BuildKit cache and 596 MB dangling images, increasing free space to 27 GiB while guaranteeing zero named volume deletion.

### D2: Secret-Aware Bearer Auth in `agentmemory-healthcheck.sh`
*Alternative considered*: Disabling auth on `/agentmemory/health` or suppressing watchdog restart.
*Decision*: Patch `agentmemory-healthcheck.sh` to read `~/.agentmemory/secret` when readable and pass `-H "Authorization: Bearer $SECRET_TOKEN"`.
*Rationale*: Keeps the REST API securely authenticated while allowing the local launchd supervisor to verify health without false-positive 401 restarts.

### D3: Memory-Bounded Offline Snapshot Repacking Guidelines
*Decision*: Document that Git snapshot stores holding multi-megabyte JSON files must be repacked with memory bounds:
`-c pack.windowMemory=1g -c pack.threads=2 --window=10 --depth=10`.
*Rationale*: Unconstrained window parameters (`window=250 depth=250`) require over 36 GB RAM for 55 MB JSON diffs, causing APFS swap exhaustion on 16 GB machines.

## Risks / Trade-offs

- **Risk: Re-accumulating BuildKit cache**: Ongoing container builds recreate cache objects over time.
  - *Mitigation*: Daily workstation maintenance schedule runs `docker-disk-guard.sh` to maintain headroom.
- **Risk: Plaintext secret exposure in logs**:
  - *Mitigation*: `agentmemory-healthcheck.sh` reads the token directly into memory without printing it to stdout or `watchdog.log`.
