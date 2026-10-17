# cleanup-archive-verification Specification Delta

## MODIFIED Requirements

### Requirement: Archive evidence uses one standardized form

Changes that perform verification SHALL record their verification evidence in a single `evidence.md` file inside the change directory. Guidance for this artifact SHALL be named in the store's archive operations guidance. The legacy `evidence/` directory form remains valid only for changes already archived with it and SHALL NOT be used for new changes.

#### Scenario: A change records verification evidence
- **WHEN** a change completes verification work before archiving
- **THEN** its evidence is written to `evidence.md` in the change directory
- **AND** the change does not also create an `evidence/` directory

#### Scenario: Archive readiness gate enforces evidence.md and .openspec.yaml
- **WHEN** `scripts/validate-archive-readiness.py` evaluates an active change containing tracked tasks (`task_summary.total > 0`)
- **THEN** it SHALL verify that `.openspec.yaml` exists and that a non-empty `evidence.md` file exists in the change directory
- **AND** if `.openspec.yaml` or `evidence.md` is missing or empty, `validate-archive-readiness.py` SHALL report a non-ready status (`INVALID` / `NOT_READY`) and exit non-zero

#### Scenario: Range audit enforces evidence.md on post-2026-10-17 archives while grandfathering older archives
- **WHEN** `scripts/validate-archive-readiness.py --range <rev-range>` audits archived change directories added in a Git commit range
- **THEN** archives dated after `2026-10-17` with `task_summary.total > 0` SHALL be required to contain a non-empty `evidence.md`
- **AND** historical archives dated on or before `2026-10-17` SHALL remain grandfathered so immutable archive history is never rewritten

#### Scenario: Forward reconciliation of scheduling archives missing evidence.md
- **WHEN** an already-archived change (`2026-10-16-harden-shb-scheduler-docker-lifecycle`, `2026-10-13-durable-workstation-updater`, or the `2026-10-15` workstation/Temporal wave) was archived without `evidence.md`
- **THEN** its post-remediation verification ledger SHALL be recorded in `evidence.md` of the active corrective change while leaving `openspec/changes/archive/` byte-for-byte untouched

#### Scenario: A change performs no verification
- **WHEN** a change performs no verification work (`task_summary.total == 0`)
- **THEN** no evidence artifact is required and the change is not blocked for lacking one

#### Scenario: An existing archive uses the legacy directory form
- **WHEN** an archived change already contains an `evidence/` directory
- **THEN** it is left unchanged and is not migrated, renamed, or converted
