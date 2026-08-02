# Implementation evidence

## Scope completed

- Added the typed `ConsumerRuntimeProfile`, immutable authority policy, and
  composition boundary in `agent-core`.
- Preserved legacy `ConsumerConfig` and `harness_config` through one warning
  adapter, while requiring an explicit gateway or resolver before agent
  construction.
- Passed public capability/toolset instances through runtime construction and
  removed the runtime's private function-toolset dependency.
- Added public state/history access and async checkpointer setup at the
  LangGraph facade boundary.
- Migrated `agent-docs-sync` to a composed runtime profile and structural
  gateway protocol; its dynamic workflow test now uses the public toolset API.
- Added migration documentation and characterization/conformance tests.

## Verification

The following commands passed after the final edits:

```text
agent-core:
  uv run ruff check .
  uv run ruff format --check src tests
  uv run mypy src tests --strict
  uv run pytest -q  (all tests passed)

agent-docs-sync:
  uv run ruff check .
  uv run ruff format --check src tests
  uv run mypy src tests --strict
  uv run pytest -q  (192 passed)
```

GitNexus `detect-changes --repo` reports medium risk for `agent-docs-sync`
and critical risk for `agent-core`; the latter is expected because the
approved `BaseAgent.run`/runtime composition seam is intentionally upstream
of many existing flows.

## Consumer census

Source inspection confirms `agent-docs-sync` and `agent-harness` are the active
framework consumers. `code-daily-scan` is manifest-only, while `ai-review` and
`jira-epic-report` have no direct source imports. The deployment bundle at
`deployments/ai-review/deps/agent-core` is stale and does not yet contain the
new composition module; refreshing that bundle is intentionally still pending.

## Remaining work

Lifecycle hook parity, native deferred/stream end-to-end coverage, spec
round-trip fidelity, generic memory-store migration, framework-version matrix,
Graphify queries, rollback drills, and deployment-bundle refresh remain
follow-up work. They are not represented as complete in the task checklist.
