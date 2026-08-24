## Context

OmniRoute runs as a Docker Compose stack (`base` profile, Hub image `diegosouzapw/omniroute:latest`, named volume `omniroute-data`, loopback-bound ports 20128/20129/20132) deployed from `~/Omniroute`. The update command is `cd ~/Omniroute && docker compose --profile base pull && docker compose --profile base up -d --no-build` (~30s). State that survives updates: named volume (SQLite DB), `.env` (secrets + config), `docker-compose.override.yml` (deployment infrastructure). The DB is handled by the app's internal migrations on boot.

A Docker Hub API comparison (no auth required for public repos) showed the running image digest (`sha256:92c768c...`) already differs from the remote `latest` (`sha256:2bf79cf...`) — an update exists but is invisible without explicit checking.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│ UPDATE TRACKING ARCHITECTURE                                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────┐                                    │
│  │  com.omniroute.update-check      │  LaunchAgent (twice daily)         │
│  │  runs: check-upstream.sh         │  logs: update-check.log           │
│  └──────────┬───────────────────────┘                                    │
│             │                                                            │
│             ▼                                                            │
│  ┌──────────────────────────────────┐                                    │
│  │  check-upstream.sh               │                                    │
│  │  1. docker image inspect → local │  digest                           │
│  │  2. Docker Hub API → remote      │  digest                           │
│  │  3. compare                      │                                    │
│  │     ├─ same → clear flag         │                                    │
│  │     └─ different → write flag +  │  osascript notification           │
│  └──────────┬───────────────────────┘                                    │
│             │                                                            │
│             ▼                                                            │
│  ┌──────────────────────────────────┐                                    │
│  │  ~/.omniroute/update-available   │  flag file (ephemeral)            │
│  │  contains: remote digest         │  present = update available       │
│  └──────────┬───────────────────────┘  absent = up-to-date             │
│             │                                                            │
│  ═══════════╪═══════════════════════════ user decision boundary ═══════  │
│             │                                                            │
│             ▼                                                            │
│  ┌──────────────────────────────────┐                                    │
│  │  update.sh (manual, on-demand)   │                                    │
│  │  1. snapshot DB → ~/.omniroute/  │  snapshots/                       │
│  │  2. docker compose pull          │                                    │
│  │  3. docker compose up -d         │                                    │
│  │  4. wait for healthy (5min max)  │                                    │
│  │  5. verify: login + API          │                                    │
│  │  6. record new digest            │                                    │
│  │  7. clear flag                   │                                    │
│  │  8. macOS notification           │                                    │
│  └──────────────────────────────────┘                                    │
│                                                                          │
│  ROLLBACK (if update breaks):                                            │
│  1. docker compose down                                                  │
│  2. restore snapshot → named volume                                      │
│  3. pin previous image tag in override (optional)                        │
│  4. docker compose up -d --no-build                                      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. `check-upstream.sh`

- **Input**: none (reads running image state + Docker Hub API)
- **Output**: flag file (`~/.omniroute/update-available`) + log entry + optional macOS notification
- **Frequency**: twice daily via LaunchAgent
- **Idempotent**: yes — clears flag when up-to-date, writes it when not
- **Error handling**: warnings logged, never exits non-zero on transient failures (Docker Hub down, network timeout)

Docker Hub API call: `curl -sL "https://registry.hub.docker.com/v2/diegosouzapw/omniroute/manifests/latest"` with `Accept: application/vnd.docker.distribution.manifest.v2+json`. For multi-arch images, extracts the `arm64` manifest digest.

### 2. `update.sh`

- **Input**: reads flag file (gates update; can be forced by creating the flag manually)
- **Output**: updated container + logs + snapshot + notification
- **Run**: manually, when user sees notification and chooses to update
- **Safety**: snapshots DB before pull (Docker's in-container `better-sqlite3.backup`)
- **Verification**: waits for healthy (5min max), checks login + dashboard HTTP

### 3. LaunchAgent (`com.omniroute.update-check`)

- **Schedule**: `StartInterval: 43200` (twice daily)
- **Logs**: `~/.omniroute/update-check.log` (stdout), `~/.omniroute/update-check.err` (stderr)
- **Not persistent across reboots**: no `RunAtLoad` — check runs on the schedule, not on login. The update itself is always manual.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Check frequency | Twice daily (12hr) | Docker Hub releases are infrequent (weekly at most); daily would be sufficient but twice daily catches releases the same day without excessive polling |
| Auto-update | No — manual only | User chose on-demand in the previous change; auto-update risks breaking changes applying without review |
| Notification mechanism | macOS `osascript display notification` + flag file | Flag file is machine-readable (scripts can check it); notification is human-visible. Both are lightweight, no dependencies |
| Snapshot method | In-container `better-sqlite3.backup` + `docker cp` | Produces a clean, consistent backup without stopping the container; avoids host-side sqlite3 (which can't read the VM-internal volume) |
| Flag file location | `~/.omniroute/update-available` | Consistent with other OmniRoute state; ephemeral (created on detection, cleared on update) |
| Script location | `~/Omniroute/scripts/` | Deployment-owned (not tracked by git); co-located with the source checkout but classified as deployment infrastructure |
| Rollback | Restore snapshot + optional image pin | Two-stage rollback: volume restore (data) + image pin (code). Image pin is optional; the snapshot alone is usually sufficient |

## Verification

1. Run `check-upstream.sh` manually → verify flag file created, log entry written, macOS notification shown
2. Run `update.sh` → verify: snapshot created, image pulled, container recreated, healthy, login works, flag cleared, notification shown
3. Verify LaunchAgent loaded: `launchctl list | grep omniroute.update`
4. Verify logs: `~/.omniroute/update-check.log` shows periodic check entries
