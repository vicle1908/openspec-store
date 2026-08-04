# Tasks: Release and Roll Out TDT Home Provider

Each task is one focused work session. Depends on all prior changes being
complete: provider foundation, source conformance, and migration engine.

## 1. Release artifact

- [x] 1.1 Build provider wheel and locked dependency closure into a fresh local wheelhouse (no checkout, no PYTHONPATH).
- [x] 1.2 Install provider from wheelhouse into a clean virtual environment.
- [x] 1.3 Verify version equality between distribution metadata and runtime `__version__`.
- [x] 1.4 Verify `tdt --help` and `tdt config doctor` run without scheduler extras.
- [x] 1.5 Verify package resources load correctly (source-registry.json, schemas).
- [x] 1.6 Run provider-only contract tests in the clean environment.

## 2. Internal registry publication

- [ ] 2.1 Publish provider wheel to internal package registry (if applicable).
- [ ] 2.2 Verify registry availability from a clean environment.
- [x] 2.3 Document the publication process and version tagging convention.

## 3. Staged consumer rollout

- [ ] 3.1 Select a target only after its deployment owner, runtime principal,
  configuration owner, compatibility evidence, maintenance window, and
  approval are recorded.
- [ ] 3.2 Install the immutable published provider artifact in the selected
  target; any consumer dependency-metadata change belongs to that consumer's
  provider-gated adoption change.
- [ ] 3.3 Run the consumer test suite and smoke checks with the provider loaded
  from the qualified installed artifact.
- [ ] 3.4 Verify consumer behavior unchanged (smoke tests, existing test suite).
- [ ] 3.5 Repeat for each approved target one at a time, stopping on any failed
  gate or withdrawn approval; do not promote automatically.
- [x] 3.6 Record provider, staging, consumer, deployment, and live-root scopes
  separately for all 15 participants, including unverified and blocked states.

## 4. Reverse rollback rehearsal (integrated per consumer)

For each consumer promoted in Task 3:
- [ ] 4.1 Simulate provider rejection by restoring the exact pre-change
  artifact and closure in a disposable or staging target.
- [ ] 4.2 Verify the promoted consumer's behavior remains available after rollback.
- [ ] 4.3 Record rollback evidence (exit code, test output, timing) per consumer.

After all consumers are promoted and rehearsed:
- [ ] 4.4 Document the consolidated rollback procedure and time estimate.
- [ ] 4.5 Verify no live ~/.tdt data was modified during any rehearsal.

## 5. Release gates

- [ ] 5.1 All provider, registry, staging, and explicitly approved consumer
  rollout gates pass; missing consumer evidence remains blocked.
- [ ] 5.2 Rollback rehearsal successful.
- [ ] 5.3 Documentation updated with release notes and consumer migration guide.
- [x] 5.4 Run `openspec validate --all --strict` and `openspec store doctor`.

## Archive gate

Do not archive until staged rollout is complete for all consumers, rollback
rehearsal passes, and documentation is final.

## Evidence boundary

The retained evidence proves provider build/install/version checks (tasks 1.1–1.3),
participant-scope recording, publication-process documentation, and the OpenSpec
validation gate. The combined CLI/doctor task 1.4 is not complete because the
retained doctor invocation used the default live root rather than an isolated
qualification root; package-resource and provider-contract evidence for tasks
1.5–1.6 is absent. Publication was not executed because no approved internal
registry coordinate or operator authorization is present. Registry availability,
target selection, consumer installation/tests/behavior, rollback rehearsal, and
release gates 5.1–5.3 are explicitly blocked or pending execution. The
participant-scope record names all 15 participants but records zero approved
consumers. Process documentation is not execution evidence, so this change
remains open and must not be archived.
