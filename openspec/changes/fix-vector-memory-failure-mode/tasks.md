## Tasks

### 1. Implementation
- [x] Write proposal.md explaining vector memory silent failure problem
- [x] Write design.md with structured degradation approach
- [x] Write delta spec for vector-memory-search error classification
- [x] Fix facade.py:162 — replace `except Exception: pass` with logged degradation
- [x] Add `_vector_degraded` flag and `vector_degraded` property to Memory class

### 2. Testing
- [x] Add test: mock VectorMemory.search() raising ConnectionError, verify recall returns empty + logs warning
- [x] Add test: verify vector_degraded=True after vector failure
- [x] Add test: verify vector_degraded=False when vector=None (not configured)
- [x] Run full agent-core test suite (704+ tests must pass)

### 3. Spec Update
- [x] Update vector-memory-search main spec to include new error classification requirement

### 4. Verification
- [x] ruff check src/agent_core/memory/ tests/
- [x] mypy src/agent_core/memory/ --strict
- [x] git diff --check
