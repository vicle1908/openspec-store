# Spec Delta: OmniRoute Runtime Customization

## MODIFIED Requirements

### Requirement: Compatibility Behavior and Patch Retirement Gates
The compatibility ledger SHALL map each local modification in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`3` non-chunk patches and `41` chunk/route replacements) to its intended behavior, affected versions, 46 fail-closed marker assertions (3 non-chunk markers and 43 chunk markers across 16 compiled files), upstream replacement status, and removal condition. Marker checks SHALL fail closed when any target file is missing or renamed and SHALL supplement behavioral verification.

#### Scenario: Retiring one upstreamed fix
- **WHEN** a validated upstream release supplies a replacement for a local modification
- **THEN** only that modification SHALL become eligible for retirement after its behavior passes verification, and unrelated modifications SHALL remain accounted for.

#### Scenario: Missing required compatibility state
- **WHEN** a candidate deployment cannot demonstrate a required compatibility condition or a target chunk or server file for any of the 46 required markers is absent or renamed
- **THEN** `/app/container-entrypoint-compat.sh` SHALL fail closed with `[COMPAT_ERROR]` and exit `1` rather than silently skipping verification, and SHALL NOT promote the deployment as compatible.

### Requirement: Hybrid Retrieval Evaluation and Isolation
The evaluation plan SHALL compare lexical and semantic retrieval using the same authorized query set and corpus, including embedding generation, filtering, ranking, reranking, and fallback costs where applicable, and SHALL enforce owner and `expires_at` filtering across SQLite `memories`, `memory_fts`, `vec_memories`, and Qdrant `fetchMemoriesByIds` paths. It SHALL retain the existing hybrid deployment until an alternative satisfies the documented acceptance criteria and receives cutover approval.

#### Scenario: Comparing local and external vector backends
- **WHEN** an evaluator compares supported local hybrid retrieval with Qdrant-backed retrieval
- **THEN** the report SHALL include relevance, end-to-end latency, resource use, configuration, and sample conditions; isolated keyword-query timings SHALL NOT be presented as equivalent semantic-search performance.

#### Scenario: Deleted, expired, or differently owned memories
- **WHEN** retrieval evaluates deleted or expired records (`expires_at <= datetime('now')`) or records outside the caller's authorized owner scope across `fetchMemoriesByIds`, `VectorStoreImpl.searchVector`, or `VectorStoreImpl.searchHybrid`
- **THEN** those records SHALL NOT appear in returned candidates or injected context, including on vector and hybrid fallback paths.

#### Scenario: Vector backend failure
- **WHEN** an evaluated vector backend fails or has no usable vectors
- **THEN** the report SHALL identify the fallback actually used and its quality impact rather than counting lexical fallback as successful semantic retrieval.
