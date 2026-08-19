## Tasks

### 1. Implementation
- [x] Write proposal.md explaining vector memory silent failure problem
- [x] Write design.md with structured degradation approach
- [x] Write delta spec for vector-memory-search error classification
- [ ] Fix facade.py:162 — replace `except Exception: pass` with logged degradation
- [ ] Add `_vector_degraded` flag and `vector_degraded` property to Memory class

### 2. Testing
- [ ] Add test: mock VectorMemory.search() raising ConnectionError, verify recall returns empty + logs warning
- [ ] Add test: verify vector_degraded=True after vector failure
- [ ] Add test: verify vector_degraded=False when vector=None (not configured)
- [ ] Run full agent-core test suite (704+ tests must pass)

### 3. Spec Update
- [ ] Update vector-memory-search main spec to include new error classification requirement

### 4. Verification
- [ ] ruff check src/agent_core/memory/ tests/
- [ ] mypy src/agent_core/memory/ --strict
- [ ] git diff --check
