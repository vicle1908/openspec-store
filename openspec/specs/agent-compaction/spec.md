# agent-compaction

## Purpose

Manages context window size through configurable compaction strategies, tool result clearing, read deduplication, limit warnings, and output overflow handling.

## Requirements

### Requirement: Compaction strategy selection

When `AgentConfig.context_compaction` is set, `AgentRuntime` SHALL create the appropriate compaction capability based on the `strategy` field.

#### Scenario: SummarizingCompaction (default)
- **WHEN** `context_compaction={"strategy": "summarize", "max_messages": 50, "keep_messages": 20}`
- **THEN** `SummarizingCompaction(max_messages=50, keep_messages=20)` SHALL be created

#### Scenario: SlidingWindow
- **WHEN** `context_compaction={"strategy": "sliding_window", "max_messages": 40}`
- **THEN** `SlidingWindow(max_messages=40)` SHALL be created

#### Scenario: Tiered compaction
- **WHEN** `context_compaction={"strategy": "tiered", "tiers": [...], "target_tokens": 80000}`
- **THEN** `TieredCompaction(tiers=[...], target_tokens=80000)` SHALL be created

#### Scenario: No compaction
- **WHEN** `context_compaction` is `None`
- **THEN** no compaction capability SHALL be added

### Requirement: ClampOversizedMessages

When `AgentConfig.context_compaction` includes `clamp_oversized: true`, a `ClampOversizedMessages` capability SHALL be added alongside the primary compaction strategy.

#### Scenario: Clamp enabled
- **WHEN** `context_compaction={"clamp_oversized": true, "max_part_tokens": 4000}`
- **THEN** `ClampOversizedMessages(max_part_tokens=4000)` SHALL be created

### Requirement: ClearToolResults

When `AgentConfig.context_compaction` includes `clear_tool_results: true`, a `ClearToolResults` capability SHALL be added. `ClearToolResults` requires at least one of `max_messages` or `max_tokens`.

#### Scenario: Clear enabled with message limit
- **WHEN** `context_compaction={"clear_tool_results": true, "max_messages": 10, "keep_pairs": 3}`
- **THEN** `ClearToolResults(max_messages=10, keep_pairs=3)` SHALL be created

#### Scenario: Clear enabled with token limit
- **WHEN** `context_compaction={"clear_tool_results": true, "max_tokens": 5000, "keep_pairs": 3}`
- **THEN** `ClearToolResults(max_tokens=5000, keep_pairs=3)` SHALL be created

#### Scenario: Missing both limits
- **WHEN** `context_compaction={"clear_tool_results": true}` without `max_messages` or `max_tokens`
- **THEN** a `ValueError` SHALL be raised at capability creation time

### Requirement: DeduplicateFileReads

When `AgentConfig.context_compaction` includes `deduplicate_reads: true`, a `DeduplicateFileReads` capability SHALL be added.

#### Scenario: Dedup enabled
- **WHEN** `context_compaction={"deduplicate_reads": true}`
- **THEN** `DeduplicateFileReads(file_key=...)` SHALL be created with a default file key extractor

### Requirement: LimitWarner

When `AgentConfig.limit_warnings` is set, a `LimitWarner` capability SHALL be created.

#### Scenario: Limit warner enabled
- **WHEN** `limit_warnings={"max_iterations": 10, "warning_threshold": 0.7}`
- **THEN** `LimitWarner(max_iterations=10, warning_threshold=0.7)` SHALL be created

### Requirement: OverflowingToolOutput

When `AgentConfig.output_overflow` is set, an `OverflowingToolOutput` capability SHALL be created. `Band` uses `over` (token count threshold) and `action` ("summarize" | "truncate" | "spill").

#### Scenario: Band-based overflow
- **WHEN** `output_overflow={"bands": [{"over": 1000, "action": "summarize"}]}`
- **THEN** `OverflowingToolOutput(bands=[Band(over=1000, action="summarize")])` SHALL be created

#### Scenario: Per-tool overflow config
- **WHEN** `output_overflow={"per_tool": {"shell_execute": [{"over": 500, "action": "truncate"}]}}`
- **THEN** per-tool bands SHALL be applied only to the specified tools

### Requirement: CacheStabilityMonitor

When `AgentConfig.cache_monitoring` is set, a `CacheStabilityMonitor` capability SHALL be created.

#### Scenario: Cache monitoring enabled
- **WHEN** `cache_monitoring={"collapse_ratio": 0.5}`
- **THEN** `CacheStabilityMonitor(collapse_ratio=0.5)` SHALL be created
