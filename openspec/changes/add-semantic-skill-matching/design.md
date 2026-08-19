# Design: Add Semantic Skill Matching

## Problem

The `SkillMatcher` (133 lines, `skill_system/matcher.py`) uses only keyword + token overlap. Skills with synonymous descriptions don't match.

## Approach

### 1. EmbeddingProvider integration

Add optional `embedding_provider: EmbeddingProvider | None` to `SkillMatcher.__init__`. When None, behavior is unchanged (purely lexical).

### 2. Pre-computed skill embeddings

At matcher initialization, embed each skill's description string and cache as `{skill_name: list[float]}`. This is a one-time cost.

### 3. Blended scoring

```python
def _semantic_score(self, query_embedding: list[float], skill_embedding: list[float]) -> float:
    # Cosine similarity via dot product (normalized vectors)
    dot = sum(a * b for a, b in zip(query_embedding, skill_embedding))
    return max(0.0, min(1.0, dot))

def score(self, query: str, skill: Skill) -> SkillMatch:
    keyword = self._keyword_score(query, skill)
    overlap = self._overlap_score(query, skill)
    lexical = self._keyword_weight * keyword + self._overlap_weight * overlap
    
    if self._embedding_provider and skill.name in self._skill_embeddings:
        query_emb = self._embedding_provider.embed(query)  # cached
        semantic = self._semantic_score(query_emb, self._skill_embeddings[skill.name])
        final = 0.4 * lexical + 0.6 * semantic
    else:
        final = lexical
    
    return SkillMatch(skill=skill, score=final, ...)
```

### 4. Spec delta

Add semantic matching requirement to `skill-scope-profiles` spec.

## Files Changed

| File | Change |
|------|--------|
| `agent_core/skill_system/matcher.py` | Add embedding_provider param, semantic scoring, skill embedding cache |
| `openspec/specs/skill-scope-profiles/spec.md` | MODIFIED: semantic matching requirement |

## Testing

- Existing matcher tests pass unchanged (embedding_provider defaults to None)
- New test: mock EmbeddingProvider, verify blended scoring produces different results than lexical
- New test: verify lexical-only behavior when embedding_provider is None
