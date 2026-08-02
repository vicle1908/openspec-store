# harness-artifact-integrity Specification

## Purpose
Ensures harness artifacts and durable checkpoints are self-describing, atomically persisted, and verified before they can be resumed, reported, or used as evidence.
## Requirements
### Requirement: Atomic artifact envelope

An accepted artifact SHALL be persisted as one versioned envelope containing its identity, source/input references, content digest, validation result, writer/store provenance, and storage commit identity; partial JSON or digest sidecars SHALL never be authoritative. A filesystem store SHALL commit with same-filesystem temporary write, file flush, atomic rename, then containing-directory flush in that order. A backend that cannot provide and attest the declared durability class SHALL fail closed or expose a separately named weaker class that is ineligible for durable checkpoints.

#### Scenario: Artifact commit succeeds

- **WHEN** a stage accepts an artifact
- **THEN** the store SHALL flush the temporary envelope, atomically rename it, flush the containing directory, and only then report durable commit success
- **AND** readers SHALL verify the digest before returning the artifact

#### Scenario: Artifact commit is interrupted

- **WHEN** persistence fails between content and metadata writes
- **THEN** the incomplete envelope SHALL not be readable as accepted
- **AND** retry SHALL either complete the same identity or report a bounded failure

#### Scenario: Concurrent writers target one revision

- **WHEN** two writers attempt to commit the same artifact identity or revision
- **THEN** compare-and-swap or equivalent create-if-absent semantics SHALL permit at most one matching durable commit
- **AND** a conflicting digest, writer, store, or expected revision SHALL fail without replacing accepted evidence

### Requirement: Verified checkpoint references

Durable checkpoints SHALL contain bounded artifact references and immutable source identities rather than full artifact bodies or live service objects. A reference SHALL be publishable only after the artifact store reports durable commit success. When artifact and checkpoint stores cannot share a transaction, a recoverable commit-marker/outbox protocol SHALL make uncommitted references invisible and replay publication idempotently.

#### Scenario: Resume reads a reference

- **WHEN** a process resumes a checkpoint
- **THEN** it SHALL reconstruct configured services, resolve each referenced envelope, and verify identity, digest, schema, and freshness before continuing

#### Scenario: Reference is missing or mismatched

- **WHEN** an artifact reference is missing, stale, malformed, or has a digest mismatch
- **THEN** resume SHALL fail closed with an actionable integrity diagnostic
- **AND** it SHALL not synthesize an empty artifact

#### Scenario: Crash crosses an artifact/checkpoint boundary

- **WHEN** a process stops after any temporary-write, file-flush, rename, directory-flush, commit-marker, outbox, or checkpoint-publication boundary
- **THEN** recovery SHALL expose either the prior checkpoint or the new fully verified artifact reference, never a partial or orphan-authoritative state
- **AND** retry SHALL be bounded and idempotent

### Requirement: Artifact provenance is verified

Artifact verification SHALL validate the trusted writer identity, store identity, commit identity, source/input identities, and schema in addition to content digests.

#### Scenario: Digest matches but provenance does not

- **WHEN** content has the expected digest but its writer, store, commit, source, or input provenance is missing or untrusted
- **THEN** resume and report SHALL reject the artifact as readiness evidence
- **AND** diagnostics SHALL identify the provenance field without exposing credentials

