# Tasks: disk-reclaim-2026-09

## 1. Pre-flight state capture

- [x] 1.1 Record baseline: free space (`df -h /System/Volumes/Data`), `docker system df`, container health (`docker ps`), volume count by type (named vs anonymous hash-named), image list. Verify the 3 running containers (omniroute, omniroute-redis, claude-code-provider-adapter) are healthy — proceed only if all 3 healthy.

## 2. Anonymous volume prune (data-preserving)

- [x] 2.1 Run `docker volume prune -f` and record the reclaimed bytes. Verify: `docker volume ls` still shows all 10 named volumes (omniroute-redis-data, omniroute_omniroute-data, 8× tdt-local-full_*) and only anonymous hash-named volumes are gone. — Reclaimed 2.107GB; 10/10 named volumes retained

## 3. Explicit unused image removal (rollback preserved)

- [x] 3.1 Re-verify each target image has no container reference (`docker ps -a --filter ancestor=<image>`), then remove the explicit list: tdt-scheduler:main-c6a0fd4, agent-core:local-dev, tdt-observability:local-20260825, tdt-observability-mlflow:v3.15.1, langfuse/langfuse:4.16.0, langfuse/langfuse-worker:4.16.0, grafana/otel-lgtm:0.31.0, clickhouse/clickhouse-server:26.7.5.10-alpine, ghcr.io/mlflow/mlflow:v3.15.1, otel/opentelemetry-collector-contrib:0.159.0, postgres:18.6-trixie, redis:7-alpine, alpine:3.20, alpine:3.21, alpine:latest, bufbuild/buf:1.71.0, minio/mc:RELEASE.2025-08-13T08-35-41Z, minio/minio:RELEASE.2025-09-07T16-13-09Z, ghcr.io/gitleaks/gitleaks:v8.30.1, registry:2, testcontainers/ryuk:0.8.1, plus the dangling untagged diegosouzapw/omniroute image. Verify: `docker images` retains diegosouzapw/omniroute:latest, claude-code-provider-adapter-adapter:latest, redis:8.10.1-alpine, AND omniroute:rollback-3.8.49-20260828-075010. — DEVIATIONS (caught by verification): (a) redis:7-alpine REMOVED FROM LIST — omniroute-redis (active container) runs on redis:7-alpine, not 8.10.1; kept. (b) The "dangling diegosouzapw/omniroute" entry shares image ID sha256:4205701… with omniroute:rollback-3.8.49 (same image, one 1.97GB artifact) — nothing extra to remove; rollback preserved. 149 untag/delete ops executed; 25→5 images; all 4 preservation targets verified KEPT.

## 4. Stale build cache + Go module cache

- [x] 4.1 Run `docker builder prune -f` (default, non-`--all`) and record reclaimed bytes; verify remaining cache is the in-use portion only (`docker system df` build-cache reclaimable ≈ 0). — Reclaimed 10.66GB (image removals unlinked extra cache, raising it from the 4.37GB estimate)
- [x] 4.2 Run `go clean -modcache` and verify `du -sh ~/go/pkg/mod` shows ~0 (module cache empty; re-downloads on demand). — Cache emptied (dir removed, 1.2GiB)

## 5. Post-cleanup verification gates

- [x] 5.1 All 3 containers healthy (`docker ps` no restarting/unhealthy states) and OmniRoute healthy per documented contract: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:20128/v1/models` returns 401 (keyless loopback inference; 401 on /v1/models is the verified-healthy signature). — PASSED: 3/3 healthy, /v1/models → 401
- [x] 5.2 Free-space delta from task 1.1 baseline is ≥ 15 GiB (`df -h /System/Volumes/Data`), Docker.raw actual size shrank accordingly (`du -sh ~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`). — PASSED: 49GiB → 70GiB free (+21GiB); Docker.raw 33G → 13G
- [x] 5.3 Preservation audit passes: 10 named volumes present, rollback image present, active images present, `docker volume ls` count = 10. — PASSED: 10/10 named volumes, rollback present, 5 images (4 preserve-set + redis:8.10.1-alpine target)

## 6. Closeout

- [x] 6.1 Record before/after numbers in this change's README (or tasks annotations), archive the change (`openspec archive disk-reclaim-2026-09 --store openspec-store --yes`), and commit the store.
