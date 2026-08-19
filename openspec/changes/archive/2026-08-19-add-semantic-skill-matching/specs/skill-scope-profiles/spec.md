## ADDED Requirements

### Requirement: Optional semantic skill matching
The skill matcher SHALL support optional embedding-based semantic matching when an EmbeddingProvider is configured.

#### Scenario: Semantic matching enabled
- WHEN `SkillMatcher` is initialized with an `EmbeddingProvider`
- AND `init_embeddings()` is called with the skill list
- THEN skill description embeddings SHALL be pre-computed and cached
- AND `a_match()` SHALL blend lexical and semantic scores (default 0.4/0.6 split)
- AND `match()` SHALL remain lexical-only (synchronous, no embedding calls)

#### Scenario: Semantic matching disabled
- WHEN `SkillMatcher` is initialized without an `EmbeddingProvider` (default)
- THEN `match()` SHALL be purely lexical (keyword + token overlap)
- AND `init_embeddings()` SHALL be a no-op
- AND `a_match()` SHALL fall back to `match()` behavior
- AND no embedding API calls SHALL be made

#### Scenario: Embedding provider unavailable at runtime
- WHEN the EmbeddingProvider raises an error during `init_embeddings()`
- THEN the affected skill SHALL be excluded from semantic scoring
- AND `a_match()` SHALL fall back to lexical-only for that skill
- AND a warning SHALL be logged
