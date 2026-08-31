## Purpose

Define requirements for verifiable, immutable release decision evidence and tag verification.

# Delta: ntu-keynote-release-integrity

## Requirements

### Requirement: Release decisions SHALL cite verifiable evidence for every accepted gate

A central release decision SHALL NOT mark any gate `accepted` unless it cites, for that gate, an immutable or hash-verifiable evidence record that exists at decision time. A gate whose own recorded state is `blocked`, `pending`, or `not-submitted` anywhere in the change's acceptance artifacts SHALL NOT be reported as accepted in the decision. A decision that contradicts its own acceptance records is defective and SHALL be superseded by an invalidity record in a subsequent active change; the archived artifacts remain byte-identical.

#### Scenario: Blocked gate cannot be accepted

- **WHEN** an acceptance artifact records a gate as blocked or not-submitted
- **THEN** the release decision SHALL record that gate as blocked
- **AND** a decision marking it accepted SHALL be recorded as defective with a file and line citation

#### Scenario: Evidence citation is required

- **WHEN** a release decision marks a gate accepted
- **THEN** the decision SHALL name the evidence record (path and, where applicable, hash) that supports it
- **AND** an accepted gate with no citable record SHALL be recorded as defective

### Requirement: Tag and ref claims SHALL be re-verified against the live repository at decision time

A release decision that claims a fixed ref (for example an annotated tag `refs/tags/ntu-ai-keynote-v1.0.0`) is verified SHALL be produced only after a read-only check of the live external repository confirms the ref exists, resolves to the claimed object type, and peels to a commit containing the exact accepted package digest. A decision recording `verified` for a ref that does not exist is defective and SHALL be superseded by an invalidity record.

#### Scenario: Missing ref cannot be verified

- **WHEN** the named ref does not resolve in the live repository
- **THEN** the release decision SHALL record the ref as not-created and the release gate as blocked
- **AND** a decision claiming the ref verified SHALL be recorded as defective with the verification command and its failure captured value-blind

#### Scenario: Ref verification is recorded with its method

- **WHEN** a release decision verifies a ref
- **THEN** it SHALL record the verification method (command or equivalent), timestamp, and the resolved object identity
- **AND** any later consumer SHALL be able to repeat the check read-only and obtain the same result
