# Synchronization Analysis: agent-harness-stage-modules ↔ converge-agent-framework-upstream

## Executive Summary

The two changes have **significant architectural conflicts** that must be resolved before implementation. The `converge-agent-framework-upstream` change explicitly constrains what `agent-harness-stage-modules` can do:

| Constraint | Source | Impact |
|------------|--------|--------|
| No WorkflowComposer in agent-core | converge design §12 | Must use native LangGraph |
| No runtime TypedDict synthesis | converge design §12 | Keep static HarnessState |
| No tool registry in agent-core | converge design §12 | Use agent-core's toolset composition |
| Parallelism from edges, not flags | converge design §12 | Remove `parallel: bool` from protocol |
| Stage packaging is consumer-local | converge design §12 | Protocol stays in agent-harness |
| agent-harness-stage-modules depends on converge | converge design §251 | Must complete converge first |

## Conflict Analysis

### CONFLICT 1: WorkflowComposer (RESOLVE: Remove)

**agent-harness-stage-modules proposed:**
```python
composer = WorkflowComposer("planning")
composer.add_module(IntakeModule())
composer.add_module(ContextModule())
composer.add_parallel("context", "impact")
graph = composer.build()
```

**converge-agent-framework-upstream requires:**
> "agent-core does NOT own a universal WorkflowComposer, dynamic state merger, stage registry, or parallel flag." (design §12)
> "Consumers own native graph topology." (design §12)

**Resolution:** Remove WorkflowComposer. Use native LangGraph graph construction directly:
```python
graph = StateGraph(HarnessState)
graph.add_node("intake", intake_handler)
graph.add_node("context", context_handler)
graph.add_node("impact", impact_handler)
graph.set_entry_point("intake")
graph.add_edge("intake", "context")
graph.add_edge("intake", "impact")  # Parallel via edges
graph.add_edge("context", "clarify")
graph.add_edge("impact", "design")
```

### CONFLICT 2: compose_states() (RESOLVE: Remove)

**agent-harness-stage-modules proposed:**
```python
CombinedState = compose_states(IntakeState, ContextState, ImpactState)
```

**converge-agent-framework-upstream requires:**
> "Runtime TypedDict synthesis is not useful to static type checking" (design §12)
> "Keep one statically declared HarnessState" (tasks §5.2)

**Resolution:** Remove compose_states(). Keep static HarnessState with proper reducers:
```python
class HarnessState(TypedDict):
    # Common fields
    ticket_id: str
    run_id: str
    # ... existing fields with correct reducers
```

### CONFLICT 3: ToolRegistry (RESOLVE: Remove)

**agent-harness-stage-modules proposed:**
```python
registry = ToolRegistry()
registry.register_shared("gitnexus", GitNexusToolProvider())
registry.register_module("security", "taint", TaintToolProvider())
```

**converge-agent-framework-upstream requires:**
> "agent-core does NOT own a universal WorkflowComposer, dynamic state merger, stage registry, or parallel flag" (design §12)
> "Tool policy composes through supported toolsets" (design §2)

**Resolution:** Remove ToolRegistry. Use agent-core's toolset composition:
```python
# Use agent-core's official toolset composition
from agent_core.sdk import build_agent

agent = build_agent(
    config=consumer_config,
    toolsets=[gitnexus_toolset, graphify_toolset],  # Official toolsets
    capabilities=[...],
)
```

### CONFLICT 4: parallel: bool flag (RESOLVE: Remove)

**agent-harness-stage-modules proposed:**
```python
class IntakeModule:
    parallel = False  # Cannot run in parallel

class ContextModule:
    parallel = True   # Can run in parallel with ImpactModule
```

**converge-agent-framework-upstream requires:**
> "Parallelism is derived from edges plus safe reducers, not a boolean on a module" (design §12)

**Resolution:** Remove `parallel` flag. Parallelism is implicit from graph edges:
```python
# Parallelism is defined by edges, not module flags
graph.add_edge("intake", "context")
graph.add_edge("intake", "impact")  # Both have intake as source → parallel
```

## Recommended Implementation Order

### Phase 1: Converge Prerequisites (Must Complete First)

The converge change has 72 tasks. Key tasks that unblock agent-harness:

| Converge Task | Description | Unblocks |
|---------------|-------------|----------|
| §11.1 | Replace HarnessConfig(ConsumerConfig) with composed config | agent-harness config |
| §11.2 | Resolve gateway explicitly, compose toolsets/capabilities | agent-harness factory |
| §11.4 | Replace message reducers with correct reducers | agent-harness state |
| §11.5 | Replace shared gate with dedicated post-stage gates | agent-harness gates |
| §11.6 | Refactor runner to use shared checkpointer boundary | agent-harness runner |

### Phase 2: agent-harness Stage Refactoring (After Converge)

Once converge §11 is complete, agent-harness-stage-modules can proceed with:

1. **Extract stages** into consumer-local modules (no new abstractions)
2. **Fix reducers** (workspace_repos, errors, gate_history)
3. **Fix gates** (dedicated post-stage gates, not shared)
4. **Fix checkpointer** (use shared core boundary)
5. **Add parallelism** via edges (not flags)

### Phase 3: Parallel Execution (If Safe)

After Phase 2, evaluate parallelism:
- Measure each stage's read/write fields
- Identify safe parallel candidates
- Add native fan-out/fan-in edges
- Test reducers, budgets, cancellation

## Task Alignment

### Tasks That Can Run in Parallel (No Conflict)

These agent-harness tasks don't conflict with converge:

| Agent-Harness Task | Description | Status |
|--------------------|-------------|--------|
| §2.1-2.6 | Characterize current behavior (tests) | Can run now |
| §8.7 | Keep simple stages in single module | Can run now |
| §9.1 | Measure stage read/write fields | Can run now |
| §11.6 | Update documentation | Can run now |

### Tasks That Must Wait for Converge

These agent-harness tasks depend on converge completion:

| Agent-Harness Task | Depends on Converge Task | Reason |
|--------------------|--------------------------|--------|
| §3.1 | §11.1 | Config composition |
| §3.3 | §11.2 | Gateway resolution |
| §3.4 | §11.2 | Factory composition |
| §4.1 | §3.4 (converge) | Toolset adaptation |
| §4.3 | §3.1 (converge) | Capability instances |
| §5.1 | §8.1 (converge) | Typed state support |
| §5.3 | §11.4 | Reducer fixes |
| §6.1 | §8.2 (converge) | Native Command |
| §6.2 | §11.5 | Gate fixes |
| §7.1 | §8.6 (converge) | Checkpointer boundary |
| §8.1-8.6 | §11.1-11.6 | Stage extraction |

## Revised agent-harness-stage-modules Design

### What to Keep

1. **StageModule protocol** (consumer-local, not promoted to core)
2. **Inline validation** (quality at every step)
3. **ConsumerConfig inheritance** (per-module override)
4. **Module directory structure** (clean separation)

### What to Remove

1. ~~WorkflowComposer~~ → Use native LangGraph
2. ~~compose_states()~~ → Keep static HarnessState
3. ~~ToolRegistry~~ → Use agent-core toolset composition
4. ~~parallel: bool~~ → Derive from edges

### What to Add

1. **Native graph construction** examples
2. **Reducer documentation** for HarnessState fields
3. **Gate pattern** (dedicated post-stage gates)
4. **Checkpointer integration** (use core boundary)

## Migration Path

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYNCHRONIZED MIGRATION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: Converge Prerequisites                               │
│  ───────────────────────────────                                │
│  converge §1-10: Core framework changes                        │
│  converge §11.1-11.6: Harness consumer migration               │
│                                                                 │
│  Phase 2: agent-harness Refactoring                            │
│  ──────────────────────────────────                             │
│  §2.1-2.6: Characterize current behavior                       │
│  §3.1-3.5: Config composition (after converge §11.1)           │
│  §4.1-4.5: Tool/capability composition (after converge §3-4)   │
│  §5.1-5.5: State contracts (after converge §8.1)               │
│  §6.1-6.5: Graph/gate fixes (after converge §8.2, §11.5)      │
│  §7.1-7.7: Runner/checkpointer (after converge §8.6)           │
│  §8.1-8.7: Stage extraction (after converge §11.1-11.6)        │
│                                                                 │
│  Phase 3: Parallel Execution (Optional)                        │
│  ─────────────────────────────────────                          │
│  §9.1-9.4: Evaluate and add parallelism                        │
│                                                                 │
│  Phase 4: CLI and Documentation                                │
│  ────────────────────────────────                               │
│  §10.1-10.4: CLI migration                                     │
│  §11.1-11.6: Verification and docs                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Recommendations

1. **Complete converge §11 first** — This unblocks all agent-harness tasks
2. **Remove conflicting abstractions** — WorkflowComposer, compose_states, ToolRegistry, parallel flag
3. **Keep consumer-local patterns** — StageModule protocol stays in agent-harness
4. **Use native LangGraph** — Graph construction, edges, Command, interrupt
5. **Derive parallelism from edges** — Not from module flags
6. **Keep static HarnessState** — With proper reducers for all fields

## Next Steps

1. Update agent-harness-stage-modules tasks to remove conflicting tasks
2. Complete converge-agent-framework-upstream §11 (harness migration)
3. Implement agent-harness refactoring with aligned design
4. Evaluate parallel execution after stage extraction
