## Tasks

### 1. Implementation
- [x] Create `agent_core/evaluation/datasets/__init__.py` with dataset registry
- [x] Create `jira_triage.py` with 5 evaluation cases
- [x] Create `code_review.py` with 5 evaluation cases
- [x] Create `docs_sync.py` with 3 evaluation cases
- [x] Add `eval run` CLI command to agent-core Typer app

### 2. Testing
- [x] Add tests for dataset loading and case validation
- [x] Run full agent-core test suite (704+ tests)
- [x] CLI smoke test: `agent-core eval run --dataset jira_triage`

### 3. Spec Update
- [x] Update evaluation main spec with dataset requirement

### 4. Verification
- [x] ruff check src/agent_core/evaluation/
- [x] mypy src/agent_core/evaluation/ --strict
