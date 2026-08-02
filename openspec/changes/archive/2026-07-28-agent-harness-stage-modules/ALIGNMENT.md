# Final Alignment Summary: agent-harness-stage-modules

## Status: ✅ ALIGNED with converge-agent-framework-upstream

All artifacts have been verified and are consistent with the converge constraints.

---

## Artifact Alignment Checklist

### ✅ proposal.md

| Constraint | Status | Evidence |
|------------|--------|----------|
| Depends on converge | ✅ | "Depend on converge-agent-framework-upstream" |
| Consumer-local stages | ✅ | "Keep stage packaging consumer-local and structural" |
| Native LangGraph | ✅ | "Build the workflow directly with native LangGraph" |
| No WorkflowComposer | ✅ | Non-goals: "Creating a tool registry, workflow DSL..." |
| No ToolRegistry | ✅ | "Replace tool-name lookup and a second ToolRegistry" |
| No compose_states | ✅ | "Keep one statically declared workflow state; do not synthesize TypedDict" |
| No parallel flag | ✅ | "Determine parallelism from explicit graph topology...not a parallel boolean" |

### ✅ design.md

| Constraint | Status | Evidence |
|------------|--------|----------|
| Consumer-local StageDefinition | ✅ | Decision 1: "consumer-local structural objects" |
| Static HarnessState | ✅ | Decision 4: "One statically declared HarnessState" |
| Native graph construction | ✅ | Decision 5: "Native graph construction is the only topology authority" |
| Dedicated post-stage gates | ✅ | Decision 6: "Dedicated post-stage gates have one target" |
| Shared checkpointer boundary | ✅ | Decision 7: "The shared core checkpointer boundary serves every operation" |
| Typed toolsets/capabilities | ✅ | Decision 3: "Official toolsets filtered by explicit per-stage policy" |
| No workflow DSL | ✅ | Non-Goals: "A workflow DSL over LangGraph" |
| No runtime TypedDict | ✅ | Non-Goals: "Runtime generation or merging of TypedDict classes" |

### ✅ specs/stage-module-protocol/spec.md

| Constraint | Status | Evidence |
|------------|--------|----------|
| Consumer-local contract | ✅ | "consumer-local stage definition" |
| Typed toolsets/capabilities | ✅ | "typed official toolsets/capabilities" |
| No string names | ✅ | "WHEN a stage supplies an unresolved string...SHALL fail" |
| No depends_on/parallel | ✅ | "Graph dependencies and parallelism SHALL be declared by native graph edges" |

### ✅ specs/native-workflow-composition/spec.md

| Constraint | Status | Evidence |
|------------|--------|----------|
| Native LangGraph | ✅ | "native LangGraph StateGraph, node, edge, Command, interrupt, and checkpointer APIs" |
| No WorkflowComposer | ✅ | "SHALL NOT add a registry-backed WorkflowComposer abstraction" |
| Safe parallelism | ✅ | "Parallel edges SHALL be added only after read/write, reducer, authority, budget, and fan-in behavior are proven safe" |

### ✅ specs/stage-toolset-composition/spec.md

| Constraint | Status | Evidence |
|------------|--------|----------|
| Official toolsets | ✅ | "public Pydantic AI toolsets and capabilities through the converged agent_core.sdk" |
| No ToolRegistry | ✅ | "SHALL NOT introduce a second shared/module/stage ToolRegistry" |
| Explicit gateway | ✅ | "Stage agent construction SHALL require a resolved TDT gateway" |

### ✅ specs/state-composition/spec.md

| Constraint | Status | Evidence |
|------------|--------|----------|
| Static HarnessState | ✅ | "Keep one statically declared HarnessState" |
| Correct reducers | ✅ | "Replace message reducers on workspace_repos, errors, and gate_history" |
| No runtime synthesis | ✅ | "prohibit runtime TypedDict synthesis" |

### ✅ specs/agent-harness-workflow/spec.md

| Constraint | Status | Evidence |
|------------|--------|----------|
| Incremental extraction | ✅ | "Incremental stage modularization" |
| Dedicated gates | ✅ | "One-target gate interrupts" |
| Read-only authority | ✅ | "Read-only workflow authority" |

### ✅ specs/agent-harness-runner/spec.md

| Constraint | Status | Evidence |
|------------|--------|----------|
| Shared checkpointer | ✅ | "shared agent-core checkpointer boundary" |
| Durable resume | ✅ | "Durable interrupt resume" with native Interrupt.id |
| Public status inspection | ✅ | "public compiled-graph state APIs" aget_state/aget_state_history |

### ✅ tasks.md

| Constraint | Status | Evidence |
|------------|--------|----------|
| No WorkflowComposer | ✅ | Task 6.1: "add no WorkflowComposer" |
| No parallel flag | ✅ | Task 9.4: "rather than adding a dormant boolean/API" |
| Converge dependency | ✅ | Task 1.1: "Complete and verify converge-agent-framework-upstream" |
| Incremental extraction | ✅ | Tasks 8.1-8.6: Extract stages incrementally |
| Characterization tests | ✅ | Tasks 2.1-2.6: Characterize current behavior first |

---

## Key Design Principles (Aligned)

1. **Consumer-local stages** — StageDefinition stays in agent-harness, not promoted to core
2. **Native LangGraph** — Direct StateGraph construction, no DSL wrapper
3. **Static state** — One HarnessState with correct reducers, no runtime synthesis
4. **Typed composition** — Official toolsets/capabilities, no string lookups
5. **Dedicated gates** — Post-stage interrupt nodes with one continuation
6. **Shared checkpointer** — Use agent-core boundary, no local saver factory
7. **Safe parallelism** — Derived from edges + reducer safety, not boolean flags

---

## Implementation Order

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Converge §11 (harness migration) — BLOCKING                │
│  2. Characterize current behavior (tests) — CAN RUN NOW        │
│  3. Config composition (after converge §11.1)                  │
│  4. Tool/capability composition (after converge §3-4)          │
│  5. State/reducer fixes (after converge §8.1)                  │
│  6. Gate fixes (after converge §11.5)                          │
│  7. Runner/checkpointer (after converge §8.6)                  │
│  8. Stage extraction (after converge §11.1-11.6)               │
│  9. Parallel evaluation (optional, after extraction)           │
│  10. CLI migration and documentation                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Conclusion

**All artifacts are aligned.** The agent-harness-stage-modules change:

1. ✅ Depends on converge-agent-framework-upstream
2. ✅ Uses consumer-local stage definitions (not promoted to core)
3. ✅ Uses native LangGraph (no WorkflowComposer DSL)
4. ✅ Keeps static HarnessState (no runtime TypedDict synthesis)
5. ✅ Uses typed toolsets/capabilities (no ToolRegistry)
6. ✅ Uses dedicated post-stage gates (not shared gate)
7. ✅ Uses shared checkpointer boundary (not local factory)
8. ✅ Derives parallelism from edges (not boolean flags)

**Ready for implementation** after converge-agent-framework-upstream §11 is complete.
