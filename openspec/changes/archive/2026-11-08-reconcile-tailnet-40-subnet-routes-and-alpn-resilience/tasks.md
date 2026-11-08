# Tasks

## 1. Specification & Delta Spec Updates

- [x] 1.1 Create delta spec `specs/workstation-tailscale-connectivity/spec.md` with MODIFIED requirements codifying the 40 surgical `/32` routes and HTTP/1.1 ALPN enforcement with bounded handshake retry absorption
- [x] 1.2 Synchronize delta spec to canonical `platform/openspec-store/openspec/specs/workstation-tailscale-connectivity/spec.md`

## 2. Knowledge Bases & Wiki Entities

- [x] 2.1 Update `~/Developer/wiki/entities/tailscale.md` with the 40 `/32` route inventory, ALPN HTTP/1.1 enforcement, and end-to-end verification telemetry
- [x] 2.2 Consolidate and update managed skills `tailscale-macos-cross-node-optimization` and `tailscale-macos-mesh-and-nat-audit` with live verification recipes
- [x] 2.3 Verify workspace skills consistency via `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check`

## 3. Memories & Notion Hub Synchronization

- [x] 3.1 Record structured memories and lessons in AgentMemory via MCP tools
- [x] 3.2 Synchronize updated wiki entities and OpenSpec catalog to Notion Knowledge Hub via `~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh`
- [x] 3.3 Capture durable lesson and managed skill via OMP `learn`
