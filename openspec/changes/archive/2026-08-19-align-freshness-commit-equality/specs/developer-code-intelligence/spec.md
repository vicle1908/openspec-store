## MODIFIED Requirements

### Requirement: Non-destructive configuration and MCP verification

The integration SHALL preserve existing AgentMemory lifecycle hooks, hand-authored guidance, unrelated MCP servers, client credentials, and unrelated configuration. GitNexus and Graphify setup SHALL modify only their marked source-of-truth and router-owned entries. Verification SHALL cover the MCP Router endpoint or bridge, router server identity, child server identity, tool discovery, canonical repository routing, freshness, and representative read-only tool calls before setup is declared successful. Repository readiness for freshness SHALL reflect recorded index commit equality with repository HEAD, not timestamp recency alone. A repository whose recorded indexed revision does not equal the current HEAD SHALL NOT be reported as ready for freshness-dependent operations.

#### Scenario: Existing Agentmemory hooks are present

- **WHEN** Codex or Claude configuration already contains AgentMemory hooks
- **THEN** setup leaves those entries semantically unchanged and changes only the approved MCP routing entries

#### Scenario: GitNexus stable Codex setup is inspected

- **WHEN** the selected GitNexus `1.6.9` setup completes
- **THEN** exactly one router-owned GitNexus MCP boundary serves an isolated approved registry or validated filtered view and exposes only the approved repository set and operations
- **AND** no supported client starts another direct GitNexus MCP server

#### Scenario: GitNexus client operation allowlist is enforced

- **WHEN** an ordinary client requests GitNexus tools through MCP Router
- **THEN** only the reviewed read-only allowlist is exposed
- **AND** mutation, setup, group synchronization, and administrative tools are rejected at the boundary

#### Scenario: GitNexus registry contains an unapproved repository

- **WHEN** the native global registry contains a repository outside the approved exposure set
- **THEN** the router-owned boundary excludes it from repository discovery and rejects direct selection
- **AND** the native unrestricted registry is not exposed directly to clients

#### Scenario: MCP is live

- **WHEN** the developer starts an authorized client and queries the router-exposed GitNexus repository list plus Graphify statistics for each approved project
- **THEN** each server responds for the intended repository or project and reports source freshness
- **AND** freshness evidence SHALL not rely solely on recent refresh activity; recorded indexed revision equality with repository HEAD SHALL be the primary signal when recorded revision is available
- **AND** a repository whose recorded indexed revision does not equal HEAD SHALL be reported as stale for freshness
- **AND** the calls prove tool execution through MCP Router rather than only configuration presence

#### Scenario: Duplicate tool name would be ambiguous

- **WHEN** two enabled router child servers advertise the same unqualified Graphify tool name
- **THEN** readiness fails before client cutover
- **AND** the integration requires one multi-project Graphify server or an independently verified collision-safe namespace mechanism

#### Scenario: Repository metadata contains embedded credentials

- **WHEN** GitNexus repository metadata contains userinfo or credential-like material in a remote URL
- **THEN** MCP output and retained evidence redact the complete userinfo and credential value
- **AND** verification fails if an unredacted credential-bearing URL reaches a client-visible result

#### Scenario: Tool-owned integration is removed

- **WHEN** the documented targeted uninstall path runs
- **THEN** router-owned GitNexus/Graphify MCP entries, skills, guidance markers, and hooks in the approved scope are removed while AgentMemory hooks, unrelated router servers, client bridges, and hand-authored guidance remain
