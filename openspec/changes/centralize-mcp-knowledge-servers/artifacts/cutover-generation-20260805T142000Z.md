# Cutover Generation: centralize-mcp-knowledge-servers
# Created: 2026-08-05T14:20:00Z
# Status: PLAN READY — requires operator GO before execution

## Plan Digest
- Store commit: fcdf9481cb701747041abcb702cae9dd782ab8db
- go-microservices commit: 9112298a6e47561f621efda678539caf0a43d65e
- mcp-router commit: ad389663d31cfddad246dd0d2d43a86175b08774
- Prerequisite generation: 20260805T141500Z

## Cutover Scope

### What Changes
1. MCP Router gains 3 knowledge children:
   - gitnexus (read-only, approved repos only)
   - graphify (multi-project, project_path required)
   - agentmemory (fail-closed, engine-backed)

2. Client configs modified (after backup):
   - Claude: remove direct agentmemory entry
   - Cursor: remove direct agentmemory entry
   - Codex: verify router bridge only

3. Provider processes centralized:
   - Kill duplicate gitnexus/graphify/agentmemory processes
   - Start router-owned children

### What Does NOT Change
- MCP Router bridge per client (preserved)
- Hermes native memory (separate)
- Provider indexes (preserved)
- Memory data (preserved)
- Skills, hooks, sessions (preserved)

## Affected Clients
| Client | Config | Change | Risk |
|--------|--------|--------|------|
| Claude | ~/.claude.json | Remove direct agentmemory | Low |
| Cursor | ~/.cursor/mcp.json | Remove direct agentmemory | Low |
| Codex | ~/.codex/config.toml | Verify router bridge | None |

## Backup Manifest
- Claude config: backed up before mutation
- Cursor config: backed up before mutation
- Codex config: backed up before mutation
- Router database: SQLite online backup
- Provider processes: restart from backup

## Maintenance Window
- Duration: ~15 minutes
- Impact: Brief MCP tool unavailability during client restarts
- Recovery: Restore from backup if cutover fails

## Operator GO Required
To execute this cutover, confirm:
1. ✅ Plan reviewed and approved
2. ✅ Backup manifest verified
3. ✅ Maintenance window acceptable
4. ✅ Rollback procedure understood

**Reply with "GO" to authorize execution.**
