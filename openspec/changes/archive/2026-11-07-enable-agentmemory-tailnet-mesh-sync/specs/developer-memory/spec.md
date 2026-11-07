# Spec Delta: developer-memory

## ADDED Requirements

### Requirement: Cross-node Tailscale mesh synchronization and engine secret propagation

The AgentMemory engine stack (`agentmemory-3111`), LaunchAgent supervisor, and MCP bridge SHALL propagate the canonical `AGENTMEMORY_SECRET` to the worker container and MCP process environments, SHALL maintain supervisor stability without invalid CLI arguments, and SHALL execute authenticated, anti-SSRF-validated peer-to-peer mesh synchronization (`mem::mesh-sync`) across shared memory scopes over private tailnets.

#### Scenario: Worker container and MCP bridge inherit active AGENTMEMORY_SECRET
- **WHEN** the AgentMemory engine worker and MCP processes initialize
- **THEN** `explicitSecret()` SHALL resolve the canonical 64-character hex secret from `AGENTMEMORY_SECRET` in environment or `AGENTMEMORY_ENV_FILE` (derived from `~/.agentmemory/.env`)
- **AND** `registerMeshFunction` SHALL bind `meshAuthToken` with the resolved secret
- **AND** `mem::mesh-sync` tool calls through MCP Router or REST SHALL NOT fail with `mesh sync requires AGENTMEMORY_SECRET`

#### Scenario: LaunchAgent supervisor executes default daemon command without invalid arguments
- **WHEN** `launchctl kickstart -k gui/$(id -u)/com.agentmemory.server` is invoked
- **THEN** the supervisor SHALL execute `cli.mjs` without subcommands, routing execution to `main()`
- **AND** the daemon SHALL NOT exit with status 1 due to `Unknown command: start`
- **AND** the `0644` LaunchAgent plist SHALL NOT store plaintext `AGENTMEMORY_SECRET` in `EnvironmentVariables`

#### Scenario: Anti-SSRF validation permits Tailscale CGNAT IPv4 addresses and rejects RFC1918 and IPv6 ULA
- **WHEN** a mesh peer URL is submitted to `mem::mesh-register` or evaluated during sync
- **THEN** literal Tailscale IPv4 addresses (`100.64.0.0/10`) on configured port `3111` SHALL pass `isAllowedUrl()` and `isPrivateIP()` validation
- **AND** loopback (`127.0.0.1`, `localhost`), RFC1918 subnets (`192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`), and IPv6 addresses starting with `fd` SHALL be rejected with `URL blocked: private/local address not allowed`

#### Scenario: Bidirectional last-write-wins delta sync reconciles shared memory scopes
- **WHEN** `mem::mesh-sync` executes across authenticated peers (`iosteam-mac-mini` at `http://100.70.16.83:3111` and `macbook-pro-m5` at `http://100.101.64.56:3111`)
- **THEN** delta records modified since `peer.lastSyncAt` across shared scopes (`memories`, `actions`, `semantic`, `procedural`, `relations`, `graph:nodes`, `graph:edges`) SHALL be transferred via POST `/agentmemory/mesh/receive` and GET `/agentmemory/mesh/export`
- **AND** incoming records SHALL be merged using monotonic timestamps with keyed locks (`withKeyedLock`), returning metrics for pushed and pulled items
- **AND** `peer.lastSyncAt` SHALL be updated to the pre-transfer `syncStartedAt` ISO timestamp when zero errors occur, preventing records created during in-flight transfers from being skipped

#### Scenario: Unauthenticated or mismatched secret requests are rejected
- **WHEN** a request reaches `/agentmemory/mesh/*` without an `Authorization: Bearer <secret>` header matching `AGENTMEMORY_SECRET`
- **THEN** the request SHALL be rejected with HTTP `401 Unauthorized`
- **AND** zero unauthorized modifications SHALL be applied to the local memory store
