## 1. Evidence and inventory baselines

- [x] 1.1 Define the documentation evidence inputs and schema checks for all eight service coverage summaries, the seven CDC connector inventory, the canonical Compose smoke report, Compose acceptance evidence, and deployment-validation manifests.
- [x] 1.2 Add a deterministic service-inventory check that distinguishes the eight deployable services from the seven local CDC outbox owners and reports missing or extra entries.
- [x] 1.3 Declare the twelve current OpenSpec workflow skill pairs under `.agents/skills` and `.codex/skills`, then add a parity check that compares them without modifying generated mirrors.

## 2. Documentation refresh

- [x] 2.1 Update `docs/local-service-verification.md` with current passing coverage values, evidence date, summary schema, and the canonical local verification commands.
- [x] 2.2 Correct `services/catalog-service/README.md` and affected service READMEs so catalog CDC registration and shared versus service-local runbook ownership match the implementation.
- [x] 2.3 Reconcile `docs/runbooks/README.md` with the eight-service inventory, available root/shared runbooks, and links to service-local runbooks, while preserving explicit planned/partial statuses.
- [x] 2.4 Review deployment and root README command references for retired smoke commands or artifact paths and update only references that are not historical snapshots.

## 3. Normative specification alignment

- [x] 3.1 Apply the `platform-verification` delta so the canonical smoke requirement uses `make dev-smoke`, exact timestamped reports, and `make dev-evidence`.
- [x] 3.2 Apply the `operational-readiness` delta so the runbook requirement covers all eight deployable services and distinguishes shared procedures from service-specific runbooks.
- [x] 3.3 Apply the `operational-runbooks` delta so the index/discovery requirement identifies root, shared, service-local, planned, and partial runbook states.
- [x] 3.4 Add the `documentation-currency` capability requirements for evidence-bound references, topology counts, bounded readiness status, and skill parity.

## 4. Focused validation and compatibility

- [x] 4.1 Add regression tests for stale smoke command/path detection, service inventory drift, coverage-summary consistency, and mirrored skill parity.
- [x] 4.2 Validate all documentation links and runbook index entries, including service-local relative paths, without treating archived historical references as current documentation.
- [x] 4.3 Run `openspec validate --strict --all` and verify every modified requirement retains complete scenarios and status semantics.
- [x] 4.4 Run `make validate-agent-guidance`, the focused documentation checks, and the existing local verification/deployment evidence checks; retain reports tied to the current worktree digest.

## 5. Operational handoff

- [x] 5.1 Document the remaining root per-service runbook gap and assign it to the operational-readiness owner rather than claiming complete runbook coverage.
- [x] 5.2 Confirm the active cloud deployment and CI/CD change remains separate and unverified until its staging, production, and rollback evidence is available.
