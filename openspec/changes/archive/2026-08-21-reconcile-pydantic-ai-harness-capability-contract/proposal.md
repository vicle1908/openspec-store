## Why

Task 5 evidence shows that several archived or main OpenSpec requirements no longer describe the implemented pydantic-ai harness contract. The correction is needed now to make the public runtime defaults and override semantics, registry-aware docs-sync guardrails, workspace boundary, dependency extras, and vendor/compaction behavior truthful without rewriting historical archives or claiming live-provider acceptance.

## What Changes

- Correct the `AgentRuntime` capability contract to document implemented process-local defaults and explicit typed overrides: step persistence, tiered compaction, system reminders, and spend limits are defaulted; planning is opt-in; advisor is disabled when no model/capability is supplied; explicit `None` disables the corresponding spend default.
- Specify that public runtime options are forwarded through supported SDK/runtime boundaries, with explicit caller values taking precedence over defaults and no private-agent reconstruction.
- Clarify that docs-sync ToolGuardrails are built from the supplied production registry and exact registered tool selectors, and that write-capable construction requires a concrete workspace root plus at least one bounded workspace-relative documentation root.
- Replace the vendor-isolation TC002 guarantee with the actual public-module boundary, and record the direct dependency/optional-extra boundary for `agent-core`, `agent-docs-sync`, and `agent-harness`.
- Correct compaction semantics so omitted compaction receives the `AgentRuntime` default while a supplied typed capability preserves its target and strategy order; retain truthful public below/above-target verification requirements.
- Add deterministic evidence and limitations to the implementation record; this change does not establish live-provider, network, or clean-install acceptance for the consumer repositories.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-core-capabilities`: Correct default capability composition, typed overrides, and public configuration-boundary requirements.
- `agent-runtime`: Define public runtime-option forwarding and explicit override precedence.
- `agent-guardrails`: Define registry-aware docs-sync guardrails and the concrete workspace-root policy.
- `vendor-isolation`: Replace the obsolete TC002 confinement guarantee with the actual import and dependency/extra boundaries.
- `agent-compaction`: Correct omitted-versus-explicit compaction behavior and public verification semantics.

## Impact

The change updates only OpenSpec delta artifacts and, through CLI archive sync, the five corresponding main capability specs in `openspec-store`. It records behavior implemented across `agent-core`, `agent-docs-sync`, and `agent-harness`; no product source, lockfile, archived task file, active unrelated change, provider credential, or live service is changed.
