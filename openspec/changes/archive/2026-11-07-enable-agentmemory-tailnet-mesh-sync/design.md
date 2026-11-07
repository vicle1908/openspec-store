# Design

## Context

See `proposal.md` — Why. Both workstations (`iosteam-mac-mini` at `100.70.16.83` and `macbook-pro-m5` at `100.101.64.56`) run local AgentMemory instances backed by the iii micro-engine (`agentmemory-3111`, composed of `http` on port `3111`, `state` on port `49134`, and the `@agentmemory/agentmemory` worker executing `dist/index.mjs`).

Analysis of `@agentmemory/agentmemory/dist/cli.mjs` and `index.mjs` identified the exact mechanics:
1. **Worker Compose Generation**: `writeWorkerCompose()` in `cli.mjs` dynamically regenerates `~/Library/Application Support/agentmemory/compose/worker-compose.yaml` and `.agentmemory-filtered.env` every time `agentmemory` starts. It filters `~/.agentmemory/.env` and injects variables from `AGENTMEMORY_WORKER_ENV_ALLOWLIST` (which includes `AGENTMEMORY_SECRET`). Hand-editing `worker-compose.yaml` is transient; `~/.agentmemory/.env` is the authoritative source.
2. **`meshAuthToken` Binding**: `registerMeshFunction(sdk, kv, explicitSecret() || void 0)` binds `meshAuthToken` at worker startup. `explicitSecret()` reads `process.env.AGENTMEMORY_SECRET` or parses `AGENTMEMORY_ENV_FILE` (pointing to `.agentmemory-filtered.env`). If both lack the key, `meshAuthToken` is `undefined`, causing `mem::mesh-sync` to fail with `"mesh sync requires AGENTMEMORY_SECRET"`.
3. **Anti-SSRF Address Validation (`isAllowedUrl`)**: Outbound push (`${peer.url}/agentmemory/mesh/receive`) and pull (`${peer.url}/agentmemory/mesh/export`) pass through `isAllowedUrl()`. If given a hostname, `isAllowedUrl()` performs DNS lookup and rejects the URL if *any* returned address is private. Because MagicDNS resolves both IPv4 (`100.x`) and IPv6 (`fd7a:...`), and `isPrivateIP()` flags `fd` prefixes as private, MagicDNS hostnames are rejected. Literal IPv4 addresses (`100.64.0.0/10`) pass cleanly.
4. **Network Ingress**: Engine listeners bind strictly to `127.0.0.1:3111` for local process security. Remote peers over Tailscale receive connection refused unless an L4 TCP forwarder is configured.
5. **LaunchAgent Supervisor**: `com.agentmemory.server.plist` must invoke `cli.mjs` with no subcommand (`main()`), as passing `start` triggers `unknownCommand` and immediate exit code 1.

## Goals / Non-Goals

**Goals:**
- Enable seamless, zero-token bidirectional memory synchronization between `iosteam-mac-mini` and `macbook-pro-m5` over Tailscale.
- Establish `~/.agentmemory/.env` as the authoritative source for `AGENTMEMORY_SECRET` so worker compose generation succeeds idempotently.
- Fix `com.agentmemory.server.plist` to eliminate supervisor crash-loops.
- Configure Tailscale Serve L4 TCP port `3111` on both nodes without exposing ports to the physical LAN.
- Register mesh peers using literal Tailscale IPv4 addresses to pass anti-SSRF validation.
- Provide verification commands via the MCP Router `memory_mesh_sync` tool.

**Non-Goals:**
- Cloud relaying or third-party hosted memory brokers; all sync is direct peer-to-peer over Tailnet WireGuard.
- Syncing heavy raw binary artifacts (screenshots, audio, large raw session transcripts); mesh scopes sync only structured concepts, decisions, actions, relationship graphs, and consolidated crystals.
- Multi-tenant RBAC or complex conflict-resolution UIs (the engine uses deterministic Last-Write-Wins with keyed locks).

## Decisions

### 1. Authoritative Configuration in `~/.agentmemory/.env` Over Direct Compose Edits
- **Decision**: Configure `AGENTMEMORY_SECRET` solely in `0600`-protected `~/.agentmemory/.env` and `~/.agentmemory/secret` (plus `mcprouter.db`), never in `0644` LaunchAgent plist files.
- **Rationale**:
  - `cli.mjs` overwrites `worker-compose.yaml` and `.agentmemory-filtered.env` on every startup:
    ```javascript
    writeFileSync(filteredPath, `${readFileSync(options.envFile, "utf8").split(/\r?\n/).filter(...).join("\n")}`);
    ```
  - Direct modifications to `worker-compose.yaml` are wiped when `agentmemory` boots. Setting `AGENTMEMORY_SECRET` in `~/.agentmemory/.env` guarantees it is automatically copied into `.agentmemory-filtered.env` on every boot.

### 2. Tailscale Serve L4 TCP Port Forwarding (`:3111`) vs. HTTPS Reverse Proxy
- **Decision**: Configure Tailscale Serve raw L4 TCP forwarders (`tailscale serve --bg --tcp=3111 127.0.0.1:3111`) on both nodes.
- **Rationale**:
  - WireGuard encapsulates all Tailscale packets in ChaCha20-Poly1305 encryption. Adding an outer TLS reverse proxy layer creates certificate hostname mismatches when peers connect via literal Tailscale IP addresses.
  - Raw L4 TCP streams bytes directly to the AgentMemory HTTP listener without TLS handshake overhead and keeps the local daemon bound strictly to `127.0.0.1`.

### 3. Literal Tailscale CGNAT IPv4 Addressing vs. MagicDNS Hostnames
- **Decision**: Register peer URLs using literal Tailscale IPv4 addresses (`http://100.70.16.83:3111` and `http://100.101.64.56:3111`).
- **Rationale**:
  - `isPrivateIP()` in `@agentmemory/agentmemory/dist/index.mjs` allows `100.64.0.0/10` CGNAT addresses while blocking IPv6 `fd` prefixes.
  - MagicDNS dual-stack lookups return `fd7a:...` (ULA), causing `(await lookup(host, { all: true })).some((r) => isPrivateIP(r.address))` to return `true` and reject the connection. Literal IPv4 bypasses DNS lookup entirely.

### 4. LaunchAgent Invocation Alignment
- **Decision**: Remove argument `start` from `com.agentmemory.server.plist` while keeping `EnvironmentVariables` free of plaintext secrets.
- **Rationale**:
  - `cli.mjs` dispatches `commands[args[0]] ?? main`. Because `start` is unmapped, it exits with error code 1.
  - Omitting the subcommand routes execution to `main()`, launching the Worker Compose stack cleanly.

### 5. Deterministic Last-Write-Wins (LWW) Synchronization & Pre-Sync Watermark
- **Decision**: Synchronize all standard shared scopes (`memories`, `actions`, `semantic`, `procedural`, `relations`, `graph:nodes`, `graph:edges`) and record `syncStartedAt` *before* initiating `push` and `pull` HTTP requests.
- **Rationale**:
  - `lwwMergeList()` compares record timestamps (`updatedAt` or `createdAt`) under per-item locks (`withKeyedLock`).
  - Capturing `const syncStartedAt = new Date().toISOString()` before the transfer window and assigning `peer.lastSyncAt = syncStartedAt` upon completion prevents records created on the remote peer during a 1–5s transfer from falling behind `lastSyncAt` and being skipped on subsequent incremental syncs.

## Risks / Trade-offs

- **Remote Node Asleep or Offline**:
  - *Risk*: `macbook-pro-m5` may be asleep or disconnected when a sync is initiated.
  - *Mitigation*: `mem::mesh-sync` bounds HTTP calls with `AbortSignal.timeout(30000)` and catches connection failures per peer, reporting `errors: ["fetch failed: ..."]` while keeping local state and other peers intact.
- **Secret Rotation Across Nodes**:
  - *Risk*: Rotating `AGENTMEMORY_SECRET` on one node will immediately break sync with HTTP 401 until the peer updates.
  - *Mitigation*: Secret rotation procedure requires updating `~/.agentmemory/secret` and `~/.agentmemory/.env` on both machines before restarting daemons.
- **Tombstoneless Governance Deletions (`mem::governance-delete`)**:
  - *Risk*: `mem::governance-delete` performs a hard `kv.delete()` without storing a tombstone record. If a memory is deleted on only one node and a full or overlapping sync runs, LWW will re-import the deleted record from the peer.
  - *Mitigation*: Execute `DELETE /agentmemory/governance/memories` against both peers when permanently purging records.
