# Stage Toolset Composition Specification

## Purpose

Define typed, explicit, least-privilege toolset and capability composition for harness stages.
## Requirements
### Requirement: Official stage toolset composition

Harness stages SHALL receive public Pydantic AI toolsets and capabilities through the converged `agent_core.sdk` composition API.

#### Scenario: Shared read-only toolset

- **WHEN** multiple stages require GitNexus, Graphify, or bounded file reads
- **THEN** the composition root SHALL reuse an official toolset adapter
- **AND** it SHALL apply stage visibility through supported filtering/preparation

#### Scenario: Stage-specific tool

- **WHEN** only the impact stage is authorized to call a blast-radius tool
- **THEN** only that stage's effective toolsets SHALL expose it

### Requirement: No parallel tool registry

`agent-harness` SHALL NOT introduce a second shared/module/stage `ToolRegistry` or duplicate tool-provider protocol.

#### Scenario: Tool resolution

- **WHEN** a stage agent is constructed
- **THEN** tool identity, schema, retries, approval metadata, and ownership SHALL come from the core adapter and public toolset contracts

### Requirement: Explicit agent dependencies

Stage agent construction SHALL require a resolved TDT gateway and immutable runtime profile.

#### Scenario: Missing gateway

- **WHEN** the gateway cannot be resolved
- **THEN** construction SHALL fail before a stage node runs
- **AND** the error SHALL identify the TDT gateway configuration boundary

### Requirement: Production service composition root

`agent-harness` SHALL construct an immutable consumer-owned service composition containing factory-owned Jira read access, bounded code-intelligence providers, bounded file access, gateway/stage-agent factories, and artifact storage. Live services SHALL be reconstructed per runner process and SHALL NOT be checkpoint values.

#### Scenario: Production runner is constructed

- **WHEN** run, stream, status, resume, history, or report operation requires production services
- **THEN** the runner SHALL resolve one immutable service composition before graph compilation or state inspection
- **AND** credentials SHALL come through TDT factories and centralized environment loading

#### Scenario: Runner process restarts

- **WHEN** a durable run is opened in a separate process
- **THEN** the process SHALL reconstruct gateways, Jira clients, code-intelligence transports, and artifact-store handles from configuration
- **AND** checkpoint deserialization SHALL not load a live client or transport object

#### Scenario: Required service is missing

- **WHEN** a stage requires Jira, code intelligence, a gateway, or artifact storage that cannot be resolved
- **THEN** composition or stage execution SHALL fail closed with `needs_input` or an actionable configuration error
- **AND** an empty placeholder result SHALL not satisfy the dependency

### Requirement: Read-only code-intelligence adapters

GitNexus and Graphify production adapters SHALL expose bounded read-only operations, preserve source freshness and canonical repository identity in evidence, and SHALL NOT grant general shell or code-execution authority. GitNexus requests SHALL be validated against operation-specific bounds before transport, and typed unavailable, stale, ambiguous, out-of-bounds, and truncated results SHALL remain distinguishable to the caller.

#### Scenario: GitNexus query succeeds

- **WHEN** a stage requests an authorized GitNexus query, context, impact, or status operation through the ratified provider contract
- **THEN** the preferred read-only adapter SHALL return validated non-placeholder data and indexed source identity
- **AND** mutation operations such as analyze, rename, delete, or clean SHALL remain unavailable

#### Scenario: Production GitNexus transport is resolved

- **WHEN** production services compose a stage that requires GitNexus evidence
- **THEN** the composition SHALL resolve the reviewed `tdt.gitnexus-cli.v1` transport and verify its provider, schema, repository, source revision, and index identity before graph execution
- **AND** a test-only injected transport or `None` transport SHALL not satisfy production readiness

#### Scenario: GitNexus request exceeds bounds

- **WHEN** query limit, context limit, impact depth, impact limit, confidence, repository root, or another operation-defining field is invalid or outside the ratified bounds
- **THEN** the adapter SHALL reject the request before provider execution
- **AND** direct method invocation SHALL not bypass the validated request model

#### Scenario: GitNexus returns a typed failure

- **WHEN** the ratified provider reports unavailable, stale index, ambiguous identity, out-of-bounds, truncated, or another typed non-success status
- **THEN** the adapter SHALL preserve that status and safe diagnostic category
- **AND** it SHALL not collapse the result into an unrelated malformed-identity error

#### Scenario: Symbol discovery is ambiguous

- **WHEN** a ticket identifier or other broad query resolves zero or multiple candidate definitions
- **THEN** the stage SHALL request explicit symbol/repository evidence or report `needs_input`
- **AND** it SHALL not select a candidate or synthesize current code intelligence

#### Scenario: GitNexus transport is unavailable

- **WHEN** no approved read-only transport can execute the requested operation
- **THEN** the evidence stage SHALL report unavailable or `needs_input`
- **AND** it SHALL not synthesize empty processes, references, or impact maps with current freshness

#### Scenario: Graphify output is consumed

- **WHEN** Graphify evidence is available from an approved bounded local artifact
- **THEN** the adapter SHALL validate path, repository, graph identity, freshness, schema, and result bounds before returning evidence
- **AND** it SHALL reject missing or malformed output rather than returning an empty successful result

