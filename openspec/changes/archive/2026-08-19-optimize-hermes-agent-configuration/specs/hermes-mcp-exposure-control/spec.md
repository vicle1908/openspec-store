## Purpose

Preserves the existing MCP Router setup while providing full-operation exposure and unrestricted parallel invocation to authorized sessions on the shared default profile.

## ADDED Requirements

### Requirement: Existing MCP Router setup SHALL remain unchanged

The change SHALL treat the existing `mcp-router` definition as an immutable baseline. It SHALL NOT modify the command, package reference, arguments, environment, credential references, filters, protocol feature settings, timeout policy, or reload behavior. The only permitted MCP-server-key change is `supports_parallel_tool_calls=true`.

#### Scenario: Existing server is inventoried
- **WHEN** apply records the redacted MCP Router structure before default-profile configuration mutation
- **THEN** it captures non-secret key presence, command, arguments, and a redacted structural fingerprint without invoking or reconfiguring the server

#### Scenario: Apply completes
- **WHEN** the optimized default profile is validated
- **THEN** the MCP Router structural fingerprint matches the baseline except for the explicit `supports_parallel_tool_calls=true` addition

#### Scenario: MCP Router drift is detected
- **WHEN** any other MCP Router field differs from the baseline
- **THEN** activation is blocked and the last known-good setup is preserved without automatic repair, package probing, reload, or pinning

### Requirement: Verified MCP servers SHALL expose all advertised operations

The existing MCP Router exposure policy SHALL be preserved without adding or changing include/exclude, resource, prompt, sampling, or elicitation settings. Every tool currently registered through that setup SHALL remain available to authorized default-profile sessions.

#### Scenario: Gateway starts with full MCP exposure
- **WHEN** the default-profile Telegram gateway starts with a verified enabled MCP server
- **THEN** every advertised MCP tool and supported resource/prompt utility is registered in that session

#### Scenario: MCP capability is not negotiated

- **WHEN** initialization does not advertise tools, prompts, resources, sampling, or elicitation support for a corresponding operation
- **THEN** Hermes SHALL not claim or synthesize that operation
- **AND** the diagnostic SHALL distinguish unsupported capability from profile filtering or transport failure

#### Scenario: Mutating action is requested
- **WHEN** an authorized session requests an advertised MCP action that can create, edit, delete, publish, deploy, message, change permissions, or manage credentials
- **THEN** Hermes sends the call to the MCP server, subject to the server's credentials, scopes, availability, and any immutable Hermes safety floor

### Requirement: MCP utility operations SHALL remain exposed

Resource and prompt utility wrappers SHALL remain enabled when an MCP server advertises them, because full operation access includes the server's complete supported interface.

#### Scenario: Server advertises utilities
- **WHEN** an enabled MCP server advertises resource or prompt operations
- **THEN** the corresponding utility wrappers are included in the default profile's tool schema

#### Scenario: Server advertises no utilities
- **WHEN** an enabled MCP server does not advertise resource or prompt operations
- **THEN** Hermes exposes the complete available server interface without synthesizing unavailable wrappers

### Requirement: MCP tool calls SHALL permit parallel dispatch

Hermes SHALL set `mcp_servers.mcp-router.supports_parallel_tool_calls=true` and SHALL retain `agent.parallel_tool_call_guidance=true`. It SHALL not impose an MCP-specific serialization policy when the model emits independent calls in one turn.

The default profile SHALL impose no tool-call quota, operation-class denylist, per-server call filter, or MCP-specific call-count restriction. Tool Search discovery-result limits SHALL not be interpreted as limits on subsequent `tool_describe` or `tool_call` operations.

#### Scenario: Independent MCP calls are emitted together
- **WHEN** an authorized model turn emits two or more MCP Router tool calls
- **THEN** Hermes may dispatch them concurrently and associates each result with its originating call

#### Scenario: Built-in or plugin calls are independent
- **WHEN** a model emits independent non-MCP tool calls in the same turn
- **THEN** Hermes retains its normal parallel dispatch behavior rather than serializing them by policy

#### Scenario: Parallel calls race over shared state
- **WHEN** concurrent operations target the same mutable external resource
- **THEN** Hermes reports each real result or failure without claiming serializability, deduplicating effects, or silently retrying a business mutation

#### Scenario: Tool Search discovery limit is reached
- **WHEN** a catalog query returns its configured maximum number of matches
- **THEN** the session may issue additional searches, descriptions, and calls; the discovery page size SHALL NOT deny or cap the underlying tool operations

### Requirement: MCP setup SHALL not be reloaded by this change

The apply workflow SHALL NOT add, remove, configure, test, reinstall, pin, or reload MCP Router. Fresh sessions MAY be used to observe the already registered surface and the parallel-call flag.

#### Scenario: Validation needs a clean schema boundary
- **WHEN** the operator validates tool visibility after default-profile configuration
- **THEN** a fresh session is used without invoking `/reload-mcp` or changing the server definition

### Requirement: MCP availability SHALL be verifiable without mutation

The operator SHALL be able to verify server connectivity, enabled status, and registered runtime tool names using read-only diagnostics before permitting a profile to use the server. Evidence SHALL use the installed `mcp__<server>__<tool>` runtime naming form and SHALL distinguish native discovery from registered utility-wrapper verification.

#### Scenario: MCP verification passes
- **WHEN** the configured server connects and returns its expected advertised interface
- **THEN** the diagnostic records enabled status and the complete advertised tool inventory without executing any business action

#### Scenario: MCP verification fails
- **WHEN** the server times out, returns a mismatched tool inventory, or fails its security checks
- **THEN** the default profile remains on the last known-good MCP configuration and the failure is reported
