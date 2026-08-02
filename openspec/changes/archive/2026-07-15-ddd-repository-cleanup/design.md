# DDD Repository Cleanup - Design

## Context

The microservices monorepo uses Domain-Driven Design with hexagonal architecture. Investigation revealed that apparent "duplications" have different characteristics:

| Package | Finding | Resolution |
|---------|---------|------------|
| `order-service/internal/health/` | **Incompatible API** - uses `map[string]Check` | Rewrite to use `platform/health.Registry` |
| `order-service/internal/runtime/` | **Intentional** - service-specific wiring | Document boundaries only |
| `order-service/deploy/` | **Intentional** - standalone complete stack | Document usage |
| `order-service/contracts/` | **Legacy location** - should move | Migrate to `services/` structure |

### Health Package Comparison

```
ORDER-SERVICE HEALTH (current - incompatible)
═══════════════════════════════════════════════════════════════════
package health

type Check func(context.Context) error
type Probe struct { checks map[string]Check, timeout time.Duration, ... }
func New(checks map[string]Check, timeout time.Duration) *Probe
func (p *Probe) Live/Ready/Startup(w http.ResponseWriter, r *http.Request)

PLATFORM HEALTH (target - Registry-based)
═══════════════════════════════════════════════════════════════════
package health

type Check interface { Name() string; Run(ctx context.Context) error }
type Registry struct { ... }
func NewRegistry() *Registry
func (r *Registry) Register(kind ProbeKind, check Check)
func (r *Registry) LiveHandler/ReadyHandler/StartHandler() http.Handler
```

The key differences:
1. **Check type**: Service uses `func`, Platform uses `interface`
2. **Registration**: Service uses constructor map, Platform uses runtime `Register()`
3. **HTTP handlers**: Service uses methods on Probe, Platform returns `http.Handler`

### Deploy Structure Comparison

```
SERVICE-LEVEL deploy/ (standalone complete stack)
═══════════════════════════════════════════════════════════════════
order-service/deploy/
├── docker-compose.yaml              # Complete stack: postgres, kafka, debezium, temporal, app
├── docker-compose.test.yaml        # Test profile
├── docker-compose.tools.yaml       # Local dev tools
├── docker-compose.cross-service.yaml # Cross-service integration
├── debezium-connector.json         # Debezium config
└── provision-topics.sh             # Topic provisioning script

ROOT deploy/ (composable overlays)
═══════════════════════════════════════════════════════════════════
deploy/
├── docker-compose.yaml              # Base infrastructure only
├── docker-compose.order-service.yaml # App service overlay (extends base)
├── docker-compose.tools.yaml        # Tools overlay
├── docker-compose.lgtm.yaml         # Observability overlay
└── ...

INTENDED USAGE:
- Local standalone dev: `order-service/deploy/docker-compose.yaml`
- Composed environments: `docker compose -f deploy/docker-compose.yaml -f deploy/docker-compose.order-service.yaml`
```

## Goals / Non-Goals

**Goals:**
- Migrate order-service to use `platform/health.Registry` (breaking API change)
- Move domain contracts to `services/` directory structure
- Document deploy usage patterns to prevent confusion
- Document runtime boundaries

**Non-Goals:**
- Refactoring domain logic or aggregates
- Changing Protobuf message definitions
- Merging service deploy into root deploy (both serve different purposes)
- Modifying platform/runtime to accommodate service patterns

## Decisions

### 1. Health Package Migration Strategy

**Decision**: Rewrite order-service to use `platform/health.Registry` API.

**Migration Steps**:

1. **Update health check types** - Change from `func(ctx context.Context) error` to `interface { Name() string; Run(ctx context.Context) error }`

```go
// BEFORE (order-service/internal/runtime/healthcheck.go)
func ReadyChecks(db PostgresPinger, log *zap.Logger) map[string]health.Check {
    return map[string]health.Check{
        "database": func(ctx context.Context) error { return db.Probe(ctx) },
    }
}

// AFTER
type DatabaseCheck struct{ db PostgresPinger }
func (c DatabaseCheck) Name() string { return "database" }
func (c DatabaseCheck) Run(ctx context.Context) error { return c.db.Probe(ctx) }
```

2. **Update probe construction** - Use `Registry` instead of `Probe`

```go
// BEFORE
probe := health.New(map[string]health.Check{...}, timeout)

// AFTER
registry := health.NewRegistry()
registry.Register(health.ProbeReady, DatabaseCheck{db})
handler := registry.ReadyHandler()
```

3. **Update HTTP routing** - Mount handlers instead of probe methods

```go
// BEFORE
router.Handle("/health/live", http.HandlerFunc(probe.Live))

// AFTER
router.Handle("/health/live", registry.LiveHandler())
```

### 2. Contract Migration Strategy

**Decision**: Move `order-service/contracts/order/` → `services/order-service/contracts/order/`

The `order-service/` is currently outside `services/`. This migration:
1. Creates `services/order-service/` directory structure
2. Moves domain contracts to align with other services
3. Removes `order-service/contracts/` (or keeps only service-specific overrides)

### 3. Deploy Documentation Strategy

**Decision**: Keep both deploy structures, document intended usage.

- `order-service/deploy/` → documented as "standalone local development"
- `deploy/` → documented as "composed environment overlays"

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Health API rewrite breaks multiple call sites | High | Systematic update of all roles (api, worker, orchestrator) |
| Runtime health check construction changes | Medium | Update `runtime.Build*ReadinessChecks()` functions |
| Contract import paths change | Low | IDE refactor + verify build |
| Documentation not followed | Low | Add to onboarding docs |

## Migration Plan

### Phase 1: Health Package Migration

```bash
# 1. Update runtime readiness check functions
# File: order-service/internal/runtime/healthcheck.go
# - Change return type from map[string]health.Check to use Registry
# - Create named Check implementations

# 2. Update roles.go main functions
# Files: order-service/cmd/order-service/roles.go
# - Update probe construction for api, worker, orchestrator roles
# - Change from health.New() to registry.Register()

# 3. Update router
# File: order-service/internal/adapters/http/router.go
# - Mount registry handlers instead of probe methods

# 4. Remove service health package after migration
rm -rf order-service/internal/health/

# 5. Verify build
cd order-service && go build ./...
```

### Phase 2: Contract Migration

```bash
# 1. Create services directory structure
mkdir -p services/order-service/contracts

# 2. Move domain contracts
mv order-service/contracts/order services/order-service/contracts/

# 3. Update imports
# All files importing "order-service/contracts/order" → "services/order-service/contracts/order"

# 4. Remove or deprecate re-exports
# order-service/contracts/platform/ → platform/contracts/ (already there)
```

### Phase 3: Documentation

```bash
# 1. Update deploy/README.md with usage patterns
# 2. Create platform/docs/runtime-boundaries.md
# 3. Archive completed change
```

## Open Questions

None - all questions resolved during investigation.
