# refresh-gitnexus-index-groups Specification

## Purpose

TBD: Define the purpose of refresh-gitnexus-index-groups.

## Requirements

### Requirement: Authorized bounded index maintenance

An index refresh SHALL run only for an exact repository set with contemporaneous approval, a pinned provider identity, bounded arguments, and recorded preflight revisions.

#### Scenario: Approval is absent or scope differs

- **WHEN** approval is absent, stale, or does not name the exact repository set and action
- **THEN** no refresh SHALL run
- **AND** read-only status inspection MAY record the blocker.

#### Scenario: Postflight is current

- **WHEN** an authorized refresh completes
- **THEN** postflight evidence SHALL prove indexed revision equality with the intended repository HEAD
- **AND** consumers SHALL remain unavailable for any target that fails the predicate.

### Requirement: Separately governed group synchronization

Group synchronization SHALL require a separate approval naming the provider destination, membership delta, data class, and rollback.

#### Scenario: Group mutation is not explicitly approved

- **WHEN** only inspection or index refresh is approved
- **THEN** group state SHALL remain unchanged.
