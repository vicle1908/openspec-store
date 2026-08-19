## Tasks

### 1. Implementation
- [x] Add `embedding_provider: EmbeddingProvider | None` parameter to `SkillMatcher.__init__`
- [x] Add `lexical_weight`/`semantic_weight` parameters (default 0.4/0.6)
- [x] Add `init_embeddings()` — pre-computes and caches skill description embeddings
- [x] Add `_cosine_similarity()` helper method
- [x] Add `a_match()` — blends lexical and semantic scores when provider available

### 2. Backward Compatibility
- [x] `match()` remains synchronous lexical-only (no embedding calls)
- [x] When provider is None, `init_embeddings()` is a no-op
- [x] When provider is None, `a_match()` falls back to lexical

### 3. Testing
- [x] Test cosine similarity (identical, orthogonal, mismatched dimensions, zero vector)
- [x] Test semantic blending with embeddings
- [x] Test graceful degradation when provider errors (warning logged, skill excluded)
- [x] Test init_embeddings logs warning on failure
- [x] Run full agent-core test suite

### 4. Verification
- [x] ruff check src/agent_core/skill_system/
- [x] mypy src/agent_core/skill_system/ --strict
