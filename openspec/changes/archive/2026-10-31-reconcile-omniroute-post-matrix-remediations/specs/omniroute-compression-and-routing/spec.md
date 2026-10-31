# Spec Delta: OmniRoute Compression and Routing

## MODIFIED Requirements

### Requirement: Cache and Coordination Isolation Evaluation
Before changing cache scope or Redis eviction policy, the evaluation SHALL classify enabled cache and coordination consumers and verify request isolation across owners, system policies (`sp:<sha256_16>` covering `body.system`, `body.instructions`, `body.systemInstruction`, and `messages[]` system/developer turns), tool contracts (`ct:<sha256_16>`), tool history (`tc:<sha256_16>`), and freshness state, as well as the effect of memory pressure on rate limits, quotas, and coordination state.

#### Scenario: Similar prompts with different request context
- **WHEN** similar requests differ in authorized owner, system policy (`body.system`, `body.instructions`, `body.systemInstruction`, or `messages[].role` in `["system", "developer"]`), tool contract, tool history, or freshness-sensitive state
- **THEN** `SemanticCacheManager` SHALL partition Layer-2 cache keys by `ct:<sha256_16>`, `tc:<sha256_16>`, and `sp:<sha256_16>` so an incompatible cached response is never reused across different system policies or tool contracts while identical system-policy repeats hit Layer-2.

#### Scenario: Shared Redis reaches its proposed memory budget
- **WHEN** a candidate eviction policy is evaluated against a Redis instance shared by cache and coordination consumers
- **THEN** the report SHALL identify which keys can be lost and whether enforcement weakens, and SHALL NOT assume that all expiring keys are disposable cache data or that maxmemory equals total process memory.
