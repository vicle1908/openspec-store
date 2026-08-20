# agent-compaction

> **⚠️ Partially historical:** This spec describes `_build_harness_capabilities()`
> which has been removed. Compaction is now wired via typed capability composition
> (`TieredCompaction` in `AgentRuntime.__init__`). Config fields in `_ai/config.py`
> exist but are not read by AgentRuntime. See `agent-core/docs/harness-integration.md`.

## Purpose

Manages context window size through configurable compaction strategies, tool result clearing, read deduplication, limit warnings, and output overflow handling.

## Requirements

### Requirement: Typed compaction is explicitly enabled

The agent runtime SHALL add context compaction only when the caller supplies a typed compaction capability, and SHALL preserve the configured strategy and target without silently replacing it.

#### Scenario: Compaction omitted

- **WHEN** an agent is constructed without a compaction capability
- **THEN** no compaction capability SHALL be installed
- **AND** the runtime SHALL not trim or summarize context because of an undocumented default

#### Scenario: Tiered compaction supplied

- **WHEN** a caller supplies a tiered compaction with a target and ordered strategies
- **THEN** the runtime SHALL preserve the target and strategy order
- **AND** the capability SHALL execute through the supported upstream capability API

### Requirement: Compaction behavior is publicly verifiable

Compaction acceptance SHALL execute through the public agent boundary and SHALL prove both the below-threshold and threshold-exceeded paths.

#### Scenario: Conversation remains below target

- **WHEN** a deterministic conversation remains below the configured target
- **THEN** no compaction receipt or synthetic summary SHALL be inserted

#### Scenario: Conversation exceeds target

- **WHEN** a deterministic conversation exceeds the configured target
- **THEN** compaction SHALL reduce the active context according to the supplied strategy
- **AND** protected facts and any configured receipt/evidence SHALL remain observable
