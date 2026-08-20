## Context

See proposal.md for the current source/spec mismatch. The implementation must preserve the existing layered boundary: `agent-core` owns runtime composition, `agent-docs-sync` owns approval-gated documentation behavior, `agent-harness` remains a read-only workflow consumer, and the active observability change owns telemetry activation.

## Goals / Non-Goals

**Goals:**

- Make optional pydantic-ai-harness capabilities explicit at the public composition seam.
- Keep mandatory platform capabilities (instrumentation, tool preparation, hooks, and fallback process-local step persistence) distinct from optional harness behavior.
- Share caller-owned persistence between step continuation and ConversationSearch when requested.
- Attach ToolGuardrails only in write-capable docs-sync modes while retaining containment and approval as authoritative.
- Prove behavior through public agent construction and deterministic in-process models.

**Non-Goals:**

- No provider calls, credentials, live model acceptance, observability activation, or LLM configuration changes.
- No direct edits to archived artifacts; the corrective ledger is new evidence only.

## Decisions

- **Optional capability boundary:** `BaseAgent`/`build_agent` pass caller-owned `capabilities` through unchanged. `AgentRuntime` stops creating optional TieredCompaction, SystemReminders, and SpendLimits implicitly. Existing mandatory platform composition remains explicit and documented.
- **Configuration ownership:** remove unread capability dictionaries from compatibility configuration, or materialize them into typed capability instances before public construction. A configuration key that cannot be honored SHALL fail closed instead of being silently ignored.
- **Spend accounting:** when a USD budget is enabled, configure the upstream capability to raise on unpriced models in acceptance fixtures; production may supply an approved price function. A model counted as zero is not enforcement evidence.
- **Shared history:** change the conversation-search factory to accept the runtime’s caller-owned `SnapshotStore`/StepStore, and make the owning composition site pass the same object used by `StepPersistence`.
- **Docs guardrail assembly:** generation/full-sync build paths compose path, shell, and result guardrails alongside existing Input/OutputGuardrails. Read-only/check modes do not receive write-capable ToolGuardrails. Existing hooks and tools remain the final containment authority.
- **Extra ownership:** agent-core is the only repository that may retain `[dynamic-workflow]` because it owns optional capability composition; agent-harness and docs-sync remove the extra unless a direct production consumer is explicitly added.
- **Behavioral test harness:** use public `Agent`, `build_agent`, `TestModel`/`FunctionModel`, public ToolCall/ToolResult boundary objects, a deterministic price function, and an in-memory disposable store. No private upstream modules are imported by production code.
- **Evidence ordering:** run the quality prerequisite first, then agent-core, docs-sync, agent-harness compatibility, OpenSpec delta sync, and final integrated verification. Any source drift invalidates dependent evidence.

## Risks / Trade-offs

- [Default behavior changes] → mark the public-default correction as breaking in release notes and test both explicit-enabled and omitted-capability paths.
- [Third-party API drift] → pin the reviewed `2.32.0/0.23.0` tuple, probe public signatures, and fail the compatibility task if signatures differ.
- [Guardrail ordering] → test both guardrail and hook paths; never rely on ToolGuardrail alone for path containment or approval.
- [Shared-store lifecycle] → require construction-time failure for unavailable declared stores and preserve process-local diagnostics for omitted persistence.
- [Advisor introduces model selection] → accept only an explicit caller-owned advisor model; do not reopen global provider precedence.

## Migration Plan

1. Complete `restore-agent-pydantic-quality-gates` and freeze accepted repository SHAs.
2. Update agent-core composition/config/tests and run its public-boundary matrix.
3. Update docs-sync production guardrail assembly and tests.
4. Remove consumer-only dependency extras and verify all three lockfiles/import origins.
5. Update delta specs/docs and run strict validation plus no-delta/rollback checks.
6. Keep the archived changes untouched; record their corrective ledger mappings and archive only after one frozen integrated evidence bundle passes.
