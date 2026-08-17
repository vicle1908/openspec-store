## Why

The agent ecosystem currently conflates model-free commands with model-backed composition, permits one consumer to downgrade failed canonical mapping, and relies on archived live evidence that does not exercise the required installed public transactions. This change establishes one current contract and makes completion depend on truthful command classification, present implementation and documentation, exact integrated provenance, and fresh evidence through the two real consumer boundaries.

## What Changes

- **BREAKING** Remove the remaining legacy-only LLM schema and `api_mode` migration requirements from the current provider-profile contract; canonical `providers` / `models` / `defaults` input is the only supported LLM schema.
- **BREAKING** Require `ai-review` to determine its enabled native reviewer set before canonical projection and validate every enabled native mapping before constructing any native reviewer; mapping failure cannot silently downgrade to codescan-only, while a genuinely codescan-only review remains model-free.
- Classify public operations explicitly. Harness `status`/`report` and docs-sync standalone commands remain model-free; harness `run`/graph continuation and docs-sync generation-capable operations use one captured process-local model-construction context.
- Require read-only retained checkpoint/approval-state access before identity comparison where necessary, then fail closed before model construction, graph/state advancement, approval consumption, artifact mutation, or write-capable resource construction until retained/current identity, containment, and authority agree.
- Affirm the required live matrix as exactly one installed `ai-harness-skills` transaction and one installed `ai-review review ...` transaction with structured reviewer outcomes.
- Define target preservation as an allowlisted managed-output envelope plus unchanged protected surfaces.
- Use one parameterized comparison engine with `historical` and `current_reuse` tags.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `provider-model-profile-resolution`: remove legacy-only schema acceptance and inference
- `agent-harness-runner`: keep harness domain configuration model-free
- `agent-docs-sync`: classify model-free and model-backed commands
- `cli-provider-profile-resolution`: strengthen fail-closed consumer projection

## Impact

### Ownership boundaries

- `openspec-store`: owns this proposal, four delta specs, correction design/tasks
- `tdt-core`: owns canonical schema validation and transport documentation
- `agent-core`: owns public construction examples and documentation
- `agent-harness`: owns model-free harness configuration and tests
- `agent-docs-sync`: owns model-free domain configuration and tests
- `ai-harness-skills`: owns the installed `harness start` → `harness run --run <id>` live row
- `ai-review`: owns fail-closed canonical projection and structured results

### Non-goals

- Do not edit archived changes or rewrite their retained evidence.
- Do not reintroduce a compatibility phase or legacy schema.
- Do not change credential values or modify native provider authentication state.
- Do not absorb unrelated pre-existing lint/format cleanup.
