# Tasks

## 1. Prepare disk safety baseline

- [x] 1.1 Run a baseline disk inspection capturing host available space on `/System/Volumes/Data` and Docker usage via `docker system df`.
- [x] 1.2 Verify reclaimable storage breakdown (images, containers, anonymous volumes, build cache) and record initial figures.
- [x] 1.3 Document disk safeguard threshold policy (< 30 GiB available) and safe pruning boundaries.

## 2. Implement workstation lifecycle wrapper (`docker-service.sh`)

- [x] 2.1 Create executable script at `~/Developer/scripts/docker-service.sh` with subcommands: `start`, `stop`, `restart`, `status`, `drain`.
- [x] 2.2 Implement `start`: check if daemon is already up (`docker info`); if stopped, invoke official `docker desktop start --timeout 90`; verify socket reachability.
- [x] 2.3 Implement `drain`: execute `docker compose down --timeout 30` for active registered stacks (`~/Omniroute`, `~/Developer/platform/claude-code-provider-adapter`).
- [x] 2.4 Implement `stop`: execute `drain` first, then invoke official `docker desktop stop --timeout 30`; if unsuccessful, support `--force` delegating to `docker desktop stop --force`.
- [x] 2.5 Implement `restart`: invoke `drain`, then `docker desktop restart --timeout 90`, asserting clean socket restoration.
- [x] 2.6 Implement `status` and `status --json`: query official `docker desktop status --format json`, verify `/Users/androidteam/.docker/run/docker.sock` socket existence, check active context (`desktop-linux`), and probe `com.docker.socket` and `com.docker.vmnetd` launchd status.
- [x] 2.7 Verify script handles missing helpers with actionable remediation (`/Applications/Docker.app/Contents/MacOS/install config`).

## 3. Configure native Docker Desktop AutoStart

- [x] 3.1 Safely update `~/Library/Group Containers/group.com.docker/settings-store.json` to set `"AutoStart": true` while preserving existing CPU, memory, and VirtioFS settings.
- [x] 3.2 Verify macOS Login Item `Docker Desktop.app` is registered in `System Events`.
- [x] 3.3 Validate that `AutoStart: true` is respected by querying `settings-store.json` and testing login-readiness without conflicting launchd LaunchAgents.

## 4. Implement compose convention validator (`docker-standardize-check.sh`)

- [x] 4.1 Create `~/Developer/scripts/docker-standardize-check.sh` to scan docker-compose YAML files across `~/Developer` and `~/Omniroute`.
- [x] 4.2 Add rule checking for SQLite databases: flag any host bind mount targeting directories with `.sqlite`, `-wal`, or `-shm` files; assert presence of named volumes.
- [x] 4.3 Add rule checking for development mounts: flag `./src:` or `./:` bind mounts lacking explicit `user: "502:20"` (or `${UID:-502}:${GID:-20}`).
- [x] 4.4 Add rule checking for port bindings: flag ports lacking explicit loopback prefix `127.0.0.1:`.
- [x] 4.5 Ensure the script produces clear PASS/WARN/FAIL reports per stack and returns exit code 0 only when all mandatory rules pass.

## 5. Implement volume-preserving disk guard (`docker-disk-guard.sh`)

- [x] 5.1 Create `~/Developer/scripts/docker-disk-guard.sh` to inspect host disk headroom and issue warnings if free disk is under 30 GiB.
- [x] 5.2 Implement `--prune` mode using official safe pruning commands:
  - `docker image prune -a --filter "until=24h" -f` (prunes unused images older than 24 hours)
  - `docker builder prune -f` (cleans dangling BuildKit cache)
  - `docker volume prune -f` (without `--all`, strictly removing anonymous volumes while preserving named volumes like `omniroute-data`)
- [x] 5.3 Implement pre-prune safety check asserting that no running container is actively using the anonymous volumes being pruned.
- [x] 5.4 Log pruning results, timestamps, and reclaimed byte totals to `~/.docker/disk-guard.log`.

## 6. Verification and integration testing

- [x] 6.1 Test `~/Developer/scripts/docker-service.sh status --json` against the live running Docker Desktop instance and verify output schema.
- [x] 6.2 Execute `~/Developer/scripts/docker-standardize-check.sh` against `~/Omniroute` to confirm named volume (`omniroute-data`) and loopback ports pass validation.
- [x] 6.3 Execute dry-run / status check of `~/Developer/scripts/docker-disk-guard.sh` and verify accurate reporting of host disk space.
- [x] 6.4 Perform a controlled safe prune via `docker-disk-guard.sh --prune` to reclaim storage, and record reclaimed disk space.
- [x] 6.5 Confirm `docker desktop status` remains `running` and `omniroute` remains healthy after execution.

## 7. Documentation and rollback procedures

- [x] 7.1 Document usage of `docker-service.sh`, `docker-standardize-check.sh`, and `docker-disk-guard.sh` in `~/Developer/scripts/README.md`.
- [x] 7.2 Document rollback procedure: reverting `"AutoStart": false` in `settings-store.json`.
- [ ] 7.3 Commit the new change artifacts to Git (optional; changes are already staged in platform/openspec-store).
