# Design: fix-agent-core-hooks-and-token-tracking

## Context

Three bugs discovered during agent-docs-sync feature verification. All fixes are already committed to agent-core.

## Decisions

### D1: Read pydantic-ai's actual attribute names
pydantic-ai v2.31's `RunUsage` uses `input_tokens`/`output_tokens`, not `prompt_tokens`/`completion_tokens`. The hook now reads the correct attributes and maps them for backward-compatible log output.

### D2: Route logs to stderr
`StreamHandler(sys.stdout)` → `StreamHandler(sys.stderr)`. This keeps stdout clean for command output (JSON, text reports) while all log messages go to stderr. Verified: sync stdout now contains only report output.

### D3: Pass deps_type to pydantic-ai Agent
Adding `deps_type=AgentRuntimeDeps` tells pydantic-ai the correct deps type for `RunContext`, eliminating the `'str' object has no attribute 'deps'` error. Type guards added as defensive fallback.

## Risks

- [Log format change] → Log keys remain `prompt_tokens`/`completion_tokens` (backward compatible)
- [deps_type change] → Agent construction gains type safety; no behavioral change for correct usage
