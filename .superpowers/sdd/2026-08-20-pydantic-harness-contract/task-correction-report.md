# Task correction report: reconcile pydantic-ai harness capability contract

Date: 2026-08-21
Repository: `/Users/androidteam/Developer/openspec-store`
Change: `reconcile-pydantic-ai-harness-capability-contract`

## Result

The approved Task 5 correction was created with the registered OpenSpec CLI,
validated, archived with `openspec archive --yes`, and synced into the five
declared main capability specs. The dated archive is:

`openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/`

The correction records the now-implemented public contract for AgentRuntime
defaults and typed overrides, public runtime-option forwarding,
registry-aware docs-sync ToolGuardrails, explicit workspace-root policy,
dependency/optional-extra ownership, and corrected vendor-isolation and
compaction semantics.

## CLI lifecycle evidence

The store was selected explicitly with `openspec store list --json`; it resolved
`openspec-store` to `/Users/androidteam/Developer/openspec-store`.

```text
openspec new change "reconcile-pydantic-ai-harness-capability-contract" --store openspec-store
exit 0
created openspec/changes/reconcile-pydantic-ai-harness-capability-contract/
schema: spec-driven
```

The pre-archive status graph reported proposal, specs, design, and tasks as
`done`; the change was planning-complete and implementation-complete. The
archive-readiness validator reported:

```text
python3 ~/Developer/openspec-store/scripts/validate-archive-readiness.py \
  --change reconcile-pydantic-ai-harness-capability-contract --json
exit 0
status: ready
tasks: 15 total, 15 completed, 0 remaining
artifacts: proposal/design/tasks found
delta_specs_count: 5
warnings: []
```

The first full strict validation caught five omitted legacy scenario names in
wholesale `MODIFIED` requirement blocks and exited non-zero (`374 passed, 1
failed`). Those blocks were repaired to retain every prior scenario label with
corrected semantics. The reruns then passed:

```text
openspec validate reconcile-pydantic-ai-harness-capability-contract --type change --strict --store openspec-store
exit 0: change is valid

openspec validate --all --strict --store openspec-store
exit 0: Totals: 375 passed, 0 failed (375 items)
```

The requested archive operation completed through the CLI:

```text
openspec archive reconcile-pydantic-ai-harness-capability-contract --yes --store openspec-store
exit 0
specs updated successfully
agent-compaction: update
agent-core-capabilities: update
agent-guardrails: update
agent-runtime: update
vendor-isolation: update
totals: +3, ~10, -0, renamed 0
archived as 2026-08-21-reconcile-pydantic-ai-harness-capability-contract
```

The only archive warning was non-blocking: the proposal contains more than ten
delta operations. No incomplete task warning was emitted.

Post-archive checks passed:

```text
openspec list --json --store openspec-store
exit 0: active changes remain only establish-agent-observability-contract and align-jti-skill-runtime-contract

openspec validate --all --strict --store openspec-store
exit 0: Totals: 374 passed, 0 failed (374 items)

git diff --check
exit 0
```

## Changed-path and preservation evidence

The repository was on `main` at immutable pre-edit HEAD
`72b701abfc4ea5cee9246635b5715bffd432cdad`. Before this correction, the raw
status contained only the two staged files belonging to the pre-existing
`establish-agent-observability-contract` change:

```text
M  openspec/changes/establish-agent-observability-contract/design.md
M  openspec/changes/establish-agent-observability-contract/tasks.md
```

Those paths were not edited, staged, or included in the correction commit.
The CLI-created correction paths are:

```text
openspec/specs/agent-compaction/spec.md
openspec/specs/agent-core-capabilities/spec.md
openspec/specs/agent-guardrails/spec.md
openspec/specs/agent-runtime/spec.md
openspec/specs/vendor-isolation/spec.md
openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/.openspec.yaml
openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/design.md
openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/proposal.md
openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/specs/agent-compaction/spec.md
openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/specs/agent-core-capabilities/spec.md
openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/specs/agent-guardrails/spec.md
openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/specs/agent-runtime/spec.md
openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/specs/vendor-isolation/spec.md
openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/tasks.md
```

The requested report is the sole additional non-CLI evidence path:

`.superpowers/sdd/2026-08-20-pydantic-harness-contract/task-correction-report.md`

## Supplied implementation evidence

The source evidence was
`.superpowers/sdd/2026-08-20-pydantic-harness-contract/task-5-report.md`.
It records the following deterministic focused results:

| Repository | Command/result |
|---|---|
| `agent-core` | `uv run pytest -q tests/_ai/test_harness_capabilities.py tests/sdk/test_agents.py tests/test_harness_features_integration.py` — 64 passed |
| `agent-docs-sync` | `uv run pytest -q tests/test_agent_factory_guardrails.py tests/test_dependency_baseline.py` — 16 passed |
| `agent-harness` | `uv run pytest -q tests/test_stage_classification.py tests/test_cli_lifecycle.py` — 27 passed |
| `agent-core` | focused Ruff `TC002` check on `agent.py`, `agents.py`, and `composition.py` — passed |
| edited documentation | `git diff --check` — passed |

The report also records two local public-boundary probes: construction of
`AgentRuntime(model=TestModel(), tools=[])` observed the documented default
capabilities, and public `build_doc_sync_agent()` generation construction
observed the registry guardrails. An initial exploratory probe attempted a
nonexistent `create_agent` symbol and exited with `ImportError`; it was
corrected to the public factory and is not treated as acceptance evidence.

## Limitations

This is a deterministic contract/spec correction, not a fresh integrated
runtime acceptance run. It does not claim live-provider or external-network
acceptance, clean-install dependency resolution, durable cross-process harness
acceptance, full ecosystem test-suite readiness, or provider credential
validity. Shared-lock presence of an optional dependency remains distinct from
direct package ownership. Historical archived task files and unrelated active
OpenSpec changes were intentionally not edited.
