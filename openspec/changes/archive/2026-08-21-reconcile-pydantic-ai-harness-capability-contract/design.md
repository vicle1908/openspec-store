## Context

This is a corrective documentation/specification change for the contract already implemented in the three consumer repositories. Task 5's report records deterministic focused tests and two local public-boundary probes, while also recording that no live provider acceptance was performed. The existing store contains stale requirements that describe capability omission as disabled, require blanket TC002 import confinement, and omit the production registry/workspace and dependency-extra boundaries.

The change is store-local and must not rewrite archived task evidence, alter the active observability change, or modify product source. The CLI archive is the transaction boundary: it validates the delta artifacts, syncs the selected main specs, and moves the completed change into the dated archive.

## Goals / Non-Goals

**Goals:**

- Make the public `AgentRuntime` default and override behavior explicit and consistent across the capability and compaction specs.
- Describe public runtime-option forwarding as an observable SDK boundary with explicit options taking precedence over defaults.
- Make docs-sync guardrail composition registry-aware and require an explicit workspace root plus bounded workspace-relative documentation roots.
- Replace the obsolete vendor-isolation lint promise with the actual public/internal import boundary and record direct dependency/extra ownership.
- Preserve deterministic evidence commands, current repository identities, and limitations in the correction report.
- Use only OpenSpec CLI lifecycle operations for creation, validation, spec sync, and archive.

**Non-Goals:**

- No product-code, dependency-lock, archived-history, credential, provider, network, or deployment changes.
- No claim of live-provider, external-service, clean-install, or full cross-repository acceptance from focused local evidence.
- No edits to `openspec/changes/archive/` or to either existing active change.
- No attempt to make optional dependencies transitively present in a shared lock equivalent to a direct consumer dependency.

## Decisions

### 1. Modify existing capability paths rather than create a parallel contract

The proposal names the existing `agent-core-capabilities`, `agent-runtime`,
`agent-guardrails`, `vendor-isolation`, and `agent-compaction` paths. Their
delta files copy complete modified requirement blocks and add only the new
observable boundaries. This lets `openspec archive --yes` merge into the
canonical main specs and avoids a duplicate correction capability.

Alternative considered: adding a new umbrella capability would leave the
contradictory requirements active and would not correct consumers that resolve
the existing paths.

### 2. Model omitted values and explicit values separately

The runtime contract treats omission as documented defaulting, while an
explicit typed capability or supported disablement is an override. Defaults are
stated as process-local capability composition: 120,000-token tiered
compaction, GoalReanchor system reminders, and $5/run plus $100/day spend
limits; planning remains opt-in and advisor requires a usable explicit model.
The specs avoid implying that a missing model can be fabricated or that global
provider precedence is reopened.

Alternative considered: preserving the old omission-means-disabled wording was
rejected because it contradicts the current public `AgentRuntime` probe and
the documented implementation behavior.

### 3. Treat the supplied registry and workspace as security boundaries

Docs-sync guardrails are specified as projections of the production registry,
not an independently constructed list. Write-capable construction requires a
concrete workspace root and bounded relative documentation root before model or
write-tool execution. Existing containment, approval, audit, and redaction
layers remain authoritative; the ToolGuardrail does not duplicate path
normalization.

Alternative considered: allowing a default current working directory or a
guardrail-owned registry was rejected because either can widen write authority
and diverge from the production tool identities.

### 4. Record dependency provenance separately from environment availability

The vendor delta states that only agent-core directly declares
`pydantic-ai-harness[dynamic-workflow]`; docs-sync and harness use the base
package and do not directly declare `pydantic-monty` or use `DynamicWorkflow`.
A shared lock may still contain the optional dependency transitively, but that
does not alter a consumer's public contract.

Alternative considered: documenting whatever happens to be installed in the
shared environment was rejected because it would confuse transitive lock
availability with package ownership.

### 5. Use bounded deterministic evidence and preserve limitations

Evidence is derived from the supplied Task 5 report: strict OpenSpec
validation, focused repository tests, a focused TC002 check, `git diff --check`,
and two local public-boundary probes. The report explicitly records and
preserves the initial failed probe using the nonexistent `create_agent` symbol
as a corrected exploratory attempt, not acceptance evidence. No live provider
call is required or claimed.

## Risks / Trade-offs

- [Risk] Main specs could be merged while unrelated dirty work is accidentally included. → Use the CLI's change-scoped archive operation, capture pre/post status, and verify the final diff path inventory before committing.
- [Risk] A delta could silently omit an existing scenario. → Include complete modified requirement blocks and run strict validation before archive.
- [Risk] Focused tests may overstate ecosystem readiness. → Label them deterministic/focused and retain explicit non-live limitations in the correction report.
- [Risk] Existing active changes could be changed by broad cleanup. → Do not stage or edit them; compare changed paths against the pre-edit dirty inventory.
- [Risk] Archive sync could target a wrong capability path. → Use `artifactPaths.specs.existingOutputPaths` from CLI status and inspect each corresponding main spec after sync.

## Migration Plan

1. Create the named change with `openspec new change` using the registered `openspec-store` ID.
2. Author proposal, delta specs, design, and all-checked tasks in the new change directory only.
3. Run strict validation and archive-readiness validation; repair only the new artifacts if either reports a defect.
4. Run `openspec archive --yes --store openspec-store` so the CLI syncs the five main specs and archives the change under the current date.
5. Re-run strict validation and inspect `git status --short`, `git diff --name-status`, and the archived artifact paths.
6. Commit only the CLI-created correction/archive/main-spec files plus the requested correction report; leave pre-existing observability changes unstaged.

Rollback is a repository-level revert of this correction commit after review.
Do not manually move archive directories, edit archived tasks, or reset/clean
the worktree as part of rollback.

## Verification and Limitations

Deterministic commands recorded for this correction are:

```bash
openspec validate --all --strict --store openspec-store
python3 ~/Developer/openspec-store/scripts/validate-archive-readiness.py \
  --change reconcile-pydantic-ai-harness-capability-contract --json
git diff --check
```

The supplied implementation evidence additionally records focused commands:

```text
agent-core: uv run pytest -q tests/_ai/test_harness_capabilities.py tests/sdk/test_agents.py tests/test_harness_features_integration.py  # 64 passed
agent-docs-sync: uv run pytest -q tests/test_agent_factory_guardrails.py tests/test_dependency_baseline.py  # 16 passed
agent-harness: uv run pytest -q tests/test_stage_classification.py tests/test_cli_lifecycle.py  # 27 passed
agent-core: uv run ruff check --select TC002 src/agent_core/agent_base/agent.py src/agent_core/sdk/agents.py src/agent_core/sdk/composition.py  # passed
```

These results are focused deterministic evidence only. They do not establish
live-provider acceptance, external network behavior, clean-install dependency
resolution, durable cross-process harness acceptance, or full integrated
consumer readiness.

## Open Questions

None. Provider and clean-install evidence are intentionally limitations of this
correction, not unresolved design decisions.
