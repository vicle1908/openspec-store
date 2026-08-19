## Tasks

### 1. Implementation
- [ ] Create `agent_core/evaluation/datasets/__init__.py` with dataset registry
- [ ] Create `jira_triage.py` with 5 evaluation cases
- [ ] Create `code_review.py` with 5 evaluation cases
- [ ] Create `docs_sync.py` with 3 evaluation cases
- [ ] Add `eval run` CLI command to agent-core Typer app

### 2. Testing
- [ ] Add tests for dataset loading and case validation
- [ ] Run full agent-core test suite (704+ tests)
- [ ] CLI smoke test: `agent-core eval run --dataset jira_triage`

### 3. Spec Update
- [ ] Update evaluation main spec with dataset requirement

### 4. Verification
- [ ] ruff check src/agent_core/evaluation/
- [ ] mypy src/agent_core/evaluation/ --strict
