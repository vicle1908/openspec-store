## Why

The local implementation and retained acceptance evidence have moved ahead of
several documentation and normative-spec references. Coverage values are stale,
catalog CDC documentation still says registration is unimplemented, the
platform-verification spec names a retired smoke command and artifact path, and
the operational runbook contract lists seven services while the platform has
eight. Without an evidence-backed currency contract, future readiness claims
can drift from the commands and artifacts that actually govern the repository.

## What Changes

- Refresh local verification documentation from the current per-service
  coverage summaries and retain the evidence date and schema.
- Correct service documentation to describe the implemented catalog CDC
  registration and the canonical shared/local runbook boundaries.
- Update the platform-verification smoke requirement to use `make dev-smoke`
  and its timestamped machine-readable report, while preserving compatibility
  targets as non-authoritative aids.
- Update operational runbook requirements and indexes to cover all eight
  services and distinguish root operational runbooks from service-local
  runbooks and the shared local CDC runbook.
- Add an evidence-backed documentation and specification currency capability
  requiring canonical commands, artifact schemas, service inventories, and
  status annotations to be checked against current implementation evidence.
- Verify mirrored OpenSpec skill copies remain identical; do not hand-edit
  generated or mirrored skill files.

## Capabilities

### New Capabilities

- `documentation-currency`: Defines evidence-backed documentation, normative
  status, service inventory, command/artifact references, and generated skill
  parity requirements.

### Modified Capabilities

- `platform-verification`: Replace the retired cross-service smoke command and
  `e2e-cross-service.json` path with the canonical `dev-smoke` evidence
  contract.
- `operational-readiness`: Expand the service-runbook requirement to the
  complete eight-service topology and clarify readiness versus source-level
  implementation status.
- `operational-runbooks`: Make the runbook index and discovery contract
  explicit about available root runbooks, service-local runbooks, and shared
  operational procedures.

## Impact

- **Documentation**: `docs/local-service-verification.md`,
  `docs/runbooks/README.md`, service READMEs, and deployment/readiness
  references.
- **OpenSpec**: one new capability and deltas to three existing capabilities;
  no archived change artifacts are edited.
- **Validation**: documentation/spec consistency checks and mirrored skill
  parity checks may be added to the local documentation gate.
- **Runtime/API compatibility**: no service code, public API, event contract,
  database schema, deployment image, or cloud resource changes.
- **Evidence**: current local coverage, smoke, CDC, and deployment manifests
  remain the source evidence; cloud readiness remains outside this change.
