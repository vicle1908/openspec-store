# DDD Repository Cleanup - Tasks

## 1. Health Package Migration (High Priority)

### 1.1 Update runtime health check construction
- [x] 1.1.1 Update `services/order-service/internal/runtime/healthcheck.go`
  - Change `ProbeForChecks()` to use `health.Registry`
  - Create named `Check` implementations (e.g., `DatabaseCheck`, `TemporalCheck`)
  - Update `BuildAPIReadinessChecks()`, `BuildWorkerReadinessChecks()`, `BuildOrchestratorReadinessChecks()`
- [x] 1.1.2 Verify changes compile

### 1.2 Update API role
- [x] 1.2.1 Update `services/order-service/cmd/order-service/roles.go`
  - Change `health.New(map[string]health.Check{...})` to `registry.Register()`
  - Update probe handlers from `probe.Live()` to `registry.LiveHandler()`
- [x] 1.2.2 Verify API role builds

### 1.3 Update HTTP router
- [x] 1.3.1 Update `services/order-service/internal/adapters/http/router.go`
  - Change from mounting `*health.Probe` to mounting `*health.Registry`
  - Update route handlers to use `registry.LiveHandler()`, `registry.ReadyHandler()`, etc.
- [x] 1.3.2 Update router options if needed
- [x] 1.3.3 Run tests

### 1.4 Update worker and orchestrator roles
- [x] 1.4.1 Update worker role health check construction
- [x] 1.4.2 Update orchestrator role health check construction
- [x] 1.4.3 Verify all roles build

### 1.5 Remove service health package
- [x] 1.5.1 Verify no remaining imports to service-local health
- [x] 1.5.2 Remove service-local health package directory
- [x] 1.5.3 Final verification

## 2. Service Directory Standardization (High Priority)

### 2.1 Move order-service to services/
- [x] 2.1.1 Move `order-service/` to `services/order-service/`
- [x] 2.1.2 Update Go module path from `github.com/victory1908/order-service` to `github.com/victory1908/services/order-service`
- [x] 2.1.3 Update all internal Go imports
- [x] 2.1.4 Update Protobuf package declarations
- [x] 2.1.5 Regenerate protobuf files with buf
- [x] 2.1.6 Update root buf.yaml workspace

### 2.2 Update deployment references
- [x] 2.2.1 Update Docker Compose `context:` paths
- [x] 2.2.2 Update volume mount paths for deploy scripts
- [x] 2.2.3 Update Makefile GO_MODULES
- [x] 2.2.4 Update README documentation

## 3. Documentation Updates

### 3.1 Deploy usage documentation
- [x] 3.1.1 Update `deploy/README.md` to clarify two-layer structure
- [x] 3.1.2 Add examples showing correct usage for each

### 3.2 Runtime boundaries documentation
- [x] 3.2.1 Create `platform/docs/runtime-boundaries.md`

### 3.3 Service structure documentation
- [x] 3.3.1 Document consistent directory structure in main README

## 4. Verification

- [x] 4.1 Run platform verification
- [x] 4.2 Run order-service build and tests
- [x] 4.3 Run architecture tests
- [x] 4.4 Verify Docker Compose config
- [x] 4.5 Commit all changes

## 5. Archive

- [ ] 5.1 Final review of all changes
- [ ] 5.2 Archive change: `openspec archive ddd-repository-cleanup`
