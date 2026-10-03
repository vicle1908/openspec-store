# Tasks

## 1. Baseline Verification & Pre-State Audit

- [x] 1.1 Verify preflight state: ensure Docker daemon is reachable, host `sqlite3` is present, compose config renders without error under `--profile base`, and `~/.omniroute/update-available` contains target digest `sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218`.
- [x] 1.2 Capture pre-upgrade baseline: verify `omniroute` container is running and healthy on v3.8.50, query SQLite database inside container to confirm `integrity_check=ok`, and record baseline counts (`api_keys=1`, `provider_connections=19`) in `evidence.md §1`.
- [x] 1.3 Verify Compose deployment invariants: check that port mappings bind strictly to loopback `127.0.0.1` (ports 20128, 20129, 20132), persistence uses Docker named volume `omniroute-data` mounted at `/app/data`, and Redis has no published host ports (recorded in `evidence.md §1`).

## 2. Upgrade Execution via Fail-Closed Updater

- [x] 2.1 Execute `~/Omniroute/scripts/update.sh 3.8.51` from `~/Omniroute` and stream log output to verify sequential execution through all 10 gates (Gates 0–9).
- [x] 2.2 Confirm update flag cleanup and snapshot generation: verify `~/.omniroute/update-available` is removed and a verified snapshot file `pre-update-*.sqlite` is present in `~/.omniroute/snapshots/`.

## 3. Independent Post-Upgrade Verification

- [x] 3.1 Verify container and runtime version: assert `docker inspect --format='{{.State.Health.Status}}' omniroute` reports `healthy`, `/app/package.json` inside the container reports version `3.8.51`, running container image ID matches the pulled `latest` image ID, and image RepoDigest matches `sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218` (recorded in `evidence.md §2`).
- [x] 3.2 Verify endpoint contracts: verify `/healthz` returns `ok`, dashboard `/` returns HTTP 200 or 307, `/api/monitoring/health` returns `{"status":"healthy","setupComplete":true}`, `HEAD /v1/models` returns HTTP 200, and authenticated in-container `GET /v1/models` returns HTTP 200 with non-empty model data (recorded in `evidence.md §2`).
- [x] 3.3 Verify database integrity & persistence retention: execute `better-sqlite3` integrity check (`ok`) and confirm `api_keys` count >= baseline (1) and `provider_connections` count >= baseline (19) (recorded in `evidence.md §2`).
- [x] 3.4 Verify ecosystem infrastructure invariants: assert Redis container remains on `redis:7-alpine` and healthy, loopback port bindings are intact, SOCKS5 proxy flags remain false, container environment retains `NODE_OPTIONS=--max-old-space-size=2048`, and compile final `evidence.md §2`.

## 4. Governance & Specification Sync

- [x] 4.1 Update `platform/openspec-store/openspec/config.yaml` OmniRoute section to record version `v3.8.51`, the upgrade date, and the applied index digest `sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218`.
- [x] 4.2 Run `openspec validate upgrade-omniroute-to-v3-8-51 --strict --store openspec-store` and `openspec validate --all --strict --store openspec-store` to verify catalog consistency.
- [x] 4.3 Archive the completed change using the OpenSpec archive workflow with a scoped, pathspec-limited git commit.
