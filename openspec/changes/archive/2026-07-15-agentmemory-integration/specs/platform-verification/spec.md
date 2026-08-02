# platform-verification Specification (delta)

## Purpose
TBD - to be filled after the change is archived.

## ADDED Requirements

### Requirement: PostToolUse hook payloads carry OpenSpec context for files under openspec/
When an agent memory hook captures a `PostToolUse` event for a tool call whose file path is under `openspec/` (recursive, excluding `openspec/changes/archive/`), the hook payload SHALL include the following additional fields beyond the upstream agentmemory schema: `openspec_change` (the active change name, or `null` if the agent is not inside an active change), `openspec_artifact` (the relative path of the touched file within `openspec/changes/<change>/` or `openspec/specs/`, or `null` if not in a change), and `openspec_scenario` (the four-hash scenario heading under which the change is being implemented, or `null` if the file is not a `spec.md` or the heading cannot be resolved).

#### Scenario: Hook touches a spec.md file under an active change
- **WHEN** Claude Code's `PostToolUse` hook fires for a `Read` of `openspec/changes/agentmemory-integration/specs/developer-memory/spec.md`
- **THEN** the payload sent to `POST /agentmemory/observe` includes `openspec_change: "agentmemory-integration"`, `openspec_artifact: "specs/developer-memory/spec.md"`, and `openspec_scenario: null` (no scenario can be resolved from a `Read` of the file as a whole)

#### Scenario: Hook touches a non-spec file under openspec/
- **WHEN** the hook fires for an `Edit` of `openspec/config.yaml`
- **THEN** the payload includes `openspec_change: null`, `openspec_artifact: "config.yaml"`, and `openspec_scenario: null`

#### Scenario: Hook touches a file outside openspec/
- **WHEN** the hook fires for a `Read` of `order-service/internal/domain/order/order.go`
- **THEN** the payload includes `openspec_change: null`, `openspec_artifact: null`, and `openspec_scenario: null` (no overhead is added for non-OpenSpec files)

#### Scenario: Hook touches an archived change
- **WHEN** the hook fires for a `Read` of `openspec/changes/archive/2026-07-15-order-service-mvp/proposal.md`
- **THEN** the payload includes `openspec_change: null` and `openspec_artifact: null` (archived changes are read-only context and SHALL NOT be tagged as active)

### Requirement: traceability.yaml records agentmemory references for in-scope observations
When a captured observation is mapped to a verification ID in `verification/traceability.yaml` (i.e., the observation is the evidence for a `PV-XXX` entry), the verification harness SHALL append an `agentmemory://observations/<id>` reference to the entry's `evidence` list. The reference SHALL be the canonical URL the agentmemory server returns for the observation and SHALL be stable across the lifetime of the memory entry.

#### Scenario: Hook observation becomes evidence for a verification
- **WHEN** a developer runs `make verify-images` and the smoke test fires a hook that captures a `PostToolUse` observation of a `Read` of `deploy/docker-compose.yaml`
- **THEN** `verification/traceability.yaml` includes a `PV-XXX` entry whose `evidence` list contains the line `- agentmemory://observations/<id>` and the observation can be retrieved with `curl -fsS $AGENTMEMORY_URL/agentmemory/observations/<id>`

#### Scenario: Observation without a verification ID is not recorded in traceability
- **WHEN** a hook fires for a file outside the verification scope (e.g., a `Read` of `README.md`)
- **THEN** no `agentmemory://` reference is added to `verification/traceability.yaml` (the memory lives only in the agentmemory audit log, not in the project manifest)

### Requirement: OpenSpec validation rejects hooks that fail the contract
The release-gate step that runs `openspec validate --strict --all` SHALL be extended to also run `scripts/agentmemory-doctor.sh` (when the `agentmemory` change is active) and SHALL fail the release if `agentmemory-doctor` exits non-zero. The doctor check SHALL run before the cross-service smoke test so that a misconfigured memory layer is caught before downstream services consume it.

#### Scenario: agentmemory-doctor fails during a release tag
- **WHEN** a `v*` tag is pushed and the release-evidence workflow runs `scripts/agentmemory-doctor.sh` and the doctor reports a red row
- **THEN** the workflow exits non-zero, the year-long artifact is NOT published, and the tag is not annotated as shippable

#### Scenario: agentmemory-doctor passes during a release tag
- **WHEN** the doctor reports all green or yellow rows
- **THEN** the workflow proceeds to the cross-service smoke test and `openspec validate --strict --all`

## REMOVED Requirements

### Requirement: Cross-service smoke test does not validate agentmemory
**Reason**: This requirement was an early placeholder; the agentmemory contract is now validated by `TestAgentMemoryContract` under the new `developer-memory` capability, and the platform-verification spec only needs to gate the release on `agentmemory-doctor` (handled by the ADDED requirements above).
**Migration**: Moved to `specs/developer-memory/spec.md` as `### Requirement: CI sidecar provides the same contract`.
