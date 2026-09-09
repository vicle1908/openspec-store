## Purpose

Define fail-closed migration behavior for iCloud-hosted Git worktrees whose backing stores, hydration state, local changes, and sensitive files are not independently resolved.

## ADDED Requirements

### Requirement: Metadata inventory is non-destructive

The migration SHALL inventory worktree and `.git`-pointer metadata without opening `.git` bodies, modifying iCloud sources, or inferring whole-tree hydration from a pointer flag.

#### Scenario: Pointer metadata is available

- **WHEN** a worktree `.git` entry can be inspected with metadata-only operations
- **THEN** the inventory records type, flags where supported, and exact metadata status while leaving hydration and backing-store validity unresolved.

#### Scenario: Pointer metadata is absent or errors

- **WHEN** a `.git` entry is absent or metadata access returns an error
- **THEN** the inventory records the exact error and classifies the worktree as unresolved without deletion or Git repair in place.

### Requirement: Capacity and readability remain separate gates

The migration SHALL report destination capacity and logical-size projections separately from successfully readable bytes.

#### Scenario: Capacity exceeds logical projection

- **WHEN** free destination space exceeds the declared logical projection
- **THEN** the capacity gate may pass for that scope while readability remains unverified.

#### Scenario: Dataless entries exist

- **WHEN** metadata reports dataless entries in the declared scope
- **THEN** generalized copying SHALL remain blocked until bounded reads establish the required source coverage.

### Requirement: Sensitive-name and content safety fail closed

The migration SHALL keep sensitive-looking files out of the general recovery destination until classified, and SHALL keep per-file sensitive evidence outside OpenSpec artifacts.

#### Scenario: Sensitive-looking metadata is detected

- **WHEN** a path matches a configured sensitive category such as dotenv, credential, token, password, secret, key, or certificate
- **THEN** the path is excluded from automatic general-destination copying and only aggregate category/status metadata is placed in OpenSpec.

#### Scenario: Bounded content scan finds a sensitive assignment

- **WHEN** content scanning of a restricted pilot finds a sensitive assignment
- **THEN** the affected pilot content is quarantined, the general recovery destination remains unusable, and the secret gate remains blocked.

### Requirement: Bounded copies are independently verified

The migration SHALL copy only an explicit non-sensitive allowlist in bounded batches, exclude `.git`, preserve the iCloud source, and verify each destination file before accepting the batch.

#### Scenario: Allowlisted files copy successfully

- **WHEN** an allowlisted file is readable and the destination can be read back with matching byte count and digest
- **THEN** that file is marked verified in restricted external evidence without generalizing the result to other files or worktrees.

#### Scenario: Allowlisted file read fails

- **WHEN** a source file cannot be read
- **THEN** the exact error is recorded in restricted external evidence and the source remains preserved; the batch is not treated as complete.

### Requirement: Replacement precedes deletion

The migration SHALL verify a local snapshot, recovered Git store, or remote clone plus local-state reconciliation before any iCloud source deletion is considered.

#### Scenario: Replacement is incomplete

- **WHEN** backing-store recovery, remote provenance, local changes, or readable source coverage remains unresolved
- **THEN** deletion authorization SHALL remain absent.

#### Scenario: Replacement is verified

- **WHEN** the declared source scope, local changes, and replacement are independently verified
- **THEN** only the exact approved source path may proceed to a separate deletion gate; no bulk worktree deletion is permitted.

### Requirement: Deletion requires exact authorization

The migration SHALL require independently recorded replacement evidence and explicit authorization naming the exact source path before deleting any iCloud source.

#### Scenario: Exact path authorization and replacement evidence exist

- **WHEN** the replacement evidence covers the declared source scope and the authorization names exactly one matching source path
- **THEN** only that named path may enter the deletion operation, with the authorization and evidence retained in restricted records.

#### Scenario: Authorization is absent or mismatched

- **WHEN** replacement evidence is missing, authorization is absent, or the authorization path does not exactly match the proposed source path
- **THEN** the deletion operation SHALL be rejected and SHALL NOT mutate the iCloud source.

#### Scenario: Bulk or unbounded deletion is requested

- **WHEN** a request targets all worktrees, a directory glob, an unbounded set, or any path set without one exact authorized source path per operation
- **THEN** the request SHALL be rejected before mutation and SHALL report that bulk deletion is unsupported.
