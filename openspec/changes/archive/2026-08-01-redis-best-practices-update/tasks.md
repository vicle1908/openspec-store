# Tasks: Redis Best Practices Update

## Section 1: RESP3 Protocol Mandate

- [x] 1.1 Add requirement RC-011 to `openspec/specs/redis-cluster/spec.md`
  mandating RESP3 protocol (Protocol=3) for all Redis clients.
  - **Verification**: `openspec validate redis-cluster --type spec` passes

## Section 2: Slowlog Server-Side Configuration

- [x] 2.1 Add `--slowlog-log-slower-than 10000` and `--slowlog-max-len 128`
  to all 6 Redis node command args in `deploy/docker-compose.redis-cluster.yaml`.
  - **Verification**: `docker compose -f deploy/docker-compose.redis-cluster.yaml config` renders without error
- [x] 2.2 Add requirement RM-006 to `openspec/specs/redis-monitoring/spec.md`
  mandating explicit slowlog configuration.
  - **Verification**: `openspec validate redis-monitoring --type spec` passes

## Section 3: Connection Pool Hardening

- [x] 3.1 Add `PoolFIFO: true`, `MinRetryBackoff: 8 * time.Millisecond`,
  `MaxRetryBackoff: 512 * time.Millisecond` to catalog-service Redis adapter
  in `services/catalog-service/internal/adapters/redis/adapter.go`.
  - **Verification**: `cd services/catalog-service && go build ./...`
- [x] 3.2 Add requirement RV-012 to `openspec/specs/redis-verification/spec.md`
  mandating FIFO pool and explicit retry backoff.
  - **Verification**: `openspec validate redis-verification --type spec` passes

## Section 4: Enhanced Health Checks

- [x] 4.1 Update Docker Compose healthcheck in
  `deploy/docker-compose.redis-cluster.yaml` to verify `cluster_state:ok`
  instead of just `ping`.
  - **Verification**: `docker compose -f deploy/docker-compose.redis-cluster.yaml config` renders without error
- [x] 4.2 Add requirement RC-012 to `openspec/specs/redis-cluster/spec.md`
  mandating cluster-state health checks.
  - **Verification**: `openspec validate redis-cluster --type spec` passes

## Section 5: Graceful Shutdown

- [x] 5.1 Add requirement RC-013 to `openspec/specs/redis-cluster/spec.md`
  mandating SIGTERM handling and documenting rolling restart procedure.
  - **Verification**: `openspec validate redis-cluster --type spec` passes
- [x] 5.2 Add "Graceful Shutdown" and "Rolling Restart" sections to
  `docs/runbooks/redis.md` with replica-first ordering and replication
  offset verification steps.
  - **Verification**: `go run tools/doccheck/main.go tools/doccheck/validator.go --root .` passes documentation links

## Section 6: Documentation Updates

- [x] 6.1 Update `docs/redis-architecture.md` "Best Practice Alignment"
  section to reflect the new requirements (RESP3, slowlog, pool, health,
  shutdown all move to ✅ Excellent).
  - **Verification**: Doc links valid in doccheck
- [x] 6.2 Update `docs/redis-architecture.md` "Planned Improvements"
  section to remove items now implemented and add client-side caching
  as the next priority.
  - **Verification**: Content is accurate and actionable

## Section 7: Validation

- [x] 7.1 Run `openspec validate --strict --all` to verify all specs pass.
  - **Verification**: All 5 Redis specs pass validation
- [x] 7.2 Run `cd services/catalog-service && go build ./...` to verify
  adapter compiles with new pool settings.
  - **Verification**: Clean build, no errors
