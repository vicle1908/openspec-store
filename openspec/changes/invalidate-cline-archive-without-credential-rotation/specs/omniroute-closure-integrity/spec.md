## ADDED Requirements

### Requirement: Credential disclosure SHALL invalidate only the affected live sentinel claim

When a live sentinel is executed through a credential-carrying configuration file whose credential was exposed in a session transcript, the sentinel claim SHALL be void until the owner records upstream rotation or explicit accepted-risk authorization. This invalidation SHALL be surgical: cleanup mutations, static route-contract checks, and isolated negative-control evidence SHALL remain valid unless their own evidence is independently defective.

#### Scenario: surgical invalidation preserves unrelated evidence

- **WHEN** a credential disclosure voids a positive live-sentinel claim
- **THEN** the change SHALL preserve cleanup, static, and negative-control evidence that does not depend on the disclosed credential
- **AND** it SHALL reopen only the credential-release and positive live-sentinel gate
- **AND** the archived bytes SHALL remain unchanged

#### Scenario: fresh positive sentinel is blocked until owner release

- **WHEN** the disclosed credential has not been rotated and no accepted-risk release exists
- **THEN** no new positive live sentinel through the affected configuration SHALL be treated as authorized
- **AND** the surface SHALL remain config-level verified only
