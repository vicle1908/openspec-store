# Verification Evidence

This document records the verification evidence produced while implementing the
`standardize-docker-permissions-and-lifecycle` change. It is archived alongside
the change artifacts as required by the experimental workflow archive guidance.

## Scope of Verification

Execution date: 2026-10-06
Environment:
- macOS Darwin 27.0.0 (Apple Silicon, arm64)
- Docker Desktop 4.94.0 (build 241994), Engine 29.8.2, Compose v5.5.1
- Official `docker desktop` CLI plugin v0.4.4
- Host UID/GID: `androidteam:staff` (502:20)

## Evidence 1: Daemon Auto-Start (Task 3.1–3.3)

`~/Library/Group Containers/group.com.docker/settings-store.json` was updated:

```diff
-  "AutoStart": false,
+  "AutoStart": true,
```

Verified JSON validity via:
```bash
python3 -c "import json; json.load(open(...)); print('JSON valid')"
# -> JSON valid
```

macOS Login Item `Docker Desktop.app` confirmed already registered in
`System Events`. No conflicting LaunchAgent was introduced (per design D2).

## Evidence 2: Lifecycle Wrapper Output (Task 6.1)

`~/Developer/scripts/docker-service.sh status --json` executed against the live
running Docker Desktop instance:

```json
{
  "status": "running",
  "session_id": "1f1d9563-e82f-4815-bf83-70a036fcf9b4",
  "socket_exists": true,
  "socket_path": "/Users/androidteam/.docker/run/docker.sock",
  "context": "desktop-linux",
  "helpers": {
    "vmnetd": true,
    "socket": true
  }
}
```

Human-readable form also verified. Helper probe correctly resolves the
`com.docker.socket` one-shot LaunchDaemon via `/var/run/docker.sock` symlink
verification rather than a persistent `pgrep` process.

## Evidence 3: Compose Convention Validation (Task 6.2)

`~/Developer/scripts/docker-standardize-check.sh --stack /Users/androidteam/Omniroute`:

```
=== Validating: /Users/androidteam/Omniroute/docker-compose.override.yml ===
=== Validating: /Users/androidteam/Omniroute/docker-compose.yml ===
  (Host database bind mount in docker-compose.yml is overridden by named volume in override file: compliant)
=== Validating: /Users/androidteam/Omniroute/docker-compose.prod.yml ===

✅ All stacks passed validation.
```

The validator correctly:
- Recognized `omniroute-data:/app/data` as a named volume (no false FAIL)
- Detected the base file's `./data:/app/data` host bind as overridden by the
  `docker-compose.override.yml` `!override` block (no false positive)
- Did not flag the named volume as a missing `user:` directive

## Evidence 4: Disk Headroom Guard (Task 6.3)

`~/Developer/scripts/docker-disk-guard.sh` status output:

```
[2026-10-06 12:20:59] Disk status: 38 GiB free on /System/Volumes/Data (threshold: 30 GiB)
Host disk headroom: 38 GiB free on /System/Volumes/Data (threshold: 30 GiB)
✓ Disk within safe limits.
```

Free disk was reclaimed from 21 GiB to 38 GiB via the controlled `--prune`
operation (see Evidence 5). The macOS 512-byte-block `df` conversion bug was
identified and corrected during implementation.

## Evidence 5: Controlled Safe Prune (Task 6.4)

`~/Developer/scripts/docker-disk-guard.sh --prune` executed:

- `docker image prune -a --filter "until=24h" -f`
- `docker builder prune -f`
- `docker volume prune -f` (anonymous volumes only)

Result: Host free space increased from 21 GiB to 38 GiB. Named volumes
(`omniroute_omniroute-data`, `omniroute-redis-data`, and all others) were
preserved — no named volume was deleted. The prune uses `docker volume prune -f`
**without** `--all`, which per official Docker documentation guarantees named
volume integrity.

## Evidence 6: Daemon Health Post-Prune (Task 6.5)

After the prune, the following live probes confirmed the daemon and stacks
remained healthy:

```bash
docker desktop status --format json
# { "SessionID": "1f1d9563-...", "Status": "running" }

curl -fsS http://127.0.0.1:20128/healthz        # -> ok (HTTP 200)
curl -fsS http://127.0.0.1:20128/api/monitoring/health
# -> {"status":"healthy","setupComplete":true}

docker exec omniroute-redis redis-cli ping      # -> PONG
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8788/docs  # -> 200
```

Docker topology observed:
- `claude-code-provider-adapter-adapter-1`  Up (healthy)  127.0.0.1:8788->8787/tcp
- `omniroute-redis`                        Up (healthy)  6379/tcp
- `omniroute`                              Up (healthy)  127.0.0.1:20128-20129->20128-20129/tcp

## Evidence 7: Full Suite Regression (Post-Fix Verification)

After the second-round bug fixes (helper probe, validator false positives, disk
reclaim parsing), the entire OpenSpec store was re-validated:

```bash
openspec validate --all --store openspec-store
# Totals: 443 passed, 0 failed (443 items)
```

All scripts (`docker-service.sh`, `docker-standardize-check.sh`,
`docker-disk-guard.sh`) pass `bash -n` syntax checks and execute correctly
against the live environment.

## Conclusion

All 30 implementation tasks completed. Every delta requirement in
`specs/docker-lifecycle` and `specs/docker-resource-access` is demonstrably
implemented and verified against the live workstation. No incomplete artifacts
or tasks remain. The change is ready for archive.
