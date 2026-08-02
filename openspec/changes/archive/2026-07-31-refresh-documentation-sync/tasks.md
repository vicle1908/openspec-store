## 1. Platform Documentation

- [x] 1.1 Create `platform/docs/temporal.md` documenting Temporal TLS, Nexus security, workflow identity, and task queue isolation
- [x] 1.2 Create `platform/docs/health.md` documenting health probe contracts (live/ready/startup), per-service endpoints, and dependency checks
- [x] 1.3 Update `platform/docs/architecture.md` adding security packages section (pgroles, pgownership, pgconn, Redis/HTTP/Kafka/OTLP/Temporal security)
- [x] 1.4 Update `platform/docs/README.md` fixing table to reference temporal.md, health.md, and add security packages

## 2. Deployment Documentation

- [x] 2.1 Update `deploy/README.md` adding security contract section (runtime security modes, workload identities, SPIFFE)
- [x] 2.2 Update `deploy/README.md` adding compose profiles section (production-contract vs local-fast usage)
- [x] 2.3 Update `deploy/README.md` adding container hardening section (hardened-role anchor, security labels, read-only)
- [x] 2.4 Update `deploy/README.md` adding runtime-contract and validation scripts sections

## 3. Runbook Index

- [x] 3.1 Update `docs/runbooks/README.md` indexing service-runtime-security-contract runbook
- [x] 3.2 Update `docs/runbooks/README.md` indexing knowledge-graphs runbook
- [x] 3.3 Update `docs/runbooks/README.md` indexing temporal-nexus-shipping runbook
- [x] 3.4 Update `docs/runbooks/README.md` indexing temporal-clean-slate runbook

## 4. Verification

- [x] 4.1 Verify all files referenced in READMEs exist
- [x] 4.2 Verify deploy/README.md mentions all compose overlays
- [x] 4.3 Verify docs/runbooks/README.md indexes all runbooks
- [x] 4.4 Verify platform/docs/architecture.md mentions security packages
- [x] 4.5 Run `openspec validate --all` to confirm no regressions
