# Harness Compaction Specification

> **⚠️ Historical spec:** This spec describes the removed `harness_config`
> dictionary-based interface. The current implementation uses typed capability
> composition via `build_agent(capabilities=[TieredCompaction(...)])`.
> See `agent-core/docs/harness-integration.md` for the current API.

## Purpose

Context window management via pydantic-ai-harness compaction capabilities (SlidingWindow, SummarizingCompaction, ClampOversizedMessages, ClearToolResults, DeduplicateFileReads).

## Requirements

### Requirement: Compaction layers remain independent from memory

Typed context compaction SHALL operate only on active conversation context, while caller-owned working, long-term, and step-persistence stores SHALL retain their own data and lifecycle semantics. Compaction SHALL not delete snapshots independently of the caller's configured store-retention policy; searchability is guaranteed only for snapshots retained by that policy.

#### Scenario: Compaction with persistent history

- **WHEN** an agent uses typed compaction together with step persistence
- **THEN** compaction SHALL not delete persisted snapshots
- **AND** a later history-search capability SHALL be able to use the retained caller-owned source

#### Scenario: Requested capability unavailable

- **WHEN** a caller explicitly requests a compaction capability that cannot be imported or constructed
- **THEN** construction SHALL fail before model or tool execution with the documented exact error category for that boundary: `ImportError` for an unavailable dependency, an upstream typed construction error for invalid capability arguments, or agent-core `ConfigError` for invalid public composition
- **AND** the runtime SHALL not silently continue without the requested behavior

#### Scenario: Caller configures bounded snapshot retention

- **WHEN** a caller configures a snapshot store that prunes older snapshots
- **THEN** compaction SHALL preserve the store's caller-owned retention semantics
- **AND** documentation and acceptance evidence SHALL not claim recovery of snapshots that the configured store has pruned
