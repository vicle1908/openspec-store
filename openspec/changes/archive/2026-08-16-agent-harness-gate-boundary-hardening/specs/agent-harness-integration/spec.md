## MODIFIED Requirements

### Requirement: Authenticated gate decisions

Harness approval and rejection decisions SHALL bind a trusted authenticated subject and unique single-use nonce to the exact gate interrupt, artifact digest, run, repository, expiry, and policy version, and SHALL revalidate subject freshness, revocation, assurance, and policy generation at final resume. The default resolver SHALL fail-closed when no ratified adapter is configured. Caller-supplied identity text SHALL NOT serve as an authorization source.

#### Scenario: Authenticated gate approval

- **WHEN** a valid subject approves a pending gate after process restart
- **THEN** only the bound continuation SHALL execute
- **AND** the audit record SHALL identify the resolved subject and authentication provenance without credential values

#### Scenario: Spoofed or replayed decision

- **WHEN** a caller self-asserts identity or replays a decision for a different or terminal gate
- **THEN** the decision SHALL fail before graph continuation
- **AND** no successful gate event SHALL be recorded

#### Scenario: Default resolver denies authorization

- **GIVEN** no explicit resolver is provided to the workflow runner
- **WHEN** a gate resume is attempted
- **THEN** the authorization SHALL fail with `GateIdentityUnavailableError`
- **AND** any environment identity (e.g. `TDT_ACTOR_ID`) SHALL NOT be used for authorization

#### Scenario: Caller-supplied actor is display-only

- **GIVEN** an explicit resolver that returns a valid subject
- **WHEN** a gate resume includes `actor` text
- **THEN** the trusted decision SHALL use the resolver-returned subject ID
- **AND** the caller-supplied actor text SHALL appear only in display fields

#### Scenario: Separation of duties enforced

- **GIVEN** a valid authenticated subject that matches the gate initiator
- **WHEN** authorization is attempted
- **THEN** the authorization SHALL fail with `separation_of_duties_required`

#### Scenario: Expired gate fails before resolver call

- **GIVEN** a gate binding whose expiry is in the past
- **WHEN** authorization is attempted
- **THEN** the authorization SHALL fail with `gate_decision_expired`
- **AND** the resolver SHALL NOT be called
