## Context

Graphify (25,413 nodes, 40,546 edges) and GitNexus (28,575 nodes, 64,677 edges,
300 flows) were used to scan the full codebase for dead code, duplication,
legacy patterns, and architectural issues. The audit confirmed strong service
isolation (zero inter-service code paths) and no circular imports, but surfaced
three hygiene items.

### Finding 1: Dead ClusterMode Config (catalog-service)

The Redis adapter (`services/catalog-service/internal/adapters/redis/adapter.go`)
is a cluster-only implementation using `redis.ClusterOptions` unconditionally.
The `Redis` config struct still carries:

- `ClusterMode bool` (line 63) — never read by the adapter
- `Address string` (line 70, comment: "Single-node settings (legacy)")
- Default `redis.cluster_mode: false` (line 202)
- Env bindings `CATALOG_REDIS_CLUSTER_MODE` and `CATALOG_REDIS_ADDRESS` (lines 241-242)

GitNexus blast-radius: 0 upstream callers, 0 processes affected.

The legacy-code-removal change (2026-07-22) marked LCR-001 as complete but did
not clean up catalog-service. This change completes that gap.

### Finding 2: Dead Observability Functions (order-service)

`RedactValue` and `HashFingerprint` are defined in two build-tag-switched files:
- `observability.go` (`//go:build !platform_observability`) — legacy inline impl
- `observability_platform.go` (`//go:build platform_observability`) — platform shim

GitNexus confirms zero production callers. Only `redact_test.go` calls them.
The propagation helpers (`WithCorrelationID`, `FromContext`, `ApplyToRequest`)
ARE used in production — those stay.

The `RedactList` (legacy var) and `RedactList()` (platform func) are also
test-only. `IsSensitiveKey` is test-only in the legacy build but delegates to
`platformobs.IsSensitiveKey` in the platform build.

### Finding 3: Missing .gitnexusrc

No `.gitnexusrc` exists. GitNexus detects pdg-mode mismatch on every run and
forces a full rebuild (~12 min, 13,874 embeddings regenerated).

## Goals

1. Remove all dead config fields, defaults, and env bindings from catalog-service.
2. Remove dead exported functions and their tests from order-service observability.
3. Pin GitNexus tooling defaults to prevent unnecessary rebuilds.

## Non-Goals

- Wiring `RedactValue`/`HashFingerprint` into middleware (separate change if needed).
- Changing the shipping-service StubAdapter wiring (intentional local-dev design).
- Modifying any service behavior observable by clients or infrastructure.

## Design

### catalog-service config cleanup

Remove from `services/catalog-service/internal/config/config.go`:

1. Delete `ClusterMode bool` field from `Redis` struct.
2. Delete `Address string` field and its `// Single-node settings` comment from
   `Redis` struct.
3. Delete `v.SetDefault("redis.cluster_mode", false)` line.
4. Delete `"redis.cluster_mode": "CATALOG_REDIS_CLUSTER_MODE"` from env bindings.
5. Delete `"redis.address": "CATALOG_REDIS_ADDRESS"` from env bindings.

The adapter (`adapter.go`) never reads these fields, so no adapter changes needed.

### order-service observability cleanup

Remove from `services/order-service/internal/observability/`:

1. Delete `RedactValue` function from `observability.go`.
2. Delete `HashFingerprint` function from `observability.go`.
3. Delete `RedactedValue` constant from `observability.go`.
4. Delete `RedactList` variable from `observability.go`.
5. Delete `IsSensitiveKey` function from `observability.go`.
6. Delete `crypto/sha256`, `encoding/hex` imports from `observability.go` (if unused).
7. Repeat (1-6) for `observability_platform.go` equivalents.
8. Delete `redact_test.go` entirely.
9. Run `gofmt -w .` in the observability package.

Keep: `PropagationContext`, `FromContext`, `With*`, `ApplyToRequest`, header
constants, `MetricsCollector`, `NoopMetricsCollector`, `ValidateOutcome`, logging
helpers — all have production callers.

### .gitnexusrc pin

Create `.gitnexusrc` at repo root:

```json
{
  "pdg": false
}
```

## Verification

1. `go build ./...` in `services/catalog-service/` — compiles without ClusterMode.
2. `go build ./...` in `services/order-service/` — compiles without RedactValue.
3. `go test ./internal/config/...` in catalog-service — config tests pass.
4. `go test ./internal/observability/...` in order-service — remaining tests pass.
5. `gofmt -l .` in both directories — zero formatting issues.
6. `openspec validate --strict --all` — repository validation passes.
7. `gitnexus analyze .` — no pdg-mode rebuild triggered.
