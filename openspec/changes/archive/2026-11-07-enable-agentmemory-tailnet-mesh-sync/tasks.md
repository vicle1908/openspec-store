# Tasks

## 1. Secret Harmonization & LaunchAgent Alignment

- [x] 1.1 Verify canonical secret in `~/.agentmemory/secret` matches `AGENTMEMORY_SECRET` in `~/.agentmemory/.env` on both `iosteam-mac-mini` and `macbook-pro-m5`
- [x] 1.2 Update `~/Library/LaunchAgents/com.agentmemory.server.plist` to remove invalid `<string>start</string>` argument and ensure `0644` LaunchAgent plists on both hosts omit plaintext `AGENTMEMORY_SECRET`
- [x] 1.3 Ensure MCP Router `mcprouter.db` `servers` table stores `AGENTMEMORY_SECRET` under `env` for the `agentmemory` server

## 2. Tailscale Serve L4 TCP Forwarder Configuration

- [x] 2.1 Enforce `tailscale serve --bg --tcp=3111 127.0.0.1:3111` on `iosteam-mac-mini` (`100.70.16.83`) and verify via `tailscale serve status --json`
- [x] 2.2 Configure `tailscale serve --bg --tcp=3111 127.0.0.1:3111` on `macbook-pro-m5` (`100.101.64.56`) via Orca terminal or remote command and verify `:3111` listener
- [x] 2.3 Verify bi-directional L4 TCP reachability on port `3111` across the tailnet (`nc -zv 100.101.64.56 3111` and `nc -zv 100.70.16.83 3111`)

## 3. Daemon Restart & Ingress Probe Verification

- [x] 3.1 Restart AgentMemory via `agentmemory stop && launchctl kickstart -k gui/$(id -u)/com.agentmemory.server` on `iosteam-mac-mini` and `macbook-pro-m5`
- [x] 3.2 Verify `worker-compose.yaml` and `.agentmemory-filtered.env` are automatically regenerated with active `AGENTMEMORY_SECRET`
- [x] 3.3 Verify local `curl -fsS http://localhost:3111/agentmemory/livez` and remote `curl -fsS http://100.101.64.56:3111/agentmemory/livez` return HTTP `200`

## 4. Peer Registration & Bidirectional Mesh Synchronization

- [x] 4.1 Register `macbook-pro-m5` (`http://100.101.64.56:3111`, name `macbook-pro-m5`) as a mesh peer on `iosteam-mac-mini` using literal Tailscale IPv4
- [x] 4.2 Register `iosteam-mac-mini` (`http://100.70.16.83:3111`, name `iosteam-mac-mini`) as a mesh peer on `macbook-pro-m5`
- [x] 4.3 Patch `mem::mesh-sync` in `dist/index.mjs` on both hosts to capture `syncStartedAt` prior to network transfer, then trigger `memory_mesh_sync` and verify bidirectional push/pull record metrics with zero authentication errors

## 5. Specification Validation & Knowledge Base Sync

- [x] 5.1 Run `openspec validate enable-agentmemory-tailnet-mesh-sync --strict --store openspec-store` and verify zero validation issues
- [x] 5.2 Update `~/Developer/wiki/entities/agentmemory.md` and `~/Developer/wiki/entities/tailscale.md` with the 6-port Tailscale Serve topology and mesh replication contracts
