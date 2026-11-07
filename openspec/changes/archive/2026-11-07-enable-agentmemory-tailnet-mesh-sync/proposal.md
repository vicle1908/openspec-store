# Proposal

## Why

Developer workstations `iosteam-mac-mini` (`100.70.16.83`) and `macbook-pro-m5` (`100.101.64.56`) run concurrent AI coding agents (OMP, Claude Code, Codex, Pi, Hermes) coordinated via Orca and sharing unified OmniRoute inference and Layer-2 semantic cache partitions. However, their AgentMemory stores (memories, actions, architectural lessons, relationship graphs, and session observations) remain isolated on local loopback engines (`127.0.0.1:3111`), causing agent sessions on one machine to lack context and decisions established on the other. Enabling AgentMemory's native peer-to-peer mesh synchronization (`mem::mesh-sync`) over private Tailscale WireGuard tunnels unifies developer memory across both machines without cloud egress or token overhead.

## What Changes

- **Synchronize `AGENTMEMORY_SECRET` Across Runtime Configurations**:
  - Propagate the canonical 64-character hex secret from `~/.agentmemory/secret` into `~/.agentmemory/.env` (mode `0600`) and MCP Router (`servers.env` in `mcprouter.db`). This allows `cli.mjs` to dynamically generate `.agentmemory-filtered.env` (mode `0600`) with active `AGENTMEMORY_SECRET`, ensuring the worker container and `agentmemory-mcp` initialize `meshAuthToken` upon startup without exposing plaintext secrets in world-readable (`0644`) LaunchAgent plists.
- **Align LaunchAgent Supervisor Command Invocation**:
  - Update `~/Library/LaunchAgents/com.agentmemory.server.plist` to remove the unsupported `<string>start</string>` argument (which previously caused 56,000+ crash-loop exits with `Unknown command: start`) while keeping `EnvironmentVariables` free of plaintext secrets.
- **Expose AgentMemory REST Service via Tailscale Serve L4 TCP Forwarding**:
  - Register raw L4 TCP port forwarders (`tailscale serve --bg --tcp=3111 127.0.0.1:3111`) on both `iosteam-mac-mini` and `macbook-pro-m5`, allowing tailnet peers to communicate over authenticated ChaCha20-Poly1305 tunnels on `:3111` while keeping local engine daemons bound strictly to loopback (`127.0.0.1`).
- **Enforce Tailscale CGNAT IPv4 Peer Addressing for Anti-SSRF Compliance**:
  - Register mesh peer URLs using literal Tailscale IPv4 addresses on port `3111` (`http://100.70.16.83:3111` and `http://100.101.64.56:3111`) rather than MagicDNS hostnames, satisfying AgentMemory's `isPrivateIP()` URL validator, which accepts `100.64.0.0/10` CGNAT addresses while blocking RFC1918 private subnets and IPv6 `fd...` addresses.
- **Configure Bidirectional Last-Write-Wins (LWW) Mesh Peer Synchronization**:
  - Register cross-node peers via `mem::mesh-register` and configure bidirectional sync (`mem::mesh-sync`) across standard shared scopes (`memories`, `actions`, `semantic`, `procedural`, `relations`, `graph:nodes`, `graph:edges`), capturing `syncStartedAt` prior to network transfer so records created during in-flight transfers are never skipped.
- **Validate End-to-End Mesh Synchronization via MCP Tools**:
  - Verify that `mcp__mcp_router_memory_mesh_sync` executes successfully without authentication errors and reconciles memory records between the two machines.

## Capabilities

### Modified Capabilities
- `developer-memory`: Add requirements for cross-node Tailscale peer-to-peer mesh synchronization (`mem::mesh-sync`), LaunchAgent supervisor alignment without invalid subcommands, engine secret propagation via `~/.agentmemory/.env`, Bearer token enforcement on `/agentmemory/mesh/*`, anti-SSRF address validation on port 3111, and monotonic Last-Write-Wins conflict resolution.
- `workstation-tailscale-connectivity`: Extend Tailscale Serve forwarding requirements on `iosteam-mac-mini` and `macbook-pro-m5` to include raw L4 TCP port `3111` (`127.0.0.1:3111`) for AgentMemory mesh traffic alongside existing ports (`20128`, `20129`, `20132`, `443`, `8443`).

## Impact

- **Affected Daemons & Systems**:
  - AgentMemory iii engine compose stack (`agentmemory-3111`, `http` worker on port 3111, `state` worker).
  - LaunchAgent supervisor `com.agentmemory.server`.
  - MCP Router (`/Applications/MCP Router.app`, `:3282`) and child `@agentmemory/mcp` process.
  - Tailscale network extension (`io.tailscale.ipn.macsys.network-extension`) and `tailscaled` serve state.
- **Affected Files & Configuration**:
  - `~/Library/LaunchAgents/com.agentmemory.server.plist`
  - `~/.agentmemory/.env`
  - `~/Library/Application Support/MCP Router/mcprouter.db`
  - Dynamically generated: `~/Library/Application Support/agentmemory/compose/worker-compose.yaml` and `.agentmemory-filtered.env`
- **Security & Network Boundary**:
  - Mesh traffic is restricted to authenticated Tailnet nodes.
  - All mesh REST endpoints (`/agentmemory/mesh/*`) enforce HTTP Bearer token validation matching `AGENTMEMORY_SECRET`.
  - Zero cloud egress; all synchronization remains strictly peer-to-peer.
