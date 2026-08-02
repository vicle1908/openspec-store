# platform-go-runtime Specification

## Purpose

This spec defines the Go toolchain pin, the Fx-based dependency-injection pattern, and the canonical `cmd/` / `internal/` layout. Every service MUST target Go 1.26.5 with the same module-graph behavior, and MUST construct its app via `fx.New(New<App>())` so the wiring is statically validated at boot.

## Requirements
### Requirement: Go 1.26.5 toolchain pinned per module

> **Status**: IMPLEMENTED. All services pin Go 1.26.5 toolchain; CI enforces version via verify-go-version.

Every service `go.mod` SHALL pin the toolchain as `go 1.26.5`. New service modules created via `go mod init` on Go 1.26 binaries start with `go 1.25.0` (Go 1.26's new default that encourages forward/backward compatibility); the platform's CI SHALL bump the directive to `go 1.26.5` and verify a `go build ./...` and `go test ./...` pass before the PR merges. The platform's `Makefile` template includes a target `verify-go-version` that fails if the toolchain is anything other than `1.26.5+`.

#### Scenario: A new service module is bootstrapped on Go 1.26
- **WHEN** a developer runs `go mod init` against a fresh `services/customer-service/`
- **THEN** `go.mod` initially contains `go 1.25.0`; the platform's `bootstrap.sh` (run as a pre-PR step) bumps it to `go 1.26.5`

#### Scenario: A PR fails CI if the toolchain is not 1.26.5
- **WHEN** a service's `go.mod` says `go 1.25.x`
- **THEN** the `verify-go-version` CI check fails with a clear message

### Requirement: Green Tea GC enabled by default

> **Status**: IMPLEMENTED. Green Tea GC enabled by default; GOEXPERIMENT=nogreenteagc not set.

The platform SHALL use Green Tea GC (the default garbage collector on Go 1.26) without opt-out. Green Tea GC delivers a 10–40% reduction in GC overhead on allocation-heavy paths. The platform MUST NOT set `GOEXPERIMENT=nogreenteagc`; that experiment is expected to be removed in Go 1.27. Each service's `Dockerfile` MUST NOT pass `GOEXPERIMENT=nogreenteagc` or set `GOGC` to a value that defeats Green Tea's pacing.

#### Scenario: Default build uses Green Tea GC
- **WHEN** a service is built with `go build -o service ./cmd/service`
- **THEN** the resulting binary uses Green Tea GC (verifiable via the `GOEXPERIMENT` runtime check or by inspecting `runtime/metrics` names)

### Requirement: `GOMEMLIMIT` set to 80% of container memory

> **Status**: IMPLEMENTED. GOMEMLIMIT set to 80% of container memory in Dockerfiles and K8s manifests.

Each service's `Dockerfile` and `Kubernetes Deployment` SHALL set `GOMEMLIMIT` to 80% of the container memory limit (e.g., a 512 MiB container gets `GOMEMLIMIT=419430400` bytes ≈ 400 MiB). The 80% headroom accounts for Green Tea GC's ~8–15% RSS growth (Green Tea holds regions open longer than the prior GC). The platform's deploy overlay enforces this via a deployment manifest validator.

#### Scenario: Container memory limit of 512 MiB maps to GOMEMLIMIT of 400 MiB
- **WHEN** a service's Deployment manifest sets `resources.limits.memory: 512Mi`
- **THEN** the corresponding pod env var `GOMEMLIMIT=419430400` (400 MiB) is injected by the platform's chart; the service's metrics show stable RSS around 350–400 MiB

### Requirement: PGO via committed `default.pgo` per service

> **Status**: PARTIAL. PGO support exists; default.pgo files may not be committed for all services.

Each service SHALL commit a `default.pgo` file captured from a real peak-load run (typically a staging canary). The `Makefile` build target uses `-pgo=./default.pgo` explicitly (and falls back to `-pgo=auto` if the file is absent). The `Dockerfile` rebuild step runs `go build -pgo=./default.pgo -o /app/service ./cmd/service`. Captured profiles are refreshed quarterly and after every schema or workload change. PGO delivers 2–14% CPU savings per the official Go docs; the platform's CI measures before/after with `go test -bench=. -count=10` on a fixed benchmark suite.

#### Scenario: Build with default.pgo optimizes hot paths
- **WHEN** a service is built with `-pgo=./default.pgo`
- **THEN** devirtualization and inlining decisions reflect the peak-load call-site frequencies; the resulting binary shows a measurable CPU reduction on the smoke benchmark

#### Scenario: PGO refresh is part of the release checklist
- **WHEN** a service is released
- **THEN** the release notes include a `pgo-refreshed: <date>` line; if the PGO is older than 180 days, the platform warns but does not block

### Requirement: `tool` directive replaces `tools.go`

> **Status**: PARTIAL. Tool directive exists in go.mod; tools.go removal may be partial.

Each service's `go.mod` SHALL use the `tool` directive to pin dev tools instead of the older `tools.go` blank-import hack. The platform's tooling list is:

```
tool (
    github.com/golangci/golangci-lint/cmd/golangci-lint
    honnef.co/go/tools/cmd/staticcheck
    golang.org/x/vuln/cmd/govulncheck
    github.com/golang/mock/mockgen
    github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen
    golang.org/x/tools/cmd/stringer
    github.com/bufbuild/buf/cmd/buf
)
```

CI runs each tool via `go tool <name>` (not via `go run` or a manually installed binary). The `tools.go` file (if present) MUST be deleted; a project that ships `tools.go` after this change lands fails CI on a pre-commit hook.

#### Scenario: Dev tools are reproducible across machines
- **WHEN** two developers run `go tool staticcheck ./...` on the same codebase
- **THEN** both get identical results because the tool version is pinned via `go.mod`'s `tool` directive

#### Scenario: tools.go is rejected by CI
- **WHEN** a service's repo contains `tools.go` with blank imports of dev tools
- **THEN** the CI check `verify-no-tools-go` fails

### Requirement: `httputil.ReverseProxy{Director}` is migrated to `Rewrite`

> **Status**: PARTIAL. Migration to Rewrite pattern may be partial across services.

Each service's `internal/adapters/http/...` code SHALL use `httputil.ReverseProxy{ Rewrite: ...}` instead of `Director` (the `Director` field is deprecated in Go 1.26 because of an inherent header-leak safety issue). Migration is mechanical: every `func(req *http.Request) { ... }` body becomes a `func(pr *httputil.ProxyRequest) { ... }` body. The platform's `gofix` adoption batch may apply this via `go fix -diff ./...` as a preview PR.

#### Scenario: Reverse proxy uses Rewrite
- **WHEN** a service proxies an inbound request to a backend
- **THEN** the implementation uses `httputil.ReverseProxy{ Rewrite: func(pr *httputil.ProxyRequest) { ... } }`; `Director` is not used

### Requirement: `t.ArtifactDir()` adopted for integration and load tests

> **Status**: PARTIAL. ArtifactDir support exists; adoption across all tests may be partial.

Each service's integration, load, and fuzz tests SHALL write per-test artifacts via `t.ArtifactDir()` (Go 1.26+) into a path uploaded by CI as a build artifact. The CI workflow uses `go test -count=1 -race -artifacts` so the artifact directory is the canonical `-outputdir`. This replaces ad-hoc `os.MkdirTemp("/tmp", "test-*")` patterns.

#### Scenario: Failed test uploads artifacts to CI
- **WHEN** an integration test under `test/integration/` fails
- **THEN** `t.ArtifactDir()` returns a path under the test's output directory; the CI runner uploads the path and the developer can inspect the artifacts from the failed run

### Requirement: `B.Loop` adopted for benchmark tests

> **Status**: PARTIAL. B.Loop pattern defined; adoption across benchmarks may be partial.

Each service's `test/performance/` benchmarks SHALL use `for b.Loop()` (Go 1.24+, fixed-in-1.26-inlining-regression) instead of the older `for i := 0; i < b.N; i++` pattern. Migration is mechanical; the platform's modernization batch runs `go fix -diff ./...` and produces a preview PR.

#### Scenario: Benchmarks use B.Loop
- **WHEN** a benchmark runs `go test -bench=. -benchmem ./test/performance/...`
- **THEN** the loop body is inlined correctly (no compiler regression), and the benchmark output is consistent across runs

### Requirement: Modernizations via `go fix` batches (preview PR)

> **Status**: PARTIAL. go fix batches scheduled; modernizer adoption may be partial.

The platform SHALL run `go fix -diff ./...` periodically (quarterly) to surface modernizer opportunities (slices/maps packages, `min`/`max`, `cmp.Ordered`, etc.). The diff is committed as a separate, reviewable PR; the diff is NEVER auto-merged into a feature PR. The first such batch lands as part of this change.

#### Scenario: go fix -diff surfaces a modernizer
- **WHEN** the platform runs `go fix -diff ./...` against an older service
- **THEN** the diff output lists the files modernized (e.g., `for i, x := range foo { _, _ = foo[i], x }` → `for i, x := range foo { _ = i; _ = x }`); the batch becomes a PR

### Requirement: GODEBUG settings documented in `docs/adr/0005-go-1.26-runtime.md`

> **Status**: PARTIAL. ADR exists; GODEBUG settings documentation may be partial.

The platform SHALL document every Go 1.26 GODEBUG setting the platform touches in `docs/adr/0005-go-1.26-runtime.md`. The minimum set:

- `tlssecpmlkem=0` — opt out of post-quantum TLS if a known-upstream proxy is incompatible (rare; default ON).
- `asynctimerchan` — to be removed in 1.27; platform does not touch.
- `greenteagc=1` — implicit (Green Tea is the 1.26 default).

The ADR is updated whenever a new GODEBUG is set or unset.

#### Scenario: GODEBUG change requires ADR
- **WHEN** a PR sets a new GODEBUG in production or removes one
- **THEN** the PR must update `docs/adr/0005-go-1.26-runtime.md` and reference a verification (PV-261 series)

### Requirement: Goroutine leak profile enabled in staging canary

> **Status**: DEFERRED. Goroutine leak profile not yet enabled in staging/production.

The platform SHALL enable the experimental goroutine leak profile (`GOEXPERIMENT=goroutineleakprofile`) in staging and one production canary per service. The profile is exposed at `/debug/pprof/goroutineleak` and Prometheus-scrapeable. The platform's alert fires when the leak count exceeds a service-specific threshold (default: 10 leaks over 24 hours).

#### Scenario: Canary exposes goroutine leak profile
- **WHEN** a service runs in the production canary deployment
- **THEN** the env var `GOEXPERIMENT=goroutineleakprofile` is set; the leak profile endpoint is reachable at `/debug/pprof/goroutineleak`; the Prometheus metrics expose the leak count

### Requirement: Migration to Go 1.27 SHALL be tracked in `docs/adr/0005-go-1.26-runtime.md`

> **Status**: DEFERRED. Go 1.27 migration planned for August 2026; tracking not yet started.

The platform SHALL track the Go 1.27 migration (expected August 2026) for: `crypto/mldsa` signatures, JSON v2 (if stable), staticcheck analyzer integration into `go fix`, and the hard-flip on the `tlsunsafeekm`/`tlsrsakex`/`tls10server`/`tls3des`/`x509keypairleaf` GODEBUGs. The migration MUST be tracked as a discrete PR per service; the platform SHALL NOT adopt 1.27 en masse.

#### Scenario: Pre-flight for 1.27 lands a discrete PR per service
- **WHEN** Go 1.27 is released and the platform decides to migrate
- **THEN** each service's `go.mod` bump from `1.26.5` to `1.27.0` is a discrete, reviewable PR that includes any necessary cipher-list / CurvePreferences changes per the `tls*` GODEBUG retirement
