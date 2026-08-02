# agent-cache-monitoring

## Purpose

Monitors prompt cache hit stability and emits warnings when cache prefix collapses, enabling agents to detect and respond to cache degradation.

## Requirements

### Requirement: CacheStabilityMonitor capability

When `AgentConfig.cache_monitoring` is set, `AgentRuntime` SHALL create a `CacheStabilityMonitor` capability.

#### Scenario: Default cache monitoring
- **WHEN** `cache_monitoring={}`
- **THEN** `CacheStabilityMonitor()` SHALL be created with defaults (collapse_ratio=0.5, min_prefix_tokens=1024)

#### Scenario: Custom thresholds
- **WHEN** `cache_monitoring={"collapse_ratio": 0.3, "min_prefix_tokens": 2048}`
- **THEN** `CacheStabilityMonitor(collapse_ratio=0.3, min_prefix_tokens=2048)` SHALL be created

### Requirement: CacheBustWarning emission

When prompt cache hit collapses below `collapse_ratio`, a `CacheBustWarning` SHALL be emitted.

#### Scenario: Cache bust detected
- **WHEN** a request reads back less than `collapse_ratio` of the established prefix
- **THEN** a `CacheBustWarning` SHALL be emitted once per collapse event
- **AND** subsequent requests during the same collapse SHALL NOT emit additional warnings

### Requirement: Silent when caching off

The monitor SHALL be silent when caching is off or unreported.

#### Scenario: No cache tokens
- **WHEN** `cache_read_tokens` stays 0 across all requests
- **THEN** no warnings SHALL be emitted
