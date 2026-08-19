# Proposal: Add Evaluation Datasets for Agent Quality

## Why

The `evaluation` spec defines 5 requirements for workflow quality evaluation with `pydantic-evals` (MaxDuration, ToolCorrectness, CostScorer, RegressionScorer, LLMJudge), but no actual evaluation datasets exist. The framework is wired — `agent_core/observability/scorers/` exports all evaluators — but without datasets, there are no quality signals. We cannot measure whether agent changes improve or regress quality.

## What Changes

1. Create evaluation dataset fixtures under `agent_core/evaluation/datasets/` using real patterns from existing test fixtures
2. Add a `run_eval` CLI command to `agent-core` that runs the evaluation pipeline
3. Add dataset schema definitions to the `evaluation` spec
4. Base datasets on actual agent workflows: Jira triage, code review, docs sync

## Scope

- `agent_core/evaluation/` — new dataset directory and runner
- `openspec/specs/evaluation/spec.md` — MODIFIED: add dataset structure requirement
- Test fixtures only — no production data exposure

## Out of Scope

- External benchmark submission (SWE-bench, GAIA)
- Real-time production evaluation (future)
- Cost model training
