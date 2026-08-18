# Agent Docs Sync Observability Specification

## Purpose

Define observability for docs-sync: OpenTelemetry tracing, Langfuse integration, cost/quality scoring, and structured audit trails for documentation generation and validation operations.

## Requirements

### Requirement: Pipeline nodes emit OTel spans
Each WorkflowBuilder node handler SHALL wrap its execution in an OTel span via `agent_core.foundation.tracing.get_tracer()`. The span name SHALL be `docs_sync.{node_name}` (e.g., `docs_sync.discover`, `docs_sync.audit`). Span attributes SHALL include `repo_root`, `node_name`, and `iteration`.

#### Scenario: Discover node emits span
- **WHEN** the discover node executes
- **THEN** an OTel span named `docs_sync.discover` is created with attribute `repo_root` set to the repository path

#### Scenario: Generate node emits span with LLM attributes
- **WHEN** the generate node executes and calls the LLM
- **THEN** the span contains `gen_ai.request.model`, `gen_ai.usage.total_tokens`, and `gen_ai.usage.cost_usd` attributes from the model provider

### Requirement: Langfuse trace integration
The doc-sync agent SHALL register `langfuse_hooks` from `agent_core.agent_base.hooks.builtins` in its HookRegistry. After each agent run, a Langfuse trace SHALL be recorded with `success` and `duration_ms` scores.

#### Scenario: Successful generation run recorded in Langfuse
- **WHEN** a doc generation agent run completes successfully
- **THEN** a Langfuse trace is created with `success=1.0` and `duration_ms` score

#### Scenario: Failed generation run recorded in Langfuse
- **WHEN** a doc generation agent run fails
- **THEN** a Langfuse trace is created with `success=0.0`

### Requirement: Cost tracking per run
The doc-sync agent SHALL use the `tdt-budget-enforcement` hook from `agent_core._ai.hooks` to record token usage. Each agent run SHALL emit a structured log entry with `input_tokens` (mapped from pydantic-ai's `RunUsage.input_tokens`), `output_tokens` (mapped from `RunUsage.output_tokens`), and estimated cost computed from token counts and provider-specific rates.

#### Scenario: Cost recorded after generation
- **WHEN** a doc generation agent completes
- **THEN** the hook SHALL emit a `budget_usage_estimated` structured log entry containing `prompt_tokens` and `completion_tokens` (mapped from pydantic-ai's `input_tokens` and `output_tokens`) with non-zero values when LLM calls were made

### Requirement: Doc generation cost scorer
A `DocGenerationCostScorer` SHALL be implemented using `agent_core.observability.scorers`. It SHALL score runs based on cost-per-document-generated ratio. Scoring: cost_per_doc < $0.01 → 1.0, < $0.05 → 0.8, < $0.20 → 0.5, >= $0.20 → 0.2.

#### Scenario: Low cost per doc scores high
- **WHEN** a run generates 10 documents at total cost $0.05
- **THEN** the cost scorer returns 1.0

#### Scenario: High cost per doc scores low
- **WHEN** a run generates 1 document at total cost $0.50
- **THEN** the cost scorer returns 0.2

### Requirement: Doc quality scorer
A `DocQualityScorer` SHALL be implemented using `agent_core.observability.scorers`. It SHALL score runs based on the Diátaxis compliance rate from validation results. Score = (valid_docs / total_docs). If no docs validated, score is 0.0.

#### Scenario: All docs pass validation
- **WHEN** validation finds 10/10 docs compliant with Diátaxis rules
- **THEN** the quality scorer returns 1.0

#### Scenario: Half docs fail validation
- **WHEN** validation finds 5/10 docs compliant
- **THEN** the quality scorer returns 0.5
