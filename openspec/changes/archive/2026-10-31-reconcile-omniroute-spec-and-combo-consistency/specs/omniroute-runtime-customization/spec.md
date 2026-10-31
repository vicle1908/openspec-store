# Spec Delta: omniroute-runtime-customization

## MODIFIED Requirements

### Requirement: Compatibility Behavior and Patch Retirement Gates
The compatibility ledger SHALL map each local modification in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`3` non-chunk patches and `43` chunk/route replacements = `46` modifications) to its behavior, affected versions, `49` fail-closed markers (`3` non-chunk and `46` chunk markers across `19` compiled files), upstream status, and removal gate. Marker checks SHALL fail closed when any target file is missing or renamed.

#### Scenario: Retiring one upstreamed fix
- **WHEN** a validated upstream release supplies a replacement for a local modification
- **THEN** only that modification SHALL become eligible for retirement after its behavior passes verification, and unrelated modifications SHALL remain accounted for.

#### Scenario: Missing required compatibility state
- **WHEN** a candidate deployment cannot demonstrate a required compatibility condition or a target chunk or server file for any of the 49 required markers (`3` non-chunk and `46` chunk markers across `19` compiled files) is absent or renamed
- **THEN** `/app/container-entrypoint-compat.sh` SHALL fail closed with `[COMPAT_ERROR]` and exit `1` rather than silently skipping verification, and SHALL NOT promote the deployment as compatible.

### Requirement: Hybrid Retrieval Evaluation and Isolation
The evaluation plan SHALL compare lexical and semantic retrieval on the same authorized query set and corpus (covering embedding, filtering, ranking, reranking, and fallback costs) and SHALL enforce owner and `expires_at` filtering across SQLite `memories`, `memory_fts`, `vec_memories`, and Qdrant `fetchMemoriesByIds` paths. It SHALL retain the existing hybrid deployment until an alternative passes acceptance and cutover approval.

#### Scenario: Comparing local and external vector backends
- **WHEN** an evaluator compares supported local hybrid retrieval with Qdrant-backed retrieval
- **THEN** the report SHALL include relevance, end-to-end latency, resource use, configuration, and sample conditions; isolated keyword-query timings SHALL NOT be presented as equivalent semantic-search performance.

#### Scenario: Deleted, expired, or differently owned memories
- **WHEN** retrieval evaluates deleted or expired records (`expires_at <= datetime('now')`) or records outside the caller's authorized owner scope across `fetchMemoriesByIds`, `VectorStoreImpl.searchVector`, or `VectorStoreImpl.searchHybrid`
- **THEN** those records SHALL NOT appear in returned candidates or injected context, including on vector and hybrid fallback paths.

#### Scenario: Vector backend failure
- **WHEN** an evaluated vector backend fails or has no usable vectors
- **THEN** the report SHALL identify the fallback actually used and its quality impact rather than counting lexical fallback as successful semantic retrieval.
