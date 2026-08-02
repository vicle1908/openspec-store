## Context

Recent implementation work has produced significant new capabilities without corresponding documentation updates:

- **Security packages** (pgroles, pgownership, pgconn) in platform/security — no architecture.md coverage
- **Compose overlays** (production-contract, local-fast) — no deploy/README.md coverage
- **Container hardening** (hardened-role anchor, security labels) — no deploy/README.md coverage
- **Runtime-contract** (verification/runtime-contract.json) — no deploy/README.md coverage
- **Validation scripts** (profile, hardening, network, readiness) — no deploy/README.md coverage
- **Temporal security** (TLS, Nexus) — platform/docs/temporal.md missing
- **Health probes** — platform/docs/health.md missing
- **Runbooks** — 4 new runbooks not indexed in docs/runbooks/README.md

## Approach

### 1. Create Missing Platform Docs

**platform/docs/temporal.md** — Document:
- Temporal TLS configuration (client/server mTLS)
- Nexus endpoint security (ClaimMapper, Authorizer)
- Workflow identity and task queue isolation
- Retry policy and error handling

**platform/docs/health.md** — Document:
- Health probe contracts (live, ready, startup)
- Per-service health endpoint structure
- Dependency health checks (PG, Kafka, Temporal)
- Health check timeout and retry behavior

### 2. Update deploy/README.md

Add sections for:
- **Security Contract**: runtime security modes, workload identities, SPIFFE
- **Compose Profiles**: production-contract vs local-fast usage
- **Container Hardening**: hardened-role anchor, security labels, read-only
- **Runtime Contract**: verification/runtime-contract.json purpose
- **Validation Scripts**: profile, hardening, network, readiness checks

### 3. Update docs/runbooks/README.md

Add missing runbooks to the index:
- service-runtime-security-contract
- knowledge-graphs
- temporal-nexus-shipping
- temporal-clean-slate

### 4. Update platform/docs/architecture.md

Add security packages section covering:
- platform/security (pgroles, pgownership, pgconn)
- platform/cache (Redis TLS/ACL)
- platform/http (mTLS identity, route policy)
- platform/kafka (TLS/SASL)
- platform/observability (OTLP TLS)
- platform/temporal (TLS, Nexus)

### 5. Update platform/docs/README.md

Fix table to:
- Remove temporal.md and health.md from "missing" (they'll exist)
- Add security.md or security section
- Add projection-consumers.md

## Verification

1. All files referenced in READMEs exist
2. deploy/README.md mentions all compose overlays
3. docs/runbooks/README.md indexes all runbooks
4. platform/docs/architecture.md mentions security packages
5. No broken links in documentation
