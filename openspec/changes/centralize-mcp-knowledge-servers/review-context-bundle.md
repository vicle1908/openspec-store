# Review Context Bundle: centralize-mcp-knowledge-servers

## Change Overview
- **Name:** centralize-mcp-knowledge-servers
- **Status:** Source implemented (25/58 tasks), review pending
- **Breaking:** Yes — removes direct client GitNexus/Graphify/AgentMemory registrations
- **Repositories:** go-microservices (provider boundaries), mcp-router (app-native transaction)
- **Implementation commits:** go-microservices `6a2629f`, mcp-router `1be46aa`
- **Previous review:** MCP Router app amendment APPROVED for source; native five-provider PENDING

## Provider Pins (verified 2026-08-05)
| Tool | Package | Version | Runtime |
|------|---------|---------|---------|
| GitNexus | gitnexus@1.6.9 | npm latest | Node.js 22+ |
| Graphify | @sentropic/graphify@0.17.1 | npm latest | Node.js 20+ |
| AgentMemory | @agentmemory/agentmemory@0.9.28 | npm latest | Node.js 20+ |
| MCP Router CLI | @mcp_router/cli@0.2.0 | npm latest | Node.js 18+ |
| MCP Router App | com.electron.mcp-router | 0.6.3 | Electron |

## Key Design Decisions (D1-D8)
- D1: MCP Router is sole client-facing gateway
- D2: One GitNexus process serves the registry with repository filtering
- D3: One Graphify adapter replaces two registrations with explicit project_path
- D4: AgentMemory fails closed when engine unavailable (no fallback store)
- D5: Hermes native memory is separate from shared AgentMemory
- D6: Repository source changes precede live mutation (RED→GREEN)
- D7: Live cutover is separate transaction requiring explicit GO
- D8: Backup/rollback is format-aware

## Implementation Evidence
### go-microservices (176 files, +30785/-1574 lines)
- Topology matrix/inventory: 12 focused tests
- Transaction planner: 18 focused tests
- Graphify adapter fixture: 3/3 tests
- AgentMemory compat fixture: 2/2 tests
- AgentMemory boundary: 11/11 tests
- Provider lock: exact npm v3 registry evidence
- Gates passed: make knowledge-test, agentmemory-test, validate-agent-guidance, bash syntax, python compilation, node syntax, git diff --check, openspec validate --strict

### mcp-router (19 files, +2540/-1 lines)
- App-native declarative transaction: preview/apply/restore
- Command file authorization: owner/mode/digest validation
- Secure store: safeStorage encrypted recovery journal
- Service: MCPServerManager, TokenManager, SharedConfigManager integration
- Tests: 7 test files covering all transaction surfaces
- Package: distinct build identity from upstream 0.6.3

## Delta Specs (8)
1. developer-code-intelligence: MODIFIED — Graphify 0.9.26→0.17.1, router-owned servers
2. developer-memory: MODIFIED — AgentMemory 0.9.27→0.9.28, fail-closed engine proxy
3. operational-readiness: MODIFIED — 11-client matrix, MCP Router as sole gateway

## Open Blocks
- Task 1.3: Five-provider plan review (THIS REVIEW)
- Task 1.4a: Commit app amendment to main store
- Task 1.5a: Review access-map-only token ownership
- Tasks 2.2-2.6: RED fixture tests (topology, process, GitNexus, AgentMemory)
- Tasks 4.1-4.5: Router-owned GitNexus/Graphify source behavior
- Tasks 5.0-5.4: AgentMemory router-only bootstrap
- Tasks 6.1-6.5: Backup/cutover/rollback
- Tasks 7.2-7.5: Documentation/review gates
- Tasks 8-9: Live eligibility and cutover (BLOCKED by dependency)

## Critical Dependency
optimize-hermes-agent-configuration owns Hermes MCP Router bridge immutability.
This change cannot mutate Hermes or live MCP Router state until reconciled.
