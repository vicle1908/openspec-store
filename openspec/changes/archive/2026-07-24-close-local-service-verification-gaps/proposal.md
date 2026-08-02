## Why

The repository-wide local code gate is fail-closed but cannot pass: aggregate
service coverage ranges from 18.3% to 57.2%, inventory and shipping require
missing fuzz runners, and generated-contract verification depends on a
rate-limited remote Buf plugin. These are local development correctness and
repeatability gaps, separate from cloud deployment and CI/CD rollout.

## What Changes

- Raise all eight services to the existing 80% aggregate coverage gate while
  preserving the finer domain/application/adapter targets.
- Add deterministic fuzz suites and seed corpora for inventory and shipping,
  then make their `verify-pr` targets run them fail-closed.
- Make generated-contract checks reproducible with pinned tooling and a
  documented authenticated/offline path that does not silently skip validation.
- Add regression coverage for traceability, build-tag isolation, trimpath-safe
  architecture tests, Compose validation, and shuffled test execution.
- Retain per-service verification evidence and document any external-service
  prerequisite without weakening the gate.
- Exclude cloud deployment, hosted CI scheduling, and production promotion.

## Capabilities

### New Capabilities

- `local-service-verification`: Defines a reproducible, fail-closed local
  verification contract for coverage, fuzzing, generated contracts,
  architecture checks, and evidence across all service modules.

### Modified Capabilities

None. Existing coverage and fuzz specifications retain their requirements; this
change implements and unifies their local enforcement.

## Impact

- Affects all eight service Makefiles and tests, with the largest additions in
  currently low-coverage adapters/runtime packages.
- Adds inventory/shipping fuzz targets and corpus data without changing public
  APIs or data ownership.
- May add pinned local Buf/protoc plugin installation metadata or cache
  bootstrap, but does not change protobuf wire contracts.
- Rolls out one service at a time; rollback reverts test/tooling changes only
  and has no runtime data migration.
