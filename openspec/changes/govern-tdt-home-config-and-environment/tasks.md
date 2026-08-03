# Tasks: TDT_HOME Provider Foundation

Each task is provider-owned, limited to one focused work session, and includes a verification gate. Keep every task unchecked until the implementation and its named evidence pass on the canonical `tdt-core-home-security-kernel` worktree.

## 1. Baseline and traceability

- [ ] 1.1 Record the provider worktree, branch, HEAD, dirty fingerprint, nearest `AGENTS.md`, Python/uv identity, package version, and focused verification commands.
- [ ] 1.2 Run GitNexus impact analysis for each provider symbol selected for editing and record any critical or high-risk result before implementation continues.
- [ ] 1.3 Add a value-free fixture for the legacy root containing duplicate config sources, a secret-shaped setting, a broken credential link, runtime files, and mixed permissions.
- [ ] 1.4 Create a requirement-to-test-to-source matrix covering all delta requirements and scenarios; identify scenarios that remain intentionally deferred.

## 2. RED behavior tests

- [ ] 2.1 Add failing tests for explicit, unset, empty, tilde, relative, and post-import `TDT_HOME` behavior.
- [ ] 2.2 Add failing tests for development/production profile precedence, process-only profile selection, unknown profiles, and local dotenv handling.
- [ ] 2.3 Add failing tests for concurrent initialization, failed-load retry, repeated calls, and exact test-isolation restoration.
- [ ] 2.4 Add failing tests for path-component validation, containment, root anchoring, approved bootstrap, and descendant substitution.
- [ ] 2.5 Add failing tests for typed secret references, literal-secret rejection, duplicate scheduler settings, conflict handling, and redacted missing-reference errors.
- [ ] 2.6 Add failing tests for doctor findings, package-resource failure, base CLI behavior, and clean installed-provider execution.

## 3. Bounded paths and security kernel

- [ ] 3.1 Implement validated components and dynamic config, credential, schedule, log, state, and runtime path helpers backed by `tdt_root()`.
- [ ] 3.2 Implement existing-root anchoring and approved first-run bootstrap with descriptor identity and ownership checks.
- [ ] 3.3 Implement descriptor-relative private directory creation and protected regular-file open/replace operations with no unsafe pathname fallback.
- [ ] 3.4 Add platform-capability checks for required no-follow, descriptor-relative, synchronization, and identity primitives; fail mutation closed when unavailable.
- [ ] 3.5 Verify symlink substitution, hard-link policy, object-type policy, permission policy, descriptor cleanup, and concurrent directory creation.

## 4. Environment and typed configuration

- [ ] 4.1 Implement process-selected development/production profile loading with call-time root evaluation and redacted source provenance.
- [ ] 4.2 Implement one-time initialization, lock-scoped test isolation, failed-load rollback, retry, and concurrent caller behavior.
- [ ] 4.3 Implement typed configuration parsing with full-scalar environment references, secret-shaped key classification, and redacted errors.
- [ ] 4.4 Implement deterministic duplicate normalization and scheduler ownership/conflict handling through the governed parser.
- [ ] 4.5 Register the base `tdt` CLI and implement provider-only command dispatch without requiring scheduler extras.
- [ ] 4.6 Implement redacting doctor text/JSON/strict modes with explicit-root operation and no workspace import dependency.

## 5. Provider schemas and packaged contracts

- [ ] 5.1 Keep provider-owned path, secret-reference, principal, and package-contract schemas strict about types, identities, versions, and unsafe components.
- [ ] 5.2 Package registry/schema/rule resources through the supported package-resource mechanism and test missing-resource failure.
- [ ] 5.3 Validate packaged participant identity, uniqueness, required fields, and redacted diagnostics from an installed provider.

## 6. Provider verification and release artifact

- [ ] 6.1 Run the complete provider pytest suite, including every RED/GREEN and adversarial security test; record failures without weakening requirements.
- [ ] 6.2 Run Ruff, formatting, strict mypy, and an added-lines secret/redaction scan on the canonical provider worktree.
- [ ] 6.3 Build the provider wheel and locked dependency closure into a fresh local wheelhouse; record a value-free artifact/hash inventory.
- [ ] 6.4 Install the provider from the wheelhouse with no checkout and no `PYTHONPATH`; verify version equality, `tdt --help`, package resources, doctor, and provider contract smokes.
- [ ] 6.5 Document provider layout, profile trust, secret-reference grammar, transaction boundaries, compatibility, and rollback without documenting deferred consumer facts as if they were known.

## 7. Final OpenSpec verification

- [ ] 7.1 Re-run the requirement/scenario evidence matrix and resolve every uncovered provider scenario or record an explicit bounded reason.
- [ ] 7.2 Run GitNexus compare/detect checks against the provider branch and classify every changed path as change-owned or unrelated.
- [ ] 7.3 Run focused strict validation for the change and the modified capability, then run full `openspec validate --all --strict` and `openspec store doctor`.
- [ ] 7.4 Perform the semantic second-pass review for one-behavior requirements, one-session tasks, ownership boundaries, and deferred successor work before considering archive.

## Deferred work

The following are not tasks in this provider change and must be created as separately owned successor changes:

- Consumer/deployment manifests and source conformance audit.
- Synthetic migration plan compilation, journaled apply, and recovery.
- Per-consumer source and dependency migrations.
- Provider rollout and reverse rollback rehearsal.
- Live operator migration of `~/.tdt`.

## Archive gate

Do not sync or archive this change until all provider tasks are evidenced, the canonical provider worktree is clean, all provider gates pass, the semantic verification report has no critical issues, and each deferred successor has an explicit owner and scope.
