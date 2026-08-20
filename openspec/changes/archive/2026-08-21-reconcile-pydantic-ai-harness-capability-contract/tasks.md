## 1. Contract and provenance

- [x] 1.1 Capture the supplied Task 5 implementation report and identify the stale defaults, vendor-isolation, compaction, guardrail, workspace, and dependency claims; verify the source report exists at `.superpowers/sdd/2026-08-20-pydantic-harness-contract/task-5-report.md`.
- [x] 1.2 Create this correction through the registered OpenSpec CLI change workflow and verify `openspec status --change reconcile-pydantic-ai-harness-capability-contract --json --store openspec-store` resolves the intended store-local change root.
- [x] 1.3 Preserve unrelated active observability work and historical archives; verify with `git status --short` and a final changed-path inventory that no archived task file or active unrelated change is included.

## 2. Public runtime contract

- [x] 2.1 Reconcile `agent-core-capabilities` requirements with implemented AgentRuntime defaults and typed overrides for StepPersistence-adjacent runtime composition, 120,000-token TieredCompaction, GoalReanchor SystemReminders, $5/run and $100/day SpendLimits, opt-in Planning, and model-gated Advisor; verify the complete modified requirement blocks pass strict OpenSpec validation.
- [x] 2.2 Add the `agent-runtime` public runtime-option forwarding contract with explicit-option precedence and no private-agent reconstruction; verify every requirement has WHEN/THEN scenarios and `openspec validate --all --strict --store openspec-store` passes.
- [x] 2.3 Correct `agent-compaction` omitted/defaulted, typed-override, explicit-disablement, and public below/above-target semantics; verify the delta preserves deterministic evidence and does not claim live-provider acceptance.

## 3. Guardrails and workspace policy

- [x] 3.1 Reconcile registry-aware ToolGuardrails with the supplied production registry, exact selectors, containment hooks, approval gates, and read-only behavior; verify against the Task 5 docs-sync focused tests (16 passed as reported).
- [x] 3.2 Add the concrete workspace-root and bounded workspace-relative documentation-root policy, including missing/escaping failure scenarios; verify the delta requires fail-closed construction before model or write-tool execution.

## 4. Vendor and dependency boundaries

- [x] 4.1 Replace the obsolete blanket TC002 vendor-isolation guarantee with the actual public SDK/internal adapter boundary and focused enforcement semantics; verify the reported focused Ruff TC002 command passes without treating the old guarantee as acceptance.
- [x] 4.2 Record that only agent-core directly owns `pydantic-ai-harness[dynamic-workflow]`, while docs-sync and harness retain the base dependency and do not directly declare pydantic-monty or use DynamicWorkflow; verify the requirement distinguishes direct metadata from transitive shared-lock availability.

## 5. CLI validation, archive, and evidence

- [x] 5.1 Validate the authored proposal, five delta capability specs, design, and tasks with `openspec validate --all --strict --store openspec-store`; retain the exit status and pass/fail totals in the correction report.
- [x] 5.2 Run `python3 ~/Developer/openspec-store/scripts/validate-archive-readiness.py --change reconcile-pydantic-ai-harness-capability-contract --json` and verify all tracked tasks are checked and all delta specs are structurally valid.
- [x] 5.3 Archive with `openspec archive --yes --store openspec-store`, allowing the CLI to sync only the declared main specs; verify the dated archive exists and `openspec status` no longer lists the change as active.
- [x] 5.4 Re-run strict validation, `git diff --check`, and raw `git status --short` after archive; verify only CLI-created correction/archive/main-spec paths plus the requested report are eligible for the correction commit and pre-existing observability dirt remains untouched.
- [x] 5.5 Write `.superpowers/sdd/2026-08-20-pydantic-harness-contract/task-correction-report.md` with exact commands, exit statuses, path inventory, archive result, and truthful limitations; explicitly state that no live-provider acceptance was performed.
