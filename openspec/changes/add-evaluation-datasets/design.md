# Design: Add Evaluation Datasets

## Problem

The evaluation framework exists but has no data. `pydantic-evals` is a dependency, scorers are implemented, but there are zero dataset files to run against.

## Approach

### 1. Dataset structure

Each dataset is a `pydantic_evals.Dataset[InputType, OutputType]` with cases:

```python
# agent_core/evaluation/datasets/jira_triage.py
from pydantic_evals import Dataset

class TriageInput(BaseModel):
    ticket_summary: str
    ticket_description: str
    project_key: str

class TriageOutput(BaseModel):
    classification: str
    priority: str
    assignee_hint: str | None

triage_dataset = Dataset[TriageInput, TriageOutput](name="jira-triage")
triage_dataset.add_case(
    id="basic-triage",
    input=TriageInput(ticket_summary="Login fails on mobile", ...),
    metadata={"expected_class": "bug", "expected_priority": "high"},
)
```

### 2. Three dataset types (from existing test patterns)

| Dataset | Source | Cases | Evaluators |
|---------|--------|-------|------------|
| `jira_triage` | agent-harness intake stage patterns | 5 | ToolCorrectness, LLMJudge |
| `code_review` | ai-review MR review patterns | 5 | MaxDuration(120), CostScorer, RegressionScorer |
| `docs_sync` | agent-docs-sync patterns | 3 | MaxDuration(60), ArtifactCompleteness |

### 3. CLI integration

Add `agent-core eval run --dataset jira_triage` command using existing `agent_core/evaluation/runner.py`.

### 4. Spec delta

Add dataset structure requirement to `evaluation` spec.

## Files Changed

| File | Change |
|------|--------|
| `agent_core/evaluation/datasets/__init__.py` | NEW: dataset registry |
| `agent_core/evaluation/datasets/jira_triage.py` | NEW: 5 cases |
| `agent_core/evaluation/datasets/code_review.py` | NEW: 5 cases |
| `agent_core/evaluation/datasets/docs_sync.py` | NEW: 3 cases |
| `openspec/specs/evaluation/spec.md` | MODIFIED: dataset requirement |

## Testing

- `uv run pytest tests/ -k eval` — new dataset tests
- `uv run agent-core eval run --dataset jira_triage` — CLI smoke test
