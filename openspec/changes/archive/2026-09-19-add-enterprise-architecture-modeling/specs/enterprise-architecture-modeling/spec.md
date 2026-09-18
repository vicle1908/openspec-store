## Purpose

Define a governed TOGAF ADM-aligned architecture modeling practice using ArchiMate 3.2 viewpoints, PlantUML templates, canonical Open Exchange XML models, headless agent model operations, and repeatable CI validation without coupling the practice to a graphical model repository or mandatory desktop tooling.

## ADDED Requirements

### Requirement: ArchiMate baseline
The architecture modeling practice SHALL use ArchiMate 3.2 as its normative notation baseline and SHALL identify any future ArchiMate 4 work as a separately validated compatibility change.

#### Scenario: Baseline review
- **WHEN** an architecture template, model file, or governance rule is reviewed
- **THEN** it SHALL identify ArchiMate 3.2 as its target baseline
- **AND** it SHALL NOT claim ArchiMate 4 support without a separate validated change

### Requirement: Canonical model interchange
Architectural models intended for agent consumption or automation SHALL be stored as ArchiMate Open Exchange XML, and tooling SHALL preserve model content beyond an agent mutation operation as described in the preservation requirement.

#### Scenario: Model stored in exchange format
- **WHEN** an agent-accessible architecture model is inspected
- **THEN** it SHALL be a well-formed ArchiMate Open Exchange XML document compatible with the ArchiMate 3.2 exchange format
- **AND** it SHALL NOT depend on a proprietary repository format for automated reading

#### Scenario: Round-trip with desktop tooling
- **WHEN** a model file created or mutated by the agent tooling is opened in Archi or processed by ACLI
- **THEN** the model SHALL load without loss of elements, relationships, or folders attributable to the agent operation
- **AND** views and other content untouched by the operation SHALL remain present

### Requirement: Agent model inspection and query
The agent tooling SHALL provide read-only, side-effect-free operations for model metadata, filtered element queries, filtered relationship queries, neighborhood traversal, and view/organization listing without requiring a GUI.

#### Scenario: Read-only operations leave no trace
- **WHEN** any read or query operation executes against a model file
- **THEN** the file bytes, modification time, and working tree status SHALL be unchanged

#### Scenario: Filtered element query
- **WHEN** an agent queries elements by layer, type, name pattern, or property
- **THEN** the tooling SHALL return only matching elements with identifier, type, and name
- **AND** the result size SHALL be bounded and ordered deterministically

#### Scenario: Relationship neighborhood traversal
- **WHEN** an agent requests the neighbors of an element up to a stated depth
- **THEN** the tooling SHALL return the reachable subgraph of elements and relationships within that depth
- **AND** it SHALL state when the traversal is truncated by a limit

### Requirement: Agent model mutation
The agent tooling SHALL provide explicit mutation operations for creating, updating, and deleting elements and relationships, and every mutation SHALL be applied transactionally with validation before persistence.

#### Scenario: Create element
- **WHEN** an agent creates an element with a supported type, name, and layer
- **THEN** the tooling SHALL assign an identifier that is unique within the model and valid for the exchange format
- **AND** the persisted model SHALL remain schema-valid

#### Scenario: Create relationship with validation
- **WHEN** an agent creates a relationship between two existing elements
- **THEN** the tooling SHALL reject the operation when the relationship type is not legal for the element types or the direction is inverted per the ArchiMate 3.2 metamodel
- **AND** a rejected operation SHALL leave the model file unchanged

#### Scenario: Delete with references
- **WHEN** an agent deletes an element or relationship that is referenced by views or other relationships
- **THEN** the tooling SHALL either remove the dependent references within the same transaction or reject the delete
- **AND** the persisted model SHALL NOT contain dangling references

#### Scenario: Batch mutation atomicity
- **WHEN** an agent submits a batch of mutations and any single operation fails validation
- **THEN** no operation from the batch SHALL be persisted
- **AND** the model file SHALL remain byte-identical to its pre-batch state

### Requirement: Model validation
The agent tooling SHALL validate models in two tiers — structural schema validation against the ArchiMate Open Exchange format and semantic validation of relationship legality and directionality — and SHALL report violations with element, relationship, and rule identifiers.

#### Scenario: Structural validation failure
- **WHEN** a model file fails Open Exchange schema validation, including IDREF resolution
- **THEN** the validation result SHALL fail closed, identify the offending construct, and prevent persistence of the invalid state

#### Scenario: Semantic validation failure
- **WHEN** a relationship connects element types or in a direction that the ArchiMate 3.2 metamodel does not permit
- **THEN** the semantic validation SHALL reject it with a rule identifier and both endpoint identifiers
- **AND** the model SHALL NOT be persisted in that state

### Requirement: Deterministic identity and preservation
Mutations SHALL preserve existing identifiers of unmodified objects, allocate deterministic identifiers for new objects, and preserve unknown or unmodified XML content, including views, organizations, namespaces, and vendor extensions, where feasible.

#### Scenario: Idempotent re-application
- **WHEN** the same logical mutation is applied twice by re-running an agent operation
- **THEN** the second application SHALL NOT create duplicate elements or relationships
- **AND** identifiers SHALL remain stable across the re-application

#### Scenario: Unmodified content preserved
- **WHEN** a mutation touches one element
- **THEN** views, bendpoints, folder memberships, documentation, properties, and extensions not implicated by the operation SHALL survive the persisted write
- **AND** serialization differences SHALL be limited to the mutation and deterministic formatting

#### Scenario: Preservation failure fails closed
- **WHEN** the tooling cannot represent or safely preserve existing model content during a mutation
- **THEN** it SHALL refuse the mutation rather than silently discard content

### Requirement: Safe persistence
Model writes SHALL be performed atomically under a single-writer boundary with a pre-mutation backup and rollback on failure; a crash or rejected operation SHALL NOT leave a partially written or corrupt model file.

#### Scenario: Atomic write
- **WHEN** a validated mutation is persisted
- **THEN** the file SHALL be replaced via a temporary sibling file and atomic rename
- **AND** an interrupted write SHALL leave the previous model file intact

#### Scenario: Rollback on validation failure
- **WHEN** persistence-time validation fails after changes are staged
- **THEN** the tooling SHALL restore the last known-good state
- **AND** the repository SHALL show no model modification for the failed operation

### Requirement: TOGAF ADM template coverage
The template library SHALL provide at least one PlantUML template for Preliminary, Phases A–H, and Requirements Management.

#### Scenario: All ADM areas present
- **WHEN** `docs/architecture/diagrams/` is inspected
- **THEN** it SHALL contain `preliminary`, `phase-a` through `phase-h`, and `requirements-management`
- **AND** every directory SHALL contain at least one `.puml` file

#### Scenario: Template standard-library usage
- **WHEN** a template is inspected
- **THEN** it SHALL include the supported ArchiMate PlantUML standard library
- **AND** it SHALL express the intended ADM viewpoint concern

### Requirement: PlantUML syntax gate
CI SHALL validate every changed `.puml` file with PlantUML's `-checkonly` mode and SHALL fail when any changed file has invalid syntax.

#### Scenario: Valid pull request
- **WHEN** a pull request changes valid `.puml` files
- **THEN** the CI validation SHALL complete successfully without rendering diagrams

#### Scenario: Invalid pull request
- **WHEN** a changed `.puml` file has syntax errors
- **THEN** the CI validation SHALL fail and identify the invalid file

### Requirement: Model file gate
CI SHALL validate every changed ArchiMate Open Exchange XML model file with the two-tier validation and SHALL fail on any structural or semantic violation.

#### Scenario: Changed model file in pull request
- **WHEN** a pull request changes an exchange XML model file
- **THEN** CI SHALL run structural and semantic validation before merge
- **AND** a violation SHALL fail the pull request with a rule and construct identifier

#### Scenario: Agent mutation regression
- **WHEN** an agent mutation sequence is replayed against the repository model fixtures
- **THEN** the resulting models SHALL remain valid and preserve unmodified content
- **AND** unexpected identifier churn SHALL fail the gate

### Requirement: Toolchain verification
The repository SHALL provide a verification procedure for PlantUML, Graphviz, ArchiMate standard-library availability, and the model validation workflow before relying on local rendering or validation.

#### Scenario: Required tools available
- **WHEN** the verification procedure runs with supported tools installed
- **THEN** PlantUML and Graphviz version checks SHALL succeed
- **AND** an ArchiMate standard-library include smoke test SHALL succeed
- **AND** the model validation workflow SHALL pass against the canonical fixture

#### Scenario: Optional desktop tool absent
- **WHEN** Archi/ACLI is not installed
- **THEN** the core template, validation, and agent model workflows SHALL remain fully defined and executable
- **AND** the procedure SHALL report Archi/ACLI as optional rather than failing the core gate

### Requirement: Agent interface governance
The agent capability boundary SHALL be exposed through an optional CLI or MCP adapter whose mutation surface accepts structured operations only, SHALL be documented with authorization limits, and SHALL NOT require a GUI or desktop modeler for automated workflows.

#### Scenario: Structured mutation interface
- **WHEN** an agent invokes a mutation through the CLI or MCP adapter
- **THEN** the operation SHALL be expressed as a structured element or relationship operation, not as raw model file text
- **AND** unsupported or malformed operations SHALL be rejected without file changes

#### Scenario: Adapter optional
- **WHEN** the MCP adapter or a specific CLI distribution is unavailable
- **THEN** the governed model files and CI gates SHALL remain usable
- **AND** no workflow SHALL hard-require a running desktop application or display server

### Requirement: OpenSpec governance mapping
The architecture documentation SHALL map proposal, design, specs, and tasks to relevant TOGAF ADM governance activities and SHALL state that OpenSpec is change governance, not an enterprise-architecture repository.

#### Scenario: Complete mapping
- **WHEN** the governance mapping is reviewed
- **THEN** it SHALL cover all four OpenSpec artifacts
- **AND** it SHALL identify applicable vision, architecture-definition, migration/implementation, and change-management activities
- **AND** it SHALL name Architecture Practice ownership for model review
