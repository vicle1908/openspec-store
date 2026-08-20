## Context

See proposal.md for the current source/spec mismatch. The implementation must preserve the existing layered boundary: `agent-core` owns runtime composition, `agent-docs-sync` owns approval-gated documentation behavior, `agent-harness` remains a read-only workflow consumer, and the active observability change owns telemetry activation.

## Goals / Non-Goals

**Goals:**

- Make optional pydantic-ai-harness capabilities explicit at the public composition seam.
- Keep mandatory platform capabilities (instrumentation, tool preparation, hooks, and fallback process-local step persistence) distinct from optional harness behavior.
- Share caller-owned persistence between step continuation and ConversationSearch when requested, with conversation-scoped isolation by default.
- Attach exact-selector ToolGuardrails only in write-capable docs-sync modes while retaining containment and approval as authoritative and producing one redacted audit decision.
- Prove behavior through public agent construction and deterministic in-process models.

**Non-Goals:**

- No provider calls, credentials, live model acceptance, observability activation, or LLM configuration changes.
- No direct edits to archived artifacts; the corrective ledger is new evidence only.

## Decisions

- **Optional capability boundary:** `BaseAgent`/`build_agent` pass caller-owned `capabilities` through unchanged. `AgentRuntime` stops creating optional TieredCompaction, SystemReminders, and SpendLimits implicitly. Existing mandatory platform composition remains explicit and documented. Retained internal convenience kwargs, if needed for migration tests, are compatibility-only and never projected through public construction or docs.
- **Configuration ownership:** delete the unread harness-capability dictionaries from `AgentConfig`, its compatibility tests, and stale docs. Supported file-based composition remains Pydantic AI `AgentSpec`; live non-serializable capabilities remain caller-owned objects passed through `capabilities=[...]`. No new wrapper registry or generic builder layer is introduced.
- **Spend accounting:** when a USD budget is enabled, configure the upstream capability to raise on unpriced models in acceptance fixtures; production may supply an approved price function. A model counted as zero is not enforcement evidence.
- **Shared history:** change the existing non-exported conversation-search helper to require a caller-owned `SnapshotStore`/StepStore and construct `scope="conversation"`; callers needing all-store search use direct explicit upstream composition under their own single-tenant policy. Public acceptance constructs StepPersistence and ConversationSearch from the same store object without inspecting private upstream attributes, uses the runtime's stable correlation/conversation identity, proves two-conversation isolation, and records the caller's snapshot-retention policy. Do not add builders for capabilities already constructible upstream.
- **Docs guardrail assembly:** generation/full-sync build paths compose path, shell, and result guardrails alongside existing Input/OutputGuardrails. The write ToolGuardrail targets `write_doc.path` and `sync_spec.main_path`, while the shell guard targets `shell_execute.command` when visible. The write guard calls the existing `resolve_allowed_write_path` without modifying that CRITICAL shared function; `sync_spec.delta_path` remains a read input. Read-only/check modes do not receive write-capable ToolGuardrails. Existing hooks and tools remain the final containment authority. Because upstream ToolGuardrail is innermost, acceptance records which layer rejected each attempt, proves direct guard decisions separately, proves a valid path reaches the guard before approval, and emits exactly one redacted audit event through the existing sink.
- **Extra ownership:** agent-core retains `[dynamic-workflow]` only after `build_agent(..., capabilities=[DynamicWorkflow(...)])` executes a deterministic bounded workflow against harness `0.23.0` and `pydantic-monty>=0.0.19`, and public authority validation classifies DynamicWorkflow as runtime authoring. If that seam or authority gate does not pass, agent-core also removes the extra. Agent-harness and docs-sync remove it because they have no direct consumer. All `0.0.18` documentation is corrected.
- **Behavioral test harness:** layer tests: unit tests for store/price/guard functions, integration tests through `build_agent`, and functional multi-request tests with public `TestModel`/`FunctionModel`, a deterministic price function, disposable stores, and two stable conversation identities. No private upstream modules are imported by production code or acceptance tests.
- **Documentation execution:** representative harness snippets are imported and constructed against the frozen tuple; deprecated aliases, missing required arguments, and unsupported enum/window values fail the documentation gate.
- **Evidence ordering:** run the quality prerequisite first, then agent-core, docs-sync, agent-harness compatibility, OpenSpec delta sync, and final integrated verification. Any source drift invalidates dependent evidence.
- **Execution coordination:** run the integration session from `/Users/androidteam/Developer`, read apply instructions from the planning worktree, and mutate each repository only after its explicit writer packet is frozen. The repo-local OpenSpec planning root is context, not cross-repository write authority.

## Risks / Trade-offs

- [Default behavior changes] → mark the public-default correction as breaking in release notes and test both explicit-enabled and omitted-capability paths.
- [Third-party API drift] → pin the reviewed `2.32.0/0.23.0` tuple, probe public signatures, and fail the compatibility task if signatures differ.
- [Guardrail ordering/shared resolver risk] → characterize all existing `resolve_allowed_write_path` callers and add the exact-selector guardrail as a new caller without changing the shared resolver; attribute outer-hook versus inner-guard rejections honestly, prevent duplicate audit records, and never rely on ToolGuardrail alone for containment or approval.
- [Shared-store lifecycle and disclosure] → require construction-time failure for unavailable declared stores, default to conversation scope, prove isolation between two conversation identities, preserve process-local diagnostics for omitted persistence, and state that pruned snapshots are no longer searchable.
- [Advisor introduces model selection] → accept only an explicit caller-owned advisor model; do not reopen global provider precedence.

## Migration Plan

1. Complete `restore-agent-pydantic-quality-gates`, then `enforce-openspec-archive-readiness-gates`, and freeze their accepted SHAs.
2. Update agent-core composition/config/shared-history scope/tests and run its public-boundary plus cross-conversation-isolation matrix.
3. Update docs-sync exact-selector production guardrail assembly, audit behavior, and tests without changing the canonical path resolver.
4. Remove consumer-only dependency extras, correct Monty documentation, and verify all three lockfiles/import origins.
5. Update delta specs/docs and run strict validation plus rollback checks.
6. Keep the archived changes untouched; record their corrective ledger mappings and archive only after one frozen integrated evidence bundle passes the new archive validator.
