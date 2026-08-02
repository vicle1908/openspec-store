# Design: Ecosystem Reference Cleanup

## Scan Results

| Category | Count | Action |
|---|---|---|
| Code comments with old openspec/ paths | 8 | Fixed to reference store |
| Docs with stale stats | 1 | Updated openspec-setup.md |
| Python repos with openspec/schemas/ dependency | 1 | Verified correct (local schemas) |
| agent-docs-sync path matching | 2 | Verified works with store layout |
| AGENTS.md references | 0 | Already correct |

## Files Changed

- `go-microservices/docs/openspec-setup.md` — rewrote with current stats, git tracking
- `agent-core/src/agent_core/foundation/errors.py` — updated docstring
- `tdt-core/src/tdt_core/paths.py` — updated docstring
- `tdt-core/src/tdt_core/clients/gitlab_mr.py` — updated docstring
- `tdt-core/src/tdt_core/scheduler/README.md` — updated reference
- `jira-skill/src/jira_skill/impact/ticket_mr_resolver.py` — updated docstring
- `jira-skill/src/jira_skill/impact/feature_map.py` — updated docstring
- `jira-skill/src/jira_skill/cli.py` — updated 3 references
