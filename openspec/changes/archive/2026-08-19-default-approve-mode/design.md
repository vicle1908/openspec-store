## Context

The approval flow in agent-core uses pydantic-ai's `DeferredToolRequests` mechanism. When a tool has `requires_approval=True`, the adapter raises `ApprovalRequired`, which pydantic-ai catches and returns as `DeferredToolRequests`. The agent framework then stores the approval request and waits for manual approval via CLI.

Key code path in `agent-core/_ai/tools.py`:
```python
if (
    metadata is not None
    and (getattr(metadata, "requires_approval", False) or policy_requires_approval)
    and not ctx.tool_call_approved
):
    raise ApprovalRequired(metadata=approval_payload)
```

The `ctx.tool_call_approved` flag is set by the framework after manual approval. For auto-approval, we need to either:
1. Set this flag before the check
2. Or skip the check entirely for configured tools

## Goals / Non-Goals

**Goals:**
- Add `auto_approve_tools` config field to `DocsSyncConfig`
- Allow specific tools to bypass manual approval
- Maintain all security constraints (scope, limits, containment)
- Preserve audit trail for all writes

**Non-Goals:**
- Remove security constraints
- Enable writes without configuration
- Bypass audit trails
- Change the approval flow for non-configured tools

## Decisions

### Decision 1: Configuration-driven approach

**Choice**: Add `auto_approve_tools` field to `DocsSyncConfig`

**Rationale**:
- Explicit opt-in required (secure by default)
- Follows existing config pattern
- Easy to understand and configure

**Alternatives considered**:
- Environment variable: Less visible, harder to audit
- Command-line flag: Not persistent, per-run only
- Code-level constant: Not configurable per deployment

### Decision 2: Check in tools.py

**Choice**: Check `auto_approve_tools` in `_run_via_registry()` before raising `ApprovalRequired`

**Rationale**:
- Single point of change
- Minimal code modification
- Preserves existing approval flow for other tools

**Alternatives considered**:
- Modify pydantic-ai framework: Too invasive
- Add new ApprovalMode: Would require changes to authority_policy.py
- Set `ctx.tool_call_approved` flag: Would require changes to agent framework

### Decision 3: Pass through agent construction chain

**Choice**: Pass `auto_approve_tools` through `build_agent()` → `AgentRuntime` → `AgentRuntimeDeps`

**Rationale**:
- Follows existing parameter passing pattern
- Makes config available where needed
- No changes to agent-core SDK interface

**Alternatives considered**:
- Global config: Not thread-safe, not per-agent
- Environment variable: Less visible, harder to audit
- Direct config access: Would require config import in tools.py

## Risks / Trade-offs

### Risk 1: Security bypass
**Risk**: Auto-approval could bypass security constraints
**Mitigation**: 
- Scope containment still enforced (`allowed_doc_roots`)
- Path policy still enforced (`resolve_allowed_write_path`)
- Limits still enforced (max_calls, timeout)
- Audit trail preserved

### Risk 2: Misconfiguration
**Risk**: User configures auto-approve for sensitive tools
**Mitigation**:
- Explicit opt-in required
- Warning logged for unknown tools
- Documentation emphasizes security implications

### Risk 3: Audit trail gaps
**Risk**: Auto-approved operations might not be logged
**Mitigation**:
- All writes logged in `writes.sqlite3`
- Lifecycle audit events created
- Approval status recorded as "auto-approved"

## Migration Plan

1. **Phase 1**: Add config field to `DocsSyncConfig`
2. **Phase 2**: Pass through agent construction chain
3. **Phase 3**: Implement check in `tools.py`
4. **Phase 4**: Update `config.yaml` with default value
5. **Phase 5**: Run tests and verify

**Rollback**: Remove `auto_approve_tools` from config.yaml

## Testing Strategy

1. **Unit tests**: Test config parsing
2. **Integration tests**: Test auto-approved tools bypass approval
3. **E2E verification**: Run sync with `auto_approve_tools: [write_doc]`
4. **Security tests**: Verify scope/limits still enforced
