# Tasks: Release and Roll Out TDT Home Provider

Each task is one focused work session. Depends on all prior changes being
complete: provider foundation, source conformance, and migration engine.

## 1. Release artifact

- [ ] 1.1 Build provider wheel and locked dependency closure into a fresh local wheelhouse (no checkout, no PYTHONPATH).
- [ ] 1.2 Install provider from wheelhouse into a clean virtual environment.
- [ ] 1.3 Verify version equality between distribution metadata and runtime `__version__`.
- [ ] 1.4 Verify `tdt --help` and `tdt config doctor` run without scheduler extras.
- [ ] 1.5 Verify package resources load correctly (source-registry.json, schemas).
- [ ] 1.6 Run provider-only contract tests in the clean environment.

## 2. Internal registry publication

- [ ] 2.1 Publish provider wheel to internal package registry (if applicable).
- [ ] 2.2 Verify registry availability from a clean environment.
- [ ] 2.3 Document the publication process and version tagging convention.

## 3. Staged consumer rollout

- [ ] 3.1 Select first consumer for rollout (recommend: `agent-core` — low fanout, good test coverage).
- [ ] 3.2 Update consumer dependency to use published provider wheel.
- [ ] 3.3 Run consumer test suite with provider loaded from installed package.
- [ ] 3.4 Verify consumer behavior unchanged (smoke tests, existing test suite).
- [ ] 3.5 Repeat for each remaining consumer, one at a time with verification gates.
- [ ] 3.6 Record rollout status for all 15 repositories.

## 4. Reverse rollback rehearsal

- [ ] 4.1 Simulate provider rejection: restore pre-change tdt-core artifact in a test environment.
- [ ] 4.2 Verify consumer behavior remains available after rollback.
- [ ] 4.3 Document the rollback procedure and time estimate.
- [ ] 4.4 Verify no live ~/.tdt data was modified during rehearsal.

## 5. Release gates

- [ ] 5.1 All consumer rollout verifications pass.
- [ ] 5.2 Rollback rehearsal successful.
- [ ] 5.3 Documentation updated with release notes and consumer migration guide.
- [ ] 5.4 Run `openspec validate --all --strict` and `openspec store doctor`.

## Archive gate

Do not archive until staged rollout is complete for all consumers, rollback
rehearsal passes, and documentation is final.
