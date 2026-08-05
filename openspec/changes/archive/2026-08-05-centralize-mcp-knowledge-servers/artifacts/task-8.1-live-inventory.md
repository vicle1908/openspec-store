# Task 8.1: Redacted Live Inventory
# Captured: 2026-08-05T14:12:26Z
# Sections 1-7: COMPLETE (50/50 tasks)
# Hermes dependency (1.5a): RECONCILED
# No mutation performed — read-only snapshot only

## Client Configs
| Client | Path | Status | Size |
|--------|------|--------|------|
| Claude Code | ~/.claude.json | INSTALLED | 40270 bytes |
| Cursor | ~/.cursor/mcp.json | INSTALLED | 474 bytes |
| Codex | ~/.fable-5.toml | INSTALLED | 6391 bytes |
| OpenCode | ~/.config/opencode/opencode.jsonc | ABSENT | — |

## Provider Versions
| Provider | Package | Installed | Expected | Status |
|----------|---------|-----------|----------|--------|
| GitNexus | gitnexus | 1.6.9 | 1.6.9 | ✅ ALIGNED |
| Graphify | @sentropic/graphify | 0.17.1 | 0.17.1 | ✅ ALIGNED |
| Graphify (legacy) | graphifyy | 0.9.31 | — | ⚠️ LEGACY PRESENT |
| AgentMemory | @agentmemory/agentmemory | 0.9.27 | 0.9.28 | ⚠️ VERSION DRIFT |
| MCP Router CLI | @mcp_router/cli | 0.2.0 | 0.2.0 | ✅ ALIGNED |
| Node.js | node | v26.6.0 | ≥20 | ✅ |

## Process Families (DUPLICATE DETECTED)
Multiple process families detected — this is exactly what centralization fixes:

| Process | Count | Notes |
|---------|-------|-------|
| agentmemory-mcp | 6+ | Multiple npx child processes |
| graphify serve | 5+ | Legacy Python graphify.serve on graphify-out/ |
| gitnexus mcp | 4+ | Multiple direct registrations |
| mcp-router connect | 5+ | Bridge processes |

## Graph/Index Freshness
| Item | Status | Details |
|------|--------|---------|
| GitNexus index | CURRENT | 18658 nodes, 51939 edges, last indexed 2026-08-05 |
| Graphify (legacy) | EXISTS | graphify-out/graph.json (18 MB) |
| Graphify (new) | ABSENT | .graphify/ not yet created |
| AgentMemory engine | DOWN | localhost:3111 not reachable |
| AgentMemory store | FALLBACK | Multiple isolated fallback stores |

## Duplicate Direct Registrations
| Client | Direct Provider Entries | Router Bridge |
|--------|------------------------|---------------|
| Claude | agentmemory (direct) | — |
| Cursor | agentmemory (direct) | mcp-router |
| Codex | — | mcp-router |

## Blockers for 8.4+
1. AgentMemory engine is DOWN — needs startup before cutover
2. AgentMemory version drift (0.9.27 vs 0.9.28) — needs upgrade
3. Legacy Graphify 0.9.31 processes still running — needs cleanup
4. Duplicate process families — exactly what cutover fixes
5. New .graphify/ layout not yet created — needs graph refresh
6. Multiple direct client registrations — needs router-only cutover
