## Context

`agent-harness` stores Pydantic artifacts and enums directly in LangGraph PostgreSQL checkpoints. A live run created by one CLI process and inspected by another proves restart durability, but the permissive reader emits compatibility warnings for each custom type because the shared `agent-core` saver uses LangGraph's default serializer without a consumer allowlist. Strict mode currently blocks unregistered constructors and may fall back to raw values that graph-schema validation can reconstruct, but LangGraph explicitly warns that the permissive path will be blocked in a future version. The graph's `current_stage` channel is represented as `str` in both policies and is not treated as a serializer regression.

The shared factory must remain owned by `agent-core`, while the concrete types and trust decision remain owned by `agent-harness`. No database migration or dependency change is required. The affected deployment is the manual `agent-harness` CLI process using an existing PostgreSQL service; Docker and launchd topology do not change.

## Goals / Non-Goals

**Goals:**

- Make all durable harness lifecycle operations readable under strict MessagePack enforcement across fresh operating-system processes.
- Keep the shared saver factory generic and consumer-neutral.
- Permit only exact, trusted checkpoint types reachable from `HarnessState`.
- Preserve current checkpoint schema, CLI JSON/stdout behavior, gate authorization, and saver setup/lifetime behavior.
- Verify both fresh strict checkpoints and the already-created live checkpoint when backward compatibility permits.

**Non-Goals:**

- Allowing arbitrary modules or all MessagePack extension types.
- Changing workflow routing, gate decisions, checkpoint schema version, or PostgreSQL schema.
- Adding a package or changing frozen framework versions.
- Approving or rejecting a live gate automatically.

## Decisions

### Consumer-provided allowlist at the shared factory boundary

`create_async_checkpointer` will accept an optional immutable collection of exact `(module, type)` entries. When supplied, it will construct LangGraph's public `JsonPlusSerializer(allowed_msgpack_modules=...)` and pass it through the saver factory's public `serde=` parameter before setup and use. Existing callers that omit it retain current behavior.

This keeps `agent-core` independent of harness models. Importing harness classes in core was rejected because it reverses dependency ownership. Constructing `JsonPlusSerializer` directly in every harness lifecycle method was rejected because it duplicates saver configuration and bypasses the shared factory boundary. Applying `saver.with_allowlist(...)` after construction was also rejected: LangGraph 1.2.9 preserves a serializer whose base policy is permissive (`True`), so normal-mode reads would continue to warn despite the supplied entries.

### One explicit harness checkpoint allowlist

`agent-harness` will define one auditable constant containing every custom enum and Pydantic model reachable from durable `HarnessState` values, including all stage artifacts and their nested custom models, gate payloads, trace entries, and evidence models. Every durable factory call will pass that same constant.

An unrestricted module wildcard or `allowed_msgpack_modules=True` was rejected because checkpoint deserialization is a code-execution trust boundary. Deriving the list from arbitrary runtime values was rejected because it would silently broaden trust when state changes.

### Strict-mode process integration test

The real PostgreSQL lifecycle test will run its subprocesses with `LANGGRAPH_STRICT_MSGPACK=true`. It will assert successful run/status/resume/report behavior, no unregistered-type warning on stderr, valid isolated JSON on stdout, and no completed-stage replay. A focused `agent-core` unit test will verify allowlist forwarding without requiring PostgreSQL.

Unit-only serialization tests were rejected because the defect appears specifically when a separate process reopens a persisted checkpoint.

### Error handling and observability

An unknown or omitted allowlist entry may be returned by the current LangGraph release as raw data under strict mode, so tests assert typed artifact and nested-enum reconstruction as well as successful commands. Tests treat any unregistered-type compatibility warning as a failure, preventing permissive fallback. Existing stable CLI errors remain unchanged, and DSNs and credentials remain excluded from output.

## Risks / Trade-offs

- [A future state model is added without allowlisting its custom types] → Keep the list adjacent to harness checkpoint composition and make the strict real-PostgreSQL lifecycle test cover all major stages and gate payloads.
- [Older checkpoints contain a type absent from the new explicit list] → Poll the existing live checkpoint under strict mode before closing the change; add only exact verified TDT types if required.
- [LangGraph changes the public allowlist API] → Pin verification to the frozen compatibility tuple and retain the three-repository candidate matrix.
- [Factory serializer forwarding changes the saver type or lifecycle] → Characterize the public return type and preserve the async context-manager lifetime and `setup()` call order.
- [Dirty worktrees obscure source identity] → Record HEAD, tracked diff hash, and untracked inventory in refreshed verification evidence.

## Migration Plan

1. Add strict-mode regression tests that reproduce permissive warnings and strict fallback behavior across process boundaries.
2. Add the optional allowlist parameter to the shared `agent-core` async factory and unit-test forwarding/setup behavior.
3. Add the exact harness allowlist and pass it at every durable lifecycle call site.
4. Run the focused tests, then the real PostgreSQL lifecycle suite and the full three-repository verification matrix.
5. Re-poll the current live checkpoint with strict mode; leave its human gate untouched.
6. Roll back by reverting the factory parameter and harness registration. No database rollback is required because persisted bytes and schema are unchanged.

## Open Questions

- None. The implementation must discover the complete reachable custom-type set through strict integration tests and keep every allowed entry exact and reviewable.
