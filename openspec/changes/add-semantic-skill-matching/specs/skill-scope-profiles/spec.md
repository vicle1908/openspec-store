## ADDED Requirements

### Requirement: Optional semantic skill matching
The skill matcher SHALL support optional embedding-based semantic matching when an EmbeddingProvider is configured.

#### Scenario: Semantic matching enabled
- WHEN `SkillMatcher` is initialized with an `EmbeddingProvider`
- THEN skill description embeddings SHALL be pre-computed at initialization
- AND query scoring SHALL blend lexical and semantic scores (default 0.4/0.6 split)

#### Scenario: Semantic matching disabled
- WHEN `SkillMatcher` is initialized without an `EmbeddingProvider` (default)
- THEN scoring SHALL be purely lexical (keyword + token overlap)
- AND no embedding API calls SHALL be made

#### Scenario: Embedding provider unavailable at runtime
- WHEN the EmbeddingProvider raises an error during skill embedding pre-computation
- THEN the affected skill SHALL be excluded from semantic scoring
- AND the matcher SHALL fall back to lexical-only for that skill
- AND a warning SHALL be logged
