# Tasks: TDT_HOME Provider Foundation

Each task is provider-owned, limited to one focused work session, and includes a verification gate. Keep every task unchecked until the implementation and its named evidence pass on the canonical `tdt-core-home-security-kernel` worktree.

Evidence is recorded in `tdt-core/PROVIDER_EVIDENCE.md`. The implementation
candidate is `6fe4712`; canonical evidence hardening is integrated at `518ac81`
and the final release-hash record at `1e212d2`. Runtime mutation of the real
`~/.tdt` root and downstream consumer adoption remain explicitly deferred.

## 1. Baseline and traceability

- [x] 1.1 Record the provider worktree, branch, HEAD, dirty fingerprint, nearest `AGENTS.md`, Python/uv identity, package version, and focused verification commands.
- [x] 1.2 Run GitNexus impact analysis for each provider symbol selected for editing and record any critical or high-risk result before implementation continues.
- [x] 1.3 Add a value-free fixture for the legacy root containing duplicate config sources, a secret-shaped setting, a broken credential link, runtime files, and mixed permissions.
- [x] 1.4 Create a requirement-to-test-to-source matrix covering all delta requirements and scenarios; identify scenarios that remain intentionally deferred.

## 2. RED behavior tests

- [x] 2.1 Add failing tests for explicit, unset, empty, tilde, relative, and post-import `TDT_HOME` behavior.
- [x] 2.2 Add failing tests for development/production profile precedence, process-only profile selection, unknown profiles, and local dotenv handling.
- [x] 2.3 Add failing tests for concurrent initialization, failed-load retry, repeated calls, and exact test-isolation restoration.
- [x] 2.4 Add failing tests for path-component validation, containment, root anchoring, approved bootstrap, and descendant substitution.
- [x] 2.5 Add failing tests for typed secret references, literal-secret rejection, duplicate scheduler settings, conflict handling, and redacted missing-reference errors.
- [x] 2.6 Add failing tests for doctor findings, package-resource failure, base CLI behavior, and clean installed-provider execution.

## 3. Bounded paths and security kernel

- [x] 3.1 Implement validated components and dynamic config, credential, schedule, log, state, and runtime path helpers backed by `tdt_root()`.
- [x] 3.2 Implement existing-root anchoring and approved first-run bootstrap with descriptor identity and ownership checks.
- [x] 3.3 Implement descriptor-relative private directory creation and protected regular-file open/replace operations with no unsafe pathname fallback.
- [x] 3.4 Add platform-capability checks for required no-follow, descriptor-relative, synchronization, and identity primitives; fail mutation closed when unavailable.
- [x] 3.5 Verify symlink substitution, hard-link policy, object-type policy, permission policy, descriptor cleanup, and concurrent directory creation.

## 4. Environment and typed configuration

- [x] 4.1 Implement process-selected development/production profile loading with call-time root evaluation and redacted source provenance.
- [x] 4.2 Implement one-time initialization, lock-scoped test isolation, failed-load rollback, retry, and concurrent caller behavior.
- [x] 4.3 Implement typed configuration parsing with full-scalar environment references, secret-shaped key classification, and redacted errors.
- [x] 4.4 Implement deterministic duplicate normalization and scheduler ownership/conflict handling through the governed parser.
- [x] 4.5 Register the base `tdt` CLI and implement provider-only command dispatch without requiring scheduler extras.
- [x] 4.6 Implement redacting doctor text/JSON/strict modes with explicit-root operation and no workspace import dependency.

## 5. Provider schemas and packaged contracts

- [x] 5.1 Keep provider-owned path, secret-reference, principal, and package-contract schemas strict about types, identities, versions, and unsafe components.
- [x] 5.2 Package registry/schema/rule resources through the supported package-resource mechanism and test missing-resource failure.
- [x] 5.3 Validate packaged participant identity, uniqueness, required fields, and redacted diagnostics from an installed provider.

## 6. Provider verification and release artifact

- [x] 6.1 Run the complete provider pytest suite, including every RED/GREEN and adversarial security test; record failures without weakening requirements.
- [x] 6.2 Run Ruff, formatting, strict mypy, and an added-lines secret/redaction scan on the canonical provider worktree.
- [x] 6.3 Build the provider wheel and locked dependency closure into a fresh local wheelhouse; record a value-free artifact/hash inventory.
- [x] 6.4 Install the provider from the wheelhouse with no checkout and no `PYTHONPATH`; verify version equality, `tdt --help`, package resources, doctor, and provider contract smokes.
- [x] 6.5 Document provider layout, profile trust, secret-reference grammar, transaction boundaries, compatibility, and rollback without documenting deferred consumer facts as if they were known.

## 7. Final OpenSpec verification

- [x] 7.1 Re-run the requirement/scenario evidence matrix and resolve every uncovered provider scenario or record an explicit bounded reason.
- [x] 7.2 Run GitNexus compare/detect checks against the provider branch and classify every changed path as change-owned or unrelated.
- [x] 7.3 Run focused strict validation for the change and the modified capability, then run full `openspec validate --all --strict` and `openspec store doctor`.
- [x] 7.4 Perform the semantic second-pass review for one-behavior requirements, one-session tasks, ownership boundaries, and deferred successor work before considering archive.

## Deferred work

The following are not tasks in this provider change and must be created as separately owned successor changes:

- Consumer/deployment manifests and source conformance audit.
- Synthetic migration plan compilation, journaled apply, and recovery.
- Per-consumer source and dependency migrations.
- Provider rollout and reverse rollback rehearsal.
- Live operator migration of `~/.tdt`.

## Archive gate

Do not sync or archive this change until all provider tasks are evidenced, the canonical provider worktree is clean, all provider gates pass, the semantic verification report has no critical issues, and each deferred successor has an explicit owner and scope.
