# Task 5 report: harness contract documentation and archive evidence

Date: 2026-08-21
Scope: `agent-core`, `agent-docs-sync`, `agent-harness`, and the registered
`openspec-store` checkout.

## Result

The product documentation now describes the implemented runtime contract:
automatic defaults versus explicit overrides/disablement, public runtime
options, registry-aware docs-sync ToolGuardrails, the workspace-root boundary,
and the actual `dynamic-workflow` dependency/use boundary. The OpenSpec store
was validated before and after the documentation changes with
`openspec validate --all --strict`: 374 passed, 0 failed.

## Evidence captured

Pre-change stale-reference search:

```text
rg -n -i --glob 'CHANGELOG.md' --glob 'docs/*.md' ... \
  'automatic|default|None|disabled|vendor|pydantic|dynamic[-_ ]workflow|workspace[- ]root|ToolGuardrails|guardrail|capabilit|runtime option|provider|live' \
  agent-core agent-docs-sync agent-harness openspec/specs/vendor-isolation \
  openspec/specs/agent-compaction ...
exit 0; findings included stale dynamic-workflow claims, historical default
claims, the vendor-isolation TC002 guarantee, and archived task evidence.
```

Pre-change and post-change OpenSpec validation:

```text
openspec validate --all --strict
Totals: 374 passed, 0 failed (both runs)
```

Focused behavior tests:

| Repository | Command | Result |
|---|---|---|
| `agent-core` | `uv run pytest -q tests/_ai/test_harness_capabilities.py tests/sdk/test_agents.py tests/test_harness_features_integration.py` | 64 passed |
| `agent-docs-sync` | `uv run pytest -q tests/test_agent_factory_guardrails.py tests/test_dependency_baseline.py` | 16 passed |
| `agent-harness` | `uv run pytest -q tests/test_stage_classification.py tests/test_cli_lifecycle.py` | 27 passed |
| `agent-core` | `uv run ruff check --select TC002 src/agent_core/agent_base/agent.py src/agent_core/sdk/agents.py src/agent_core/sdk/composition.py` | passed, demonstrating TC002 does not enforce the old vendor-isolation claim |
| all edited documentation | `git diff --check` | passed |

Runtime probes:

1. `agent-core` constructed `AgentRuntime(model=TestModel(), tools=[])` and
   observed automatic `StepPersistence`, `TieredCompaction`,
   `SystemReminders`, and `SpendLimits` capabilities. The probe exited 0.
2. `agent-docs-sync` constructed the public `build_doc_sync_agent()` in
   `generate` mode with an explicit workspace and `allowed_doc_roots=['docs/']`.
   It observed `write-file-path-guard`, `shell-command-guard`, and
   `result-secret-redaction` ToolGuardrails. The probe exited 0.

The first docs-sync probe attempted the nonexistent `create_agent` symbol and
exited with `ImportError`; it was immediately corrected to the public
`build_doc_sync_agent` factory above and is not used as acceptance evidence.

## Documentation changes

Committed documentation changes are limited to:

- `agent-core/CHANGELOG.md`
- `agent-core/docs/harness-integration.md`
- `agent-core/docs/framework-integration.md`
- `agent-docs-sync/docs/framework-integration.md`
- `agent-harness/CHANGELOG.md`

The updates state that agent-core defaults are process-local step persistence,
120,000-token tiered compaction, GoalReanchor system reminders, and $5/run plus
$100/day spend limits; `None` disables each spend default, planning is opt-in,
and advisor is disabled by `None`/an absent model. They also state that
ToolGuardrails are registry-scoped in docs-sync write-capable modes and that
write policy requires a concrete workspace root plus at least one bounded,
workspace-relative documentation root.

Dependency reality is recorded explicitly: only agent-core directly declares
`pydantic-ai-harness[dynamic-workflow]`; docs-sync and agent-harness declare
`pydantic-ai-harness` without that extra, do not directly declare
`pydantic-monty`, and do not import/use `DynamicWorkflow`. A shared lock can
contain the optional dependency through editable agent-core without changing
the docs-sync or harness public contract.

## OpenSpec provenance decision

The requested OpenSpec targets were intentionally not hand-edited:

- `openspec/specs/vendor-isolation/spec.md`
- `openspec/specs/agent-compaction/spec.md`
- `openspec/changes/archive/2026-08-20-upgrade-harness-23/tasks.md`
- `openspec/changes/archive/2026-08-20-integrate-harness-features/tasks.md`

The supported CLI exposes creation, validation, sync-through-archive, and
archive operations, but no operation to revise an already archived task file or
merge an arbitrary correction into a main spec. The store currently has only
the unrelated active changes `align-jti-skill-runtime-contract` and
`establish-agent-observability-contract`; mutating either would violate change
ownership. Per the task instruction not to hand-edit files under
`openspec/`, this report is the concrete evidence artifact for a future
CLI-managed correction change.

The correction change should update vendor-isolation to describe the public SDK
modules that intentionally expose runtime pydantic-ai types and should replace
the unachievable TC002 lint guarantee. It should update agent-compaction to say
that omitted compaction receives the AgentRuntime default while a supplied
typed capability overrides it. Archived task evidence should be recaptured and
updated only through the correction change/archive workflow; historical broad
test counts and live-provider claims must not be reasserted from this focused
evidence.

## Preservation and commit scope

Pre-edit identities were:

| Repository | Branch/HEAD before edits | Pre-existing unrelated dirt |
|---|---|---|
| `openspec-store` | `main` / `790be378bb868fe916bc5920c83b51b7d24b56b8` | staged edits under `openspec/changes/establish-agent-observability-contract/` |
| `agent-core` | `main` / `2a560ddfb51ee984c9d93e15a187ccd4623298b9` | generated `graphify-out/` plus observability source/tests |
| `agent-docs-sync` | `main` / `9c78670fc2ac3544d142fbb68fb0110d8b28818d` | generated `graphify-out/` plus observability source/tests |
| `agent-harness` | `main` / `25f1dd14b433b1c376227e87a9f991f0d714c8e2` | generated `graphify-out/` |

Only the five documentation paths listed above and this report are intended
for the Task 5 commits. No product source, lockfile, generated graph, or
unrelated OpenSpec change was staged.
