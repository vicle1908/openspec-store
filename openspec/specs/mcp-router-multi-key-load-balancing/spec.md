# mcp-router-multi-key-load-balancing Specification

## Purpose
Provides multi-API-key pooling, OS keychain encryption at rest, template-based URL/header/stdio credential injection, quota-aware load balancing with automatic failover, hot-reload transport reconciliation, workspace lifecycle isolation, and key/token management UI for MCP Router.

## Requirements

### Requirement: Multi-Key Pool Configuration and Injection Targets

The system SHALL allow each MCP server configuration to define an ordered pool of API keys and custom HTTP headers, supporting credential injection into HTTP URL path/query templates (`{{KEY}}` or `${KEY}`), `Authorization: Bearer` headers, named custom HTTP headers, local stdio environment variables, and local CLI arguments.

#### Scenario: Inject selected API key into remote HTTP URL query parameter
- **WHEN** a remote or remote-streamable MCP server is configured with URL-template injection, a remote URL containing `{{KEY}}` or `${KEY}`, and an active key secret
- **THEN** the router SHALL substitute the placeholder with the URL-encoded key secret before validating and connecting the transport
- **AND** it SHALL NOT send an empty `Authorization: ""` header when no bearer token is configured

#### Scenario: WHATWG URL path percent-encoding placeholder substitution
- **WHEN** a remote server URL template specifies placeholders in the pathname (e.g., `https://host/v1/{{KEY}}/mcp`) where WHATWG URL serialization percent-encodes braces to `%7B%7BKEY%7D%7D` or `${KEY}` to `%24%7BKEY%7D`
- **THEN** the router SHALL match and replace both literal `{{KEY}}`/`${KEY}` and percent-encoded `%7B%7BKEY%7D%7D`/`%24%7BKEY%7D` with `encodeURIComponent(secret)` before validating and connecting the transport

#### Scenario: Inject selected API key into custom HTTP header or Bearer header
- **WHEN** a remote MCP server is configured with custom-header injection (such as `X-API-Key`) or bearer-token injection
- **THEN** the router SHALL attach the selected key to the configured HTTP header on SSE and Streamable HTTP requests alongside any configured custom headers

#### Scenario: Inject selected API key into local stdio environment or arguments
- **WHEN** a local stdio MCP server is configured with environment-variable injection (such as `BRAVE_API_KEY`) or CLI-argument injection
- **THEN** the router SHALL spawn the child transport with the selected key injected into the designated environment variable or argument placeholder

### Requirement: Template-Safe Remote URL and Header Security Validation

The remote URL and header validator SHALL accept `{{KEY}}` and `${KEY}` placeholders only in URL path and query components at configuration save time while enforcing HTTPS protocol, non-empty hostname, DNS resolution, private/reserved IPv4 and IPv6 SSRF protections, and HTTP header control-character rejection.

#### Scenario: Valid HTTPS URL template with placeholder in query or path is accepted
- **WHEN** a server configuration is saved with `https://mcp.example.com/v1/mcp?api_key={{KEY}}`
- **THEN** save-time normalization SHALL validate the host and HTTPS scheme while preserving the unencoded `{{KEY}}` placeholder string

#### Scenario: Placeholder in scheme, userinfo, hostname, or port is rejected
- **WHEN** a server configuration is saved with `{{KEY}}` or `${KEY}` in the scheme, username, password, hostname, or port (such as `https://{{KEY}}.example.com/mcp` or `https://{{KEY}}@example.com/mcp`)
- **THEN** validation SHALL reject the URL with an explicit security error

#### Scenario: Private IP, localhost, or non-HTTPS URL template is rejected
- **WHEN** a server configuration is saved with `https://127.0.0.1/mcp?api_key={{KEY}}` or `http://mcp.example.com/mcp?api_key={{KEY}}`
- **THEN** validation SHALL reject the URL with an explicit security error

#### Scenario: Custom HTTP headers containing control characters are rejected
- **WHEN** a server is configured with custom HTTP headers containing control characters (`\r`, `\n`, NUL, or ASCII `<= 0x1f` / `0x7f`)
- **THEN** validation or transport initialization SHALL reject the malformed header

### Requirement: Key Encryption at Rest, Just-in-Time Decryption, and Log Redaction

The system SHALL encrypt all configured key-pool API keys, bearer tokens, sensitive custom headers, and sensitive server environment variables at rest using OS keychain encryption (`mcpr-secret:v1:` prefix), decrypt them just-in-time at transport creation, and redact secrets from logs and error messages.

#### Scenario: Key pool secrets and sensitive credentials are encrypted in persistent storage
- **WHEN** a server with multiple API keys, a bearer token, sensitive custom headers, or sensitive environment variables (matching `/(authorization|bearer|token|api[-_]?key|secret|password|passphrase|credential)/i`) is saved to local persistent storage
- **THEN** every stored secret value SHALL carry the encrypted `mcpr-secret:v1:` prefix when OS encryption is available

#### Scenario: Renderer IPC secret redaction and just-in-time decryption boundary
- **WHEN** server configurations are loaded for in-memory management or standard server listing over IPC
- **THEN** stored key-pool secrets SHALL remain encrypted (`mcpr-secret:v1:`) or masked, preventing plaintext secret broadcast across IPC to the renderer process
- **AND** the router SHALL decrypt secrets just-in-time inside the main process only when constructing an upstream transport or when explicitly requested for a single-key reveal action
#### Scenario: Just-in-time decryption and log/error secret redaction
- **WHEN** the router connects to or logs requests/errors for a local stdio or remote HTTP/SSE MCP server
- **THEN** it SHALL decrypt `mcpr-secret:v1:` values in memory immediately prior to constructing the transport
- **AND** it SHALL redact resolved URL query secrets, Bearer tokens, custom header secrets, and `mcpr-secret:v1:` strings from persisted request logs and server error messages without mutating in-flight request parameters

#### Scenario: Workspace serialization and server details view preserve and mask secrets
- **WHEN** workspace server configurations are serialized for local backup/rollback or rendered in read-only and edit UI views
- **THEN** key-pool configurations and custom headers SHALL be preserved without data loss, and secret values SHALL be masked by default in the UI until explicitly revealed by the operator

### Requirement: Quota-Aware Load Balancing and Transparent Failover

The system SHALL distribute MCP requests across enabled, non-cooling keys using the configured strategy (`round-robin`, `weighted-round-robin`, `tiered-fallback`, or `least-used`) and SHALL transparently fail over to the next healthy key when an upstream server reports a rate-limit or quota error.

#### Scenario: Transparent failover on HTTP 429 transport error
- **WHEN** a tool call, resource read, or prompt fetch fails with HTTP `429` (or `401`/`402`/`403` quota rejection) on Key A
- **THEN** the router SHALL mark Key A as `cooling_down` for the `Retry-After` duration or configured cooldown seconds
- **AND** it SHALL immediately retry the request using the next healthy key B in the pool without returning an error to the MCP client

#### Scenario: Transparent failover on MCP CallToolResult payload quota error
- **WHEN** a `tools/call` invocation returns a tool result with `isError: true` or a structured JSON payload whose top-level `status === 429` or `error.status === 429` / `error.code === 429`
- **THEN** the router SHALL classify the result as a quota failure on the active key, transition that key to `cooling_down`, and re-execute the tool call on the next healthy key

#### Scenario: False-positive quota defense on tool search outputs
- **WHEN** a tool call completes with `isError: false` or omitted, and the tool returns prose text containing `"HTTP 429 Too Many Requests"` or rate-limit terms (such as search or documentation content)
- **THEN** the router SHALL NOT classify the result as a quota error and SHALL NOT trigger key cooldown
#### Scenario: All keys in pool exhausted
- **WHEN** every enabled key in the server's key pool is in `cooling_down`, `quota_exhausted`, or `invalid` state after maximum retry attempts
- **THEN** the router SHALL return the last upstream quota error to the caller and record the failure metric against the server

#### Scenario: Client-side RPM and quota window enforcement
- **WHEN** a key reaches its configured per-minute or quota limit within the active window (`per-minute`, `daily`, or `monthly`)
- **THEN** the selector SHALL skip that key until the window resets or an operator manually resets key usage

### Requirement: Hot-Reload Transport Reconciliation and Workspace Lifecycle Isolation

The system SHALL automatically reconcile and reconnect active client transports when a running MCP server's connection or key-pool configuration is updated, and SHALL tear down active key-pool timers and secondary transports when switching workspaces.

#### Scenario: Updating keys or URL on a running server takes effect immediately
- **WHEN** an operator updates the key pool configuration, remote URL, bearer token, custom headers, environment variables, or CLI arguments on a server whose status is `"running"`
- **THEN** the server manager SHALL close invalidated client transport slots and establish updated transport connections without requiring a manual server stop and start

#### Scenario: Hot-reload reconnection failure transitions server to error state
- **WHEN** an operator updates the configuration of a running server and reconnection fails
- **THEN** the server manager SHALL transition the server status to `"error"`, record the error message, and emit a server-updated notification rather than leaving a `"running"` server with zero active client slots
#### Scenario: Switching workspaces clears key pool timers and secondary client slots
- **WHEN** the active workspace is switched or all servers are cleared
- **THEN** the router SHALL cancel all pending key cooldown timers, clear in-memory key metrics, and close open multi-key client transports from the previous workspace

### Requirement: Server Key Pool UI and Downstream Client Token Management UI

The desktop UI SHALL provide a per-server `Keys & Quota` configuration tab, unlock remote URL and custom header editing, mask secret inputs by default, display key-pool health badges on server cards, and expose downstream client token listing, generation, rotation, and revocation across all platform API layers.

#### Scenario: Operator manages server key pool in the advanced configuration sheet
- **WHEN** an operator opens the `Keys & Quota` tab for a server in the advanced server configuration sheet
- **THEN** the UI SHALL allow enabling the key pool, selecting the injection target and load-balancing strategy, adding/removing/masking API keys, viewing per-key usage and cooldown state, and manually resetting cooldown or usage counters

#### Scenario: Operator edits remote URL and imports remote server JSON
- **WHEN** an operator edits a remote server or imports a JSON configuration containing a remote `url` field
- **THEN** the UI SHALL allow modifying the remote URL and custom HTTP headers and SHALL accept valid remote server JSON definitions

#### Scenario: Operator lists, rotates, or revokes downstream client MCPR tokens
- **WHEN** an operator manages client tokens in the client application access manager
- **THEN** the desktop platform API SHALL list tokens, generate or rotate client tokens (`mcpr_` prefix) with optional non-expiring (`expiresAt` omitted) or custom TTL settings while preserving existing server access permissions by default, and revoke tokens while keeping existing legacy tokens valid until explicitly revoked

### Requirement: Deployed macOS application bundle and monorepo metadata parity

The running `/Applications/MCP Router.app` bundle serving `127.0.0.1:3282` SHALL be built and deployed from the local `/Users/androidteam/Developer/platform/mcp-router` `v0.6.4` source tree (including multi-key pool load balancing, `safeStorage` encryption, and per-request stateless MCP HTTP transport), and the root `package.json` `packageManager` field SHALL match the active workstation `pnpm` major/minor track.

#### Scenario: Installed /Applications/MCP Router.app matches repo v0.6.4 build
- **WHEN** `/Applications/MCP Router.app/Contents/Info.plist` is inspected via `defaults read "/Applications/MCP Router.app/Contents/Info" CFBundleShortVersionString`
- **THEN** the reported bundle version SHALL equal `0.6.4` (matching `platform/mcp-router/apps/electron/package.json`)
- **AND** the active Electron process listening on `127.0.0.1:3282` SHALL serve the `0.6.4` multi-key pool and `mcp:reveal-key-secret` IPC handlers

#### Scenario: Monorepo packageManager field matches active pnpm toolchain
- **WHEN** `/Users/androidteam/Developer/platform/mcp-router/package.json` and `pnpm-workspace.yaml` are inspected
- **THEN** `"packageManager"` in `package.json` SHALL equal `"pnpm@12.14.0"` and `pnpm-workspace.yaml` SHALL define `overrides`, `onlyBuiltDependencies`, `nodeLinker: hoisted`, and `shamefullyHoist: true`

#### Scenario: Stateless HTTP aggregator handles consecutive POST /mcp requests
- **WHEN** downstream MCP clients send multiple consecutive JSON-RPC `POST /mcp` requests to `127.0.0.1:3282`
- **THEN** `MCPHttpServer` and `AggregatorServer` SHALL instantiate and clean up a fresh `Server` and stateless `StreamableHTTPServerTransport` per request without throwing stateless transport reuse errors

#### Scenario: All workstation coding agent MCP surfaces authenticate with mode 0600 and full active server access
- **WHEN** the 21 workstation coding agent MCP configurations (`omp`, `pi`, `claude-code`, `cursor`, `codex`, `hermes`, `opencode`, `zed`, `qwen`, `copilot`, `kimi`, `kimi-code`, `gemini-mcp`, `antigravity`, `goose`, `droid`, `kiro`, `qoder`, `grok`, `cline`, `vscode`) and `~/Library/Application Support/MCP Router/shared-config.json` are evaluated against `http://127.0.0.1:3282/mcp`
- **THEN** every credential-bearing agent MCP configuration file SHALL have permission mode `0600`
- **AND** every client token in `shared-config.json` SHALL grant access to all `14/14` active upstream MCP servers (`170` tools) and return HTTP `200` on `POST http://127.0.0.1:3282/mcp` `tools/list`
