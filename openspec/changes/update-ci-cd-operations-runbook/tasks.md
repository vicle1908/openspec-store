# Tasks: Synchronize CI/CD Operations Runbook with Modernized Architecture and 4-Tier Matrix DAG

## 1. OpenSpec Change Authoring & Strict Validation

- [ ] 1.1 Author `proposal.md`, `design.md`, and `tasks.md` in `openspec-store` under `openspec/changes/update-ci-cd-operations-runbook/`
- [ ] 1.2 Validate change strictly using `openspec validate update-ci-cd-operations-runbook --strict --store openspec-store`
- [ ] 1.3 Commit and push the OpenSpec proposal to `openspec-store` `main`

## 2. Monorepo Documentation Updates (`go-microservices`)

- [ ] 2.1 Update `docs/runbooks/ci-cd-operations.md` to:
  - Document the 4-tier parallel matrix DAG in `verify.yml` (`preflight`, `platform-verify`, `service-verify-matrix` with `fail-fast: false`, `verify-pr` rollup aggregator anchor)
  - Document headless Newman CI automated API integration and E2E saga test execution in `lgtm-e2e.yml`
  - Document host loopback endpoint resolution (`http://127.0.0.1:<PORT>`) in Newman CI environments
  - Document unit test database connection pool lazy initialization (`MinConns = 0`)
  - Cross-reference ADR 0009 and Notion architecture guide `3eec4b21-deb4-8186-abc7-d0715d40f7bb`
- [ ] 2.2 Update `docs/README.md` runbook references if necessary
- [ ] 2.3 Run `make pre-push` locally in `go-microservices` to verify whitespace, agent guidance word counts, coverage documentation parity, and documentation validation

## 3. Pull Request Lifecycle & Pipeline Monitoring

- [ ] 3.1 Create feature branch `docs/sync-ci-cd-operations-runbook` in `go-microservices`
- [ ] 3.2 Commit documentation updates and push to origin
- [ ] 3.3 Open GitHub Pull Request, arm auto-merge, and monitor PR check runs live
- [ ] 3.4 Resolve any gate failures or documentation issues until auto-merge completes cleanly
- [ ] 3.5 Pull `main` in `go-microservices` and prune feature branch locally and remotely

## 4. OpenSpec Archival & Knowledge Synchronization

- [ ] 4.1 Mark all tasks completed in `openspec-store`
- [ ] 4.2 Validate strict OpenSpec compliance and archive change to `openspec/changes/archive/2026-10-04-update-ci-cd-operations-runbook`
- [ ] 4.3 Commit and push archived change in `openspec-store`
- [ ] 4.4 Save durable learnings in `agentmemory` and update Notion via `ntn` CLI
