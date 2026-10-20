# Verification Evidence: `upgrade-omniroute-to-v3-8-52`

**Date**: 2026-10-20
**Workstation**: macOS Darwin 27.0.0 (`arm64`)
**Target Repository**: `/Users/androidteam/Omniroute`
**Target Container**: `omniroute` (`diegosouzapw/omniroute:latest` -> `v3.8.52`, index digest `sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c`)

---

## §1 Pre-Upgrade Baseline & Flag

### 1.1 Pre-Upgrade Container, Port Binding, Sidecar, and SQLite Baseline (`v3.8.51`)

```text
$ docker inspect --format='Status={{.State.Status}} Health={{.State.Health.Status}} Image={{.Image}}' omniroute
Status=running Health=healthy Image=sha256:8ac4e82973a3f687564ca4f1cafe9ad528fae9d319eecf526c78ae91f7cea05a

$ docker image inspect diegosouzapw/omniroute:latest --format='Id={{.Id}} RepoDigests={{json .RepoDigests}}'
Id=sha256:8ac4e82973a3f687564ca4f1cafe9ad528fae9d319eecf526c78ae91f7cea05a RepoDigests=["diegosouzapw/omniroute@sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218"]

$ docker inspect --format='{{json .NetworkSettings.Ports}}' omniroute
{"20128/tcp":[{"HostIp":"127.0.0.1","HostPort":"20128"}],"20129/tcp":[{"HostIp":"127.0.0.1","HostPort":"20129"}],"20132/tcp":[{"HostIp":"127.0.0.1","HostPort":"20132"}]}

$ docker inspect --format='Image={{.Config.Image}} Status={{.State.Status}} Health={{.State.Health.Status}}' omniroute-redis
Image=docker.io/library/redis:8.6.5-alpine Status=running Health=healthy
```

```json
{
  "version": "3.8.51",
  "quick_check": "ok",
  "api_keys": 1,
  "provider_connections": 33,
  "combos": 8,
  "migTable": "_omniroute_migrations",
  "migrations": {
    "m": 196,
    "total": 193
  }
}
```

### 1.2 Upstream Digest Detection (`check-upstream.sh`)

```text
$ /Users/androidteam/Omniroute/scripts/check-upstream.sh && cat /Users/androidteam/.omniroute/update-available
sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c
```

---

## §2 Fail-Closed Upgrade Execution (`update.sh 3.8.52`)

### 2.1 Initial Upgrade Run and Gate 8 `enc:v1:` At-Rest API Key Discovery

During the initial `update.sh 3.8.52` run:
- **Gate 0 (`flag present`)**: Verified `/Users/androidteam/.omniroute/update-available` (`sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c`).
- **Gate P (`preflight`)**: Verified Docker daemon, host `sqlite3`, `curl`, `docker-compose.yml`, `docker-compose.override.yml`, `docker compose --profile base config`, and container presence.
- **Gate 1 (`snapshot + integrity`)**: Verified live `PRAGMA quick_check=ok`, created `/Users/androidteam/.omniroute/snapshots/pre-update-20261020-140011.sqlite` via `better-sqlite3` `backup()`, verified host `PRAGMA quick_check=ok`, and consolidated WAL (`0|0|0`).
- **Gate 2 (`pull`) & Gate 3 (`digest-match`)**: Pulled `diegosouzapw/omniroute:latest` (`omniroute-base` only; `omniroute-redis` untouched) and verified `RepoDigest == sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c` and image ID `sha256:fababa40ede0927ecb9d95b8c7255247fe2da16d0df1bd75a6e390a7fa224a65`.
- **Gate 4 (`deploy`) & Rollback Tag**: Tagged `omniroute:rollback-3.8.51-20261020-140011` (`8ac4e82973a3`) and recreated `omniroute` via `docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base`.
- **Gate 4b (`muse-wire-compat`)**: Verified `/app/peer-stamp.mjs` (`MUSE_CODE_COMPAT_V2`) and Next.js server chunks.
- **Gate 5 (`healthy`), Gate 6 (`version`), Gate 7 (`image-id`)**: Container reached `healthy` after `7x5s` (completing SQLite migrations `197`..`212`), `/app/package.json` verified `3.8.51 -> 3.8.52`, and running image ID matched `sha256:fababa40ede0927ecb9d95b8c7255247fe2da16d0df1bd75a6e390a7fa224a65`.
- **Gate 8 (`endpoints`)**: In `v3.8.52`, `src/lib/db/apiKeys/secretAtRest.ts` encrypts `api_keys.key` at rest using the `enc:v1:<iv>:<ciphertext>:<authTag>` AES-256-GCM envelope derived from `STORAGE_ENCRYPTION_KEY` (`scryptSync(secret, "omniroute-field-encryption-v1", 32)`). Because Gate 8's in-container `AUTH_PROBE` originally sent `row.key` without decrypting `enc:v1:`, Gate 8 failed closed and retained `/Users/androidteam/.omniroute/update-available`.
- Updated `update.sh` Gate 8 `AUTH_PROBE` to decrypt `enc:v1:` envelopes in-memory inside the container using `process.env.STORAGE_ENCRYPTION_KEY`, added `verify_muse_catalog_json` in Gate 8 to structurally parse `/v1/muse-code/models` and `/muse-code/models` JSON and assert `Array.isArray(parsed.data)` contains an object with `id === "muse-spark-1.3"`, updated `update.sh` Gate 1 to set `PRAGMA journal_mode=DELETE;` so snapshots never recreate `-wal`/`-shm` sidecars on read, and updated `container-entrypoint-compat.sh` + `ensure-muse-wire-compat.sh` to match webpack's minified `response:{id:d.O1,status:"in_progress"}` (`[A-Za-z0-9_$]+\.[A-Za-z0-9_$]+`) in `/app/.build/next/server/chunks/20286.js`.

### 2.2 Verbatim `update.sh 3.8.52` Completion Log (All 10 Gates Passed)

```text
[2026-10-20 14:00:11] === OmniRoute update starting: target version 3.8.52, target digest sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c ===
[2026-10-20 14:00:12] Preflight passed
[2026-10-20 14:00:12] Pre-state: old_version=3.8.51 old_image_id=sha256:8ac4e82973a3f687564ca4f1cafe9ad528fae9d319eecf526c78ae91f7cea05a old_digest=diegosouzapw/omniroute@sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218 baseline_api_keys=1 baseline_provider_connections=33
[2026-10-20 14:00:30] Snapshot verified: /Users/androidteam/.omniroute/snapshots/pre-update-20261020-140011.sqlite (live + host quick_check ok, wal_checkpoint=0|0|0, sidecars consolidated)
[2026-10-20 14:00:55] Pulled image verified: digest=sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c id=sha256:fababa40ede0927ecb9d95b8c7255247fe2da16d0df1bd75a6e390a7fa224a65
[2026-10-20 14:00:55] Rollback tag created: omniroute:rollback-3.8.51-20261020-140011
[2026-10-20 14:00:58] Gate 4b: Muse Code wire-compat normalization verified
[2026-10-20 14:01:29] Healthy after 7x5s
[2026-10-20 14:01:29] Version verified: 3.8.51 -> 3.8.52
[2026-10-20 14:01:29] Running container confirmed on pulled image
...
[2026-10-20 14:04:26] Gate 4b: Muse Code wire-compat normalization verified
[2026-10-20 14:04:26] Healthy after 1x5s
[2026-10-20 14:04:26] Version unchanged (3.8.52) — treating as verification retry of a prior partial run
[2026-10-20 14:04:26] Running container confirmed on pulled image
[2026-10-20 14:04:27] Model catalog: anonymous GET=401 (catalog auth enabled — v3.8.50 opt-out); authenticated GET=200 count=1294
[2026-10-20 14:04:27] Endpoints verified: /healthz=ok dashboard=HTTP307 monitoring=healthy/setupComplete=true HEAD/v1/models=HTTP200 GET/v1/models=HTTP401 muse_v1=HTTP200(muse-spark-1.3) muse_rewrite=HTTP200(muse-spark-1.3)
[2026-10-20 14:04:29] Post-deploy data verified: quick_check=ok api_keys=1(>=1) provider_connections=33(>=33) pre_migration_backups=cleaned
[2026-10-20 14:04:29] All gates passed. Update flag cleared.
[2026-10-20 14:04:29] Verification-only run (already on target): the rollback tag from the original upgrade attempt remains the rollback point.
[2026-10-20 14:04:29] === OmniRoute update complete: 3.8.52 -> 3.8.52 ===
```

### 2.3 Snapshot, Rollback Tag, Flag Removal, and `db_backups` Cleanup Verification

```text
$ test ! -f /Users/androidteam/.omniroute/update-available && echo "update-available: REMOVED"
update-available: REMOVED

$ ls -lh /Users/androidteam/.omniroute/snapshots/pre-update-20261020-*
-rw-r--r-- 1 androidteam staff 950M Oct 20 14:08 /Users/androidteam/.omniroute/snapshots/pre-update-20261020-140011.sqlite

$ sqlite3 /Users/androidteam/.omniroute/snapshots/pre-update-20261020-140011.sqlite "PRAGMA quick_check;"
ok

$ docker images 'omniroute:rollback-*' --format '{{.Repository}}:{{.Tag}} -> {{.ID}} ({{.CreatedSince}})'
omniroute:rollback-3.8.51-20261020-140011 -> 8ac4e82973a3 (2 weeks ago)

$ docker exec omniroute sh -c 'ls -la /app/data/db_backups/'
total 8
drwxr-xr-x 2 node node 4096 Oct 20 07:04 .
drwxr-x--- 6 node node 4096 Oct 20 07:00 ..
```

---

## §3 Independent Post-Upgrade Verification

### 3.1 Container Health, Image Digest, and SQLite Migrations (`197`..`212`)

```text
$ docker inspect --format='Health={{.State.Health.Status}} Image={{.Image}}' omniroute
Health=healthy Image=sha256:fababa40ede0927ecb9d95b8c7255247fe2da16d0df1bd75a6e390a7fa224a65

$ docker image inspect diegosouzapw/omniroute:latest --format='Id={{.Id}} RepoDigests={{json .RepoDigests}}'
Id=sha256:fababa40ede0927ecb9d95b8c7255247fe2da16d0df1bd75a6e390a7fa224a65 RepoDigests=["diegosouzapw/omniroute@sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c"]
```

```json
{
  "version": "3.8.52",
  "quick_check": "ok",
  "api_keys": 1,
  "provider_connections": 33,
  "combos": 8,
  "migrations": {
    "m": 212,
    "total": 209
  },
  "migs197to212": [
    { "version": "197", "name": "proxy_subscription_core_config" },
    { "version": "198", "name": "proxy_subscription_core_binary" },
    { "version": "199", "name": "proxy_operator_egress" },
    { "version": "200", "name": "provider_health_matrix_covering_index" },
    { "version": "201", "name": "drop_unused_turn_node_indexes" },
    { "version": "202", "name": "model_capabilities_reasoning_efforts" },
    { "version": "203", "name": "memory_fts_content_rowid" },
    { "version": "204", "name": "llmlingua_service" },
    { "version": "205", "name": "api_key_codex_service_mode" },
    { "version": "206", "name": "codex_wakeup_tasks" },
    { "version": "207", "name": "remove_opencode_free_provider" },
    { "version": "208", "name": "proxy_subscription_selector_last_switch_by_selector" },
    { "version": "209", "name": "call_logs_artifact_relpath_index" },
    { "version": "210", "name": "call_logs_detail_pending" },
    { "version": "211", "name": "recreate_turn_nodes_content_hash_index" },
    { "version": "212", "name": "usage_history_provider_reported_cost" }
  ]
}
```

### 3.2 Next.js Server Chunk Keepalive Normalization & Muse Code Catalog Endpoints

```text
$ /Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh omniroute
Muse Code wire-compat normalization verified (already_ok)

$ docker exec omniroute node -e '...' # verify /app/.build/next/server/chunks/*.js
{"badNull":0,"badOmni":0,"badMinified":0,"good":1}

$ curl -fsS http://127.0.0.1:20128/v1/muse-code/models | jq '{object, count: (.data | length), first: .data[0].id}'
{
  "object": "list",
  "count": 13,
  "first": "muse-spark-1.3"
}

$ curl -fsS http://127.0.0.1:20128/muse-code/models | jq '{object, count: (.data | length), first: .data[0].id}'
{
  "object": "list",
  "count": 13,
  "first": "muse-spark-1.3"
}
```

### 3.3 Host CLI Bridge (`~/.local/bin/omniroute`) Verification

```text
$ /Users/androidteam/.local/bin/omniroute status

OmniRoute Status

  Status:      healthy
  Gateway DB:  healthy (remote)
  Version:     3.8.52 (CLI: 3.8.52)
  Base URL:    http://127.0.0.1:20128
  Uptime:      208s
  Providers:   27 active / 33 configured (26 healthy, 6 disabled)
  Breakers:    22 closed, 0 half-open, 0 open

$ /Users/androidteam/.local/bin/omniroute keys list --output json | jq '.keys | length'
13
```

### 3.4 Live Muse Code CLI & Combo Inference Probes (`gemini-4-argon-high`, `gemini-3.8-flash-high`)

```text
$ /opt/homebrew/bin/muse exec --disable-approval --disable-reminders --no-session-log "Reply with the single word MUSE_OK"
MUSE_OK

$ # In-container authenticated POST /v1/chat/completions combo probes
gemini-4-argon-high status=200 {"id":"chatcmpl-1792480316827-c49bc47f","model":"gemini-4-argon-high","reply":"COMBO_OK"}
gemini-3.8-flash-high status=200 {"id":"chatcmpl-1792480503305-60665829","model":"gemini-3.8-flash-high","reply":"COMBO_OK"}
```

### 3.5 Git Checkout Cleanliness (`~/Omniroute`)

```text
$ git -C /Users/androidteam/Omniroute status --short --branch
## main...origin/main
?? data.bak-20260824/
?? scripts/check-upstream.sh
?? scripts/container-entrypoint-compat.sh
?? scripts/ensure-muse-wire-compat.sh
?? scripts/update.sh
```
