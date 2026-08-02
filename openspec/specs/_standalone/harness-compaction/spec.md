# Harness Compaction Specification

## Purpose

Context window management via pydantic-ai-harness compaction capabilities (SlidingWindow, SummarizingCompaction, ClampOversizedMessages, ClearToolResults, DeduplicateFileReads).

## Requirements

### Requirement: Context compaction is configurable via harness_config

The system SHALL support a `context_compaction` configuration key in the `harness_config` dict passed to `AgentRuntime`. This enables harness compaction capabilities for context window management.

**Implementation:** In `_ai/agent.py:_build_harness_capabilities()`, the existing `context_compaction` handling already supports this. No code changes needed — just documentation and config template updates.

**Existing config fields (already implemented):**
- `strategy`: `"summarizing"` (default) or `"sliding_window"`
- `max_messages`: int (default 50)
- `max_tokens`: int|None (default None)
- `clamp_oversized`: bool (default False)
- `clear_tool_results`: bool (default False)
- `deduplicate_reads`: bool (default False)

#### Scenario: SummarizingCompaction enabled
- **WHEN** `harness_config={"context_compaction": {"strategy": "summarizing"}}` is passed to `AgentRuntime`
- **THEN** `_build_harness_capabilities()` SHALL instantiate `SummarizingCompaction(max_messages=50)` and append it to the capabilities list
- **AND** the capability SHALL be imported from `pydantic_ai_harness.compaction`

#### Scenario: SlidingWindow compaction enabled
- **WHEN** `harness_config={"context_compaction": {"strategy": "sliding_window", "max_messages": 30}}` is passed
- **THEN** `_build_harness_capabilities()` SHALL instantiate `SlidingWindow(max_messages=30)` and append it to the capabilities list

#### Scenario: Default strategy when omitted
- **WHEN** `harness_config={"context_compaction": {}}` is passed without a `strategy` key
- **THEN** the system SHALL default to `strategy: "summarizing"` and instantiate `SummarizingCompaction(max_messages=50)`

#### Scenario: Compaction disabled by default
- **WHEN** `harness_config` does not contain `context_compaction` key
- **THEN** no compaction capability SHALL be added to the agent

### Requirement: Optional compaction sub-features are configurable

The system SHALL support optional compaction sub-features via config keys. Each sub-feature is independently toggleable.

**Implementation:** Each sub-feature is handled in `_build_harness_capabilities()` with its own try/except ImportError block. Sub-features are additive — they stack on top of the base compaction strategy.

#### Scenario: ClampOversizedMessages enabled
- **WHEN** `harness_config={"context_compaction": {"clamp_oversized": true}}` is passed
- **THEN** `ClampOversizedMessages(max_part_chars=10000)` SHALL be appended to capabilities
- **AND** the default `max_part_chars` SHALL be 10000 (configurable via `max_part_chars` key)

#### Scenario: ClearToolResults enabled
- **WHEN** `harness_config={"context_compaction": {"clear_tool_results": true}}` is passed
- **THEN** `ClearToolResults(max_messages=10)` SHALL be appended to capabilities
- **AND** the default `max_messages` SHALL be 10 (configurable via `clear_tool_results_max_messages` key)

#### Scenario: DeduplicateFileReads enabled
- **WHEN** `harness_config={"context_compaction": {"deduplicate_reads": true}}` is passed
- **THEN** `DeduplicateFileReads` SHALL be appended to capabilities
- **AND** a `file_key` function SHALL be provided that extracts `tool_call_id` from parts

#### Scenario: Multiple sub-features combined
- **WHEN** `harness_config={"context_compaction": {"strategy": "summarizing", "clamp_oversized": true, "clear_tool_results": true, "deduplicate_reads": true}}` is passed
- **THEN** all three sub-features SHALL be appended to capabilities alongside the base compaction

### Requirement: Compaction composes with existing memory layers

Harness compaction SHALL operate alongside agent-core's existing memory system without conflicts. The layers operate at different levels of the memory hierarchy.

**Layer architecture:**
- Harness compaction: handles context window truncation (smart summarization, sliding window)
- ContextMemory: bounded FIFO working buffer (in-process)
- ScratchMemory: filesystem key-value (ephemeral state)
- PostgresMemory: JSONB long-term knowledge (semantic search)
- FeedbackStore: episodic feedback (unique to agent-core)

#### Scenario: Compaction with ContextMemory
- **WHEN** an agent has both harness compaction and ContextMemory enabled
- **THEN** harness compaction SHALL handle context window truncation
- **AND** ContextMemory SHALL continue to serve as the bounded FIFO working buffer
- **AND** both systems SHALL operate at different layers without interference

#### Scenario: Compaction with PostgresMemory
- **WHEN** an agent has both harness compaction and PostgresMemory enabled
- **THEN** compaction SHALL only affect the active conversation context
- **AND** PostgresMemory SHALL continue to handle long-term knowledge storage and retrieval

#### Scenario: Compaction with FeedbackStore
- **WHEN** an agent has both harness compaction and FeedbackStore enabled
- **THEN** compaction SHALL NOT affect feedback entries
- **AND** FeedbackStore SHALL continue to record episodic feedback independently

### Requirement: Compaction gracefully degrades when harness is unavailable

The system SHALL handle missing pydantic-ai-harness dependency gracefully. All harness imports are wrapped in try/except ImportError blocks.

#### Scenario: Harness installed
- **WHEN** `pydantic-ai-harness` is available in the Python environment
- **AND** `context_compaction` config is enabled
- **THEN** compaction capabilities SHALL be successfully instantiated

#### Scenario: Harness not installed
- **WHEN** `pydantic-ai-harness` is NOT available in the Python environment
- **AND** `context_compaction` config is enabled
- **THEN** `_build_harness_capabilities()` SHALL log a warning via structlog and skip compaction capabilities (graceful degradation, no crash)

### Requirement: Compaction parameters are configurable

The system SHALL support tuning compaction parameters via config. All parameters have sensible defaults.

#### Scenario: Custom max_messages
- **WHEN** `harness_config={"context_compaction": {"strategy": "summarizing", "max_messages": 30}}` is passed
- **THEN** `SummarizingCompaction(max_messages=30)` SHALL be instantiated with the custom value

#### Scenario: Custom max_tokens
- **WHEN** `harness_config={"context_compaction": {"strategy": "summarizing", "max_tokens": 8000}}` is passed
- **THEN** `SummarizingCompaction(max_tokens=8000)` SHALL be instantiated with the custom value

#### Scenario: Custom clamp_oversized max_part_chars
- **WHEN** `harness_config={"context_compaction": {"clamp_oversized": true, "max_part_chars": 5000}}` is passed
- **THEN** `ClampOversizedMessages(max_part_chars=5000)` SHALL be instantiated with the custom value

### Requirement: Compaction config is documented in config.yaml.example

The `context_compaction` config key SHALL be documented in `agent-core/config.yaml.example` with usage comments.

#### Scenario: Config template includes compaction
- **WHEN** a user copies `config.yaml.example` to `~/.tdt/config.yaml`
- **THEN** the template SHALL include a commented `context_compaction` section with example configuration showing all strategies and sub-features
