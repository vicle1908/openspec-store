## Context

agent-core v0.2.0+ provides harness capabilities (planning, subagents, guardrails, dynamic_workflow) that agent-docs-sync should leverage. Current implementation partially uses these features but doesn't fully integrate them.

## Goals / Non-Goals

**Goals:**
1. Fully integrate agent-core planning for better LLM classification
2. Add subagents for delegated validation tasks
3. Add guardrails for input validation
4. Upgrade to DynamicWorkflow for complex routing

**Non-Goals:**
1. Replace existing tools (Scanner, Classifier, etc.)
2. Change agent-core itself
3. Add new features beyond harness integration

## Decisions

### Decision 1: Planning Integration

**Choice:** Use agent-core's planning capability with custom guidance

**Rationale:**
- Planning decomposes complex classification tasks
- Caches plans for repeated execution
- Integrates naturally with existing LlmConfig

**Implementation:**
```python
harness_config={
    "planning": {
        "guidance": config.planning_guidance,
        "cache_ttl": "5m",
    }
}
```

### Decision 2: SubAgents Integration

**Choice:** Use agent-core's subagents for validation delegation

**Rationale:**
- Separates concerns (discovery vs validation)
- Allows independent scaling
- Inherits parent tools automatically

**Implementation:**
```python
harness_config={
    "subagents": {
        "agents": [
            {"name": "validator", "model": "gpt-4o-mini"},
        ],
        "inherit_tools": True,
    }
}
```

### Decision 3: Guardrails Integration

**Choice:** Use agent-core's guardrails for path validation

**Rationale:**
- Standardized input validation
- Replaces custom hooks (validate_write_path)
- More secure than manual validation

**Implementation:**
```python
def doc_path_guard(messages, info):
    for msg in messages:
        if "tool_name" in msg and msg["tool_name"] == "write_doc":
            path = msg["args"].get("path", "")
            if not path.startswith("docs/"):
                return GuardResult(action="block")
    return GuardResult(action="allow")
```

### Decision 4: DynamicWorkflow Upgrade

**Choice:** Upgrade from basic WorkflowBuilder to DynamicWorkflow

**Rationale:**
- More flexible routing
- Better conditional execution
- Supports complex pipelines

**Implementation:**
```python
from agent_core.orchestration import DynamicWorkflow

workflow = DynamicWorkflow(
    name="discovery-pipeline",
    nodes=[...],
    edges=[...],
)
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Planning adds latency | Cache plans for 5 minutes |
| SubAgents increase complexity | Start with minimal delegation |
| Guardrails may block valid operations | Extensive testing before deployment |
| DynamicWorkflow is new | Fall back to basic WorkflowBuilder if issues |

## Migration Plan

1. Phase 1: Add planning guidance to LlmConfig
2. Phase 2: Add subagents configuration
3. Phase 3: Implement guardrail function
4. Phase 4: Upgrade to DynamicWorkflow

## Open Questions

1. Should we enable planning by default or require opt-in?
2. How many subagents should we support initially?
3. What paths should guardrails allow/deny?
