# Public Interface Inventory: agent-harness

## CLI Commands

| Command | Entry Point | Args | Options |
|---------|-------------|------|---------|
| `run` | `cli.py:run()` | ticket | --repo, --config, --json |
| `status` | `cli.py:status()` | run | --json |
| `report` | `cli.py:report()` | run | --json |
| `approve` | `cli.py:approve()` | run, stage, decision_id | --reason |
| `reject` | `cli.py:reject()` | run, stage, decision_id, reason | --backtrack |

## Public Import Paths

| Module | Symbol | Type | Used By |
|--------|--------|------|---------|
| `agent_harness.cli` | `app` | Typer | Entry point |
| `agent_harness.cli` | `main` | Function | Entry point |
| `agent_harness.config` | `HarnessConfig` | Class | cli, runner, factory |
| `agent_harness.config` | `GateConfig` | Class | config |
| `agent_harness.config` | `ValidationConfig` | Class | config |
| `agent_harness.config` | `PersistenceConfig` | Class | config |
| `agent_harness.config` | `BudgetConfig` | Class | config |
| `agent_harness.config` | `RetentionConfig` | Class | config |
| `agent_harness.config` | `AuthorityConfig` | Class | config |
| `agent_harness.workflow.runner` | `WorkflowRunner` | Class | cli |
| `agent_harness.workflow.graph` | `build_graph` | Function | runner |
| `agent_harness.agents.factory` | `create_stage_agent` | Function | (unused) |
| `agent_harness.agents.factory` | `create_gitnexus_tools` | Function | (unused) |
| `agent_harness.agents.factory` | `create_graphify_tools` | Function | (unused) |
| `agent_harness.agents.factory` | `create_file_tools` | Function | (unused) |
| `agent_harness.state` | `HarnessState` | TypedDict | graph, runner, stages |
| `agent_harness.state` | `WorkflowStatus` | Enum | state, graph |
| `agent_harness.state` | `create_initial_state` | Function | runner |
| `agent_harness.state` | `STAGE_STATE_MAP` | Dict | (unused) |
| `agent_harness.models.artifacts` | `Stage` | Enum | all stages, gates |
| `agent_harness.models.artifacts` | `ValidationStatus` | Enum | validation |
| `agent_harness.models.artifacts` | `ArtifactEnvelope` | Class | all artifacts |
| `agent_harness.models.artifacts` | `TicketArtifact` | Class | intake |
| `agent_harness.models.artifacts` | `ContextArtifact` | Class | context |
| `agent_harness.models.artifacts` | `Requirement` | Class | clarify |
| `agent_harness.models.artifacts` | `ClarifyArtifact` | Class | clarify |
| `agent_harness.models.artifacts` | `DraftSpec` | Class | spec |
| `agent_harness.models.artifacts` | `ImpactArtifact` | Class | impact |
| `agent_harness.models.artifacts` | `DesignArtifact` | Class | design |
| `agent_harness.models.artifacts` | `APIContractArtifact` | Class | api_contract |
| `agent_harness.models.artifacts` | `ImplementationPlanArtifact` | Class | implementation_plan |
| `agent_harness.models.artifacts` | `CodingPlanArtifact` | Class | coding_plan |
| `agent_harness.models.artifacts` | `PlanReviewArtifact` | Class | plan_review |
| `agent_harness.models.artifacts` | `TestPlanArtifact` | Class | test_plan |
| `agent_harness.models.artifacts` | `VerificationArtifact` | Class | verification |
| `agent_harness.models.gates` | `GateRequest` | Class | graph, gates |
| `agent_harness.models.gates` | `GateDecision` | Class | cli, gates |
| `agent_harness.models.gates` | `GateDecisionType` | Enum | cli, gates |
| `agent_harness.models.trace` | `TraceEntry` | Class | state |
| `agent_harness.models.evidence` | `Evidence` | TypeAlias | validation |
| `agent_harness.models.evidence` | `GitNexusEvidence` | Class | evidence |
| `agent_harness.models.evidence` | `GraphifyEvidence` | Class | evidence |
| `agent_harness.models.evidence` | `FileEvidence` | Class | evidence |
| `agent_harness.models.evidence` | `ValidationEvidence` | Class | validation |
| `agent_harness.models.evidence` | `Freshness` | Enum | evidence |
| `agent_harness.models.evidence` | `EvidenceType` | Enum | evidence |
| `agent_harness.validation.pipeline` | `run_validation` | Function | graph |
| `agent_harness.validation.existence` | `validate_existence` | Function | pipeline |
| `agent_harness.validation.semantic` | `validate_semantic` | Function | pipeline |
| `agent_harness.validation.structural` | `validate_structural` | Function | pipeline |
| `agent_harness.tools.gitnexus` | `GitNexusTool` | Class | factory |
| `agent_harness.tools.graphify` | `GraphifyTool` | Class | factory |
| `agent_harness.tools.files` | `FileTools` | Class | factory |
| `agent_harness.tools.jira` | `JiraTool` | Class | (unused) |
| `agent_harness.artifacts.store` | `ArtifactStore` | Class | (unused) |
| `agent_harness.workspace` | `WorkspaceResolver` | Class | (unused) |

## Checkpoint State Fields

| Field | Type | Reducer | Current Issue |
|-------|------|---------|---------------|
| `run_id` | str | none | OK |
| `ticket_id` | str | none | OK |
| `workspace_repos` | list[str] | add_messages | WRONG (should be list_append) |
| `current_stage` | Stage | none | OK |
| `status` | WorkflowStatus | none | OK |
| `errors` | list[str] | add_messages | WRONG (should be list_append) |
| `artifact_*` (12) | Artifact | none | OK |
| `trace` | list[TraceEntry] | _append_trace | OK |
| `revision_*` (12) | int | none | OK |
| `pending_gate` | GateRequest | none | OK |
| `gate_history` | list[str] | add_messages | WRONG (should be list_append) |
| `evidence` | dict | _merge_artifacts | OK |
| `started_at` | str | none | OK |
| `completed_at` | str | none | OK |
| `correlation_id` | str | none | OK |

## Configuration Keys

| Section | Keys | Source |
|---------|------|--------|
| `harness` | consumer_name, consumer_version | config.py |
| `gate` | interrupt_stages, auto_approve_stages, decision_expiry_seconds, allowed_transports | config.py |
| `validation` | max_revisions, confidence_threshold, require_evidence_for_symbols, require_evidence_for_files | config.py |
| `persistence` | durable, postgres_url | config.py |
| `budget` | max_model_requests_per_stage, max_tokens_per_stage, max_total_tokens, max_query_fanout | config.py |
| `retention` | artifact_retention_days | config.py |
| `authority` | artifact_root, read_only_targets, allowed_shell, allowed_code_execution, allowed_external_mutation, allowed_source_write | config.py |

## Stage Order

| # | Stage | Auto-Approve | Gate |
|---|-------|--------------|------|
| 1 | INTAKE | ✓ | — |
| 2 | CONTEXT | ✓ | — |
| 3 | CLARIFY | ✓ | — |
| 4 | SPEC | — | ✓ |
| 5 | IMPACT | — | — |
| 6 | DESIGN | — | ✓ |
| 7 | API_CONTRACT | — | — |
| 8 | IMPLEMENTATION_PLAN | — | ✓ |
| 9 | CODING_PLAN | — | — |
| 10 | PLAN_REVIEW | — | ✓ |
| 11 | TEST_PLAN | — | — |
| 12 | VERIFICATION | — | — |

## Gate Configuration

| Gate Stage | Decision ID Format | Backtrack Allowed |
|------------|-------------------|-------------------|
| SPEC | gate-spec-{run_id[:8]} | Yes (to INTAKE, CONTEXT, CLARIFY) |
| DESIGN | gate-design-{run_id[:8]} | Yes (to CLARIFY, SPEC, IMPACT) |
| IMPLEMENTATION_PLAN | gate-implementation_plan-{run_id[:8]} | Yes (to SPEC, IMPACT, DESIGN) |
| PLAN_REVIEW | gate-plan_review-{run_id[:8]} | Yes (to IMPLEMENTATION_PLAN, CODING_PLAN) |

## Known Defects

1. **Missing gateway**: `create_stage_agent` calls `build_agent` without gateway
2. **Shared gate node**: Single gate has edges to all 4 gated stages (fan-out bug)
3. **Wrong reducers**: `workspace_repos`, `errors`, `gate_history` use message reducer
4. **Missing checkpoint**: `astream` and `resume` compile without checkpointer
5. **No saver setup**: Postgres saver not initialized through setup()
6. **Missing expiry**: GateRequest missing expiry field
