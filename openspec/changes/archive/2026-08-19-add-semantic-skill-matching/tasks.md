## Tasks

### 1. Implementation
- [ ] Add `embedding_provider` parameter to `SkillMatcher.__init__`
- [ ] Add skill embedding pre-computation in `__init__`
- [ ] Add `_semantic_score()` method (cosine similarity)
- [ ] Update `score()` to blend lexical and semantic when provider available
- [ ] Write delta spec for skill-scope-profiles

### 2. Testing
- [ ] Existing matcher tests pass unchanged (no provider = lexical only)
- [ ] New test: mock EmbeddingProvider, verify blended scoring
- [ ] New test: verify graceful degradation when provider errors
- [ ] Run full agent-core test suite

### 3. Verification
- [ ] ruff check src/agent_core/skill_system/
- [ ] mypy src/agent_core/skill_system/ --strict
