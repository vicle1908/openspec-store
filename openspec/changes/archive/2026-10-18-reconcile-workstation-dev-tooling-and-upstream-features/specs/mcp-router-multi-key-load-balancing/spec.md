# mcp-router-multi-key-load-balancing Specification Delta

## MODIFIED Requirements

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
