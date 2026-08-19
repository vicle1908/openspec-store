## ADDED Requirements

### Requirement: Consolidation trigger
The memory system SHALL support automatic consolidation triggered by recall count threshold or explicit invocation.

#### Scenario: Recall-count trigger
- WHEN the number of recall operations since last consolidation exceeds the configured threshold
- THEN the consolidation engine SHALL execute promotion, demotion, and merge passes
- AND metrics SHALL be returned to the caller

#### Scenario: Explicit trigger
- WHEN a consumer calls `memory.consolidate()`
- THEN the consolidation engine SHALL execute all passes immediately
- AND metrics SHALL be returned

#### Scenario: No trigger when disabled
- WHEN consolidation is not configured (default)
- THEN no consolidation SHALL execute automatically
- AND `memory.consolidate()` SHALL be a no-op returning zero metrics

### Requirement: Scratch-to-long-term promotion
Frequently-accessed scratch entries SHALL be promoted to long_term storage.

#### Scenario: Promotion threshold met
- WHEN a scratch entry has `access_count` greater than the promotion threshold
- AND the entry does not already exist in long_term
- THEN the entry SHALL be copied to long_term with the default long_term TTL
- AND the scratch entry SHALL remain unchanged

#### Scenario: Promotion skipped when already in long_term
- WHEN a scratch entry exists in long_term with the same key
- THEN the scratch entry SHALL NOT be promoted
- AND the long_term entry SHALL be left unchanged

### Requirement: Long-term demotion and expiry
Stale long_term entries SHALL be cleaned up based on TTL and access patterns.

#### Scenario: Expired entry with zero accesses
- WHEN a long_term entry has `expires_at` in the past
- AND its `access_count` is zero
- THEN the entry SHALL be deleted

#### Scenario: Expired entry with prior accesses
- WHEN a long_term entry has `expires_at` in the past
- AND its `access_count` is greater than zero
- THEN the entry SHALL be deleted
- AND a metrics entry SHALL record it as expired (not demoted)

### Requirement: Duplicate key conflict resolution
When the same key exists across multiple sessions, the most recently written value SHALL win.

#### Scenario: Cross-session duplicate
- WHEN `store("session-a", "key", value_a)` and `store("session-b", "key", value_b)` exist
- AND `updated_at` for session-b is more recent
- THEN consolidation SHALL retain session-b's entry
- AND session-a's entry SHALL be deleted
- AND metrics SHALL record one merge

### Requirement: Consolidation metrics
Consolidation SHALL return structured metrics about its operations.

#### Scenario: Metrics returned
- WHEN consolidation completes
- THEN it SHALL return a dict with keys: `promoted`, `demoted`, `merged`, `expired`
- AND each value SHALL be a non-negative integer
