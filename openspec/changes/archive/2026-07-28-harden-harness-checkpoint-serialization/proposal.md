## Why

A real cross-process `agent-harness status --json` operation against PostgreSQL currently deserializes harness artifacts only because LangGraph permits unregistered MessagePack types with warnings. LangGraph explicitly announces that this permissive fallback will be blocked in a future version; without an explicit trusted allowlist, the supported durable lifecycle is noisy today and not forward-compatible with that boundary.

## What Changes

- Extend the shared `agent-core` asynchronous PostgreSQL checkpointer boundary to accept an explicit consumer-owned MessagePack type allowlist.
- Register only the exact trusted harness enum and artifact types that can occur in durable checkpoints; do not enable unrestricted deserialization.
- Verify durable run, status, approval/rejection, and report operations in a separate process with strict MessagePack enforcement enabled.
- Add regression coverage proving current checkpoints remain readable without compatibility warnings and JSON output remains isolated on standard output.
- Refresh the three-repository verification evidence after the checkpoint contract changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-harness-runner`: Require durable lifecycle commands to use an explicit trusted checkpoint deserialization allowlist and remain functional under strict MessagePack enforcement.
- `agent-framework-verification`: Require the real PostgreSQL lifecycle gate to exercise strict MessagePack deserialization across operating-system process boundaries and reject warnings or unregistered checkpoint types.

## Impact

- Affected code: `agent-core` shared checkpointer factory and `agent-harness` checkpointer composition/serialization registration.
- Affected operations: `agent-harness run`, `status`, `report`, `approve`, and `reject` when PostgreSQL durability is enabled.
- Dependency API: the existing LangGraph `JsonPlusSerializer(allowed_msgpack_modules=...)` and saver `serde=` public contracts; no new dependency is proposed. The installed `with_allowlist(...)` helper is not used because it deliberately preserves an already-permissive serializer and therefore would not remove normal-mode warnings.
- GitNexus pre-proposal evidence rates `create_async_checkpointer` LOW (no indexed upstream callers) and `WorkflowRunner` LOW (one importing file). `WorkflowRunner._get_graph` is CRITICAL (11 impacted symbols across 9 processes), so the design avoids modifying that method; any later need to touch it requires explicit confirmation and characterization evidence.
- Mobile applications and unrelated TDT services are unaffected.

## Non-goals

- Enabling unrestricted MessagePack module deserialization.
- Changing checkpoint schemas, database migrations, gate authorization, or workflow routing.
- Approving or rejecting the currently paused live run without an explicit human decision.
- Adding dependencies or changing LangGraph version bounds.
