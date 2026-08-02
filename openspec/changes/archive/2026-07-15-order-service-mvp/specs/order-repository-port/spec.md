## ADDED Requirements

### Requirement: Repository is Order-specific
The persistence port SHALL expose Order use cases rather than generic CRUD or raw SQL transaction types.

#### Scenario: Persist aggregate
- **WHEN** the application saves an Order with expected version N
- **THEN** the repository updates the Order only if the stored version is N and persists version N+1

### Requirement: Unit of work owns atomic persistence
The application SHALL use a unit-of-work boundary that supplies repositories and outbox storage on one database transaction.

#### Scenario: Application error
- **WHEN** work inside the unit of work returns an error
- **THEN** all database changes made by that unit of work are rolled back

### Requirement: Database ownership is isolated
Only the Order Service database identity SHALL have write access to Order-owned tables, and repository interfaces SHALL remain private to the Order Service.

#### Scenario: Future service integration
- **WHEN** a Payment or Inventory service needs Order information
- **THEN** it uses a versioned API, event, or Temporal operation rather than querying Order tables or importing the repository package
