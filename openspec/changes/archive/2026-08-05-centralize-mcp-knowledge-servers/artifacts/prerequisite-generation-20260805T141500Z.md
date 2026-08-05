# Prerequisite Generation: centralize-mcp-knowledge-servers
# Replaces: prereq-e8d79b8d0a27b45a (superseded by MCP Router app amendment)
# Created: 2026-08-05T14:15:00Z
# Status: READ-ONLY PLAN — requires operator GO before execution

## Scope

This prerequisite generation captures the exact post-amendment state and defines
the required actions before live cutover (sections 8-9) can proceed.

## Components

### Provider Pins (verified 2026-08-05)
| Provider | Package | Installed | Required | Action |
|----------|---------|-----------|----------|--------|
| GitNexus | gitnexus | 1.6.9 | 1.6.9 | ✅ Aligned |
| Graphify (new) | @sentropic/graphify | 0.17.1 | 0.17.1 | ✅ Aligned |
| Graphify (legacy) | graphifyy | 0.9.31 | — | ⚠️ Needs cleanup |
| AgentMemory | @agentmemory/agentmemory | 0.9.27 | 0.9.28 | ⚠️ Needs upgrade |
| MCP Router CLI | @mcp_router/cli | 0.2.0 | 0.2.0 | ✅ Aligned |
| MCP Router App | com.electron.mcp-router | 0.6.3 | 0.6.3 | ✅ Aligned |

### Blockers Requiring Operator GO
1. **AgentMemory version drift**: 0.9.27 installed, 0.9.28 required
   - Action: `npm install -g @agentmemory/agentmemory@0.9.28 @agentmemory/mcp@0.9.28`
   - Risk: Low — patch version bump
   - Rollback: `npm install -g @agentmemory/agentmemory@0.9.27`

2. **AgentMemory engine down**: localhost:3111 not reachable
   - Action: Start agentmemory server
   - Risk: Medium — engine startup may fail
   - Rollback: Stop agentmemory server

3. **Duplicate process families**: Multiple graphify/agentmemory/gitnexus processes
   - Action: Kill legacy processes after cutover
   - Risk: Medium — may disrupt active sessions
   - Rollback: Restart killed processes

4. **Legacy Graphify processes**: graphify.serve on graphify-out/
   - Action: Stop after .graphify/ migration complete
   - Risk: Low — legacy served by new adapter
   - Rollback: Restart legacy graphify.serve

5. **Direct client registrations**: Claude has direct agentmemory entry
   - Action: Remove after router-only cutover
   - Risk: Low — router bridge replaces direct entry
   - Rollback: Restore direct entry from backup

### Required Prerequisite Actions (in order)
1. Upgrade AgentMemory to 0.9.28
2. Start AgentMemory engine
3. Build .graphify/graph.json for microservices and mcp-router
4. Verify Graphify adapter works with new layout
5. Create MCP Router app transaction for knowledge children
6. Backup all client configs
7. Apply cutover plan
8. Verify router-only topology
9. Clean up legacy processes

### Cutover Plan
- Phase 1: Provider readiness (steps 1-4)
- Phase 2: Router configuration (step 5)
- Phase 3: Client cleanup (steps 6-8)
- Phase 4: Verification and cleanup (step 9)

### Rollback Manifest
- Client configs: backed up before mutation
- Router database: SQLite online backup
- Provider processes: restart from backup
- Memory data: preserved in ~/.agentmemory/

### Evidence Requirements
- [ ] AgentMemory 0.9.28 health check passes
- [ ] .graphify/graph.json exists for both repos
- [ ] Graphify adapter serves both projects
- [ ] MCP Router app transaction preview shows correct plan
- [ ] All client configs backed up
- [ ] No duplicate direct registrations after cutover
- [ ] Router-only topology verified
