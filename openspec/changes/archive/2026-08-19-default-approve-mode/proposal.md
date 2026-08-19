## Why

During real operations verification of agent-docs-sync, we discovered that the approval flow blocks all documentation writes. The current configuration requires:
- A lifecycle identity provider (unavailable)
- Authorized subject IDs in `approval_actors` (empty by default)
- Manual approval via CLI for each write operation

This results in 21 write_doc calls started but 0 completed. Agents cannot produce documentation output without manual intervention, making the pipeline ineffective for autonomous operation.

**Non-goals:**
- Remove security constraints (scope, limits, containment remain)
- Enable writes without configuration (explicit opt-in required)
- Bypass audit trails (all writes still logged)

## What Changes

- Add `auto_approve_tools` configuration field to `DocsSyncConfig`
- Allow specific tools to bypass the manual approval flow when configured
- Maintain all existing security constraints (path containment, scope, limits)
- Preserve audit trail for all writes

**BREAKING**: None — this is additive configuration.

## Capabilities

### New Capabilities
- `default-approve-mode`: Configuration-driven auto-approval for specific tools, bypassing manual approval while maintaining security constraints

### Modified Capabilities
- `docs-sync-configuration`: Extended with `auto_approve_tools` field

## Impact

**Affected code:**
- `agent-docs-sync/config.py` — New config field
- `agent-docs-sync/agents/generation.py` — Pass config to agent
- `agent-docs-sync/agent.py` — Accept new parameter
- `agent-core/sdk/agents.py` — Accept new parameter
- `agent-core/_ai/agent.py` — Pass to AgentRuntime
- `agent-core/_ai/tools.py` — Check before raising ApprovalRequired

**Affected APIs:**
- `build_agent()` — New optional parameter
- `build_doc_sync_agent()` — New optional parameter
- `build_generation_agent()` — Uses config field

**Dependencies:**
- No new dependencies

**Systems:**
- agent-docs-sync approval flow
- agent-core tool execution pipeline
