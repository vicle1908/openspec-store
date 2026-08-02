## Purpose

This specification defines requirements for Agent Docs Research.

## Requirements

### Requirement: Framework comparison accuracy

The framework comparison docs SHALL reflect accurate version numbers and feature statuses from official sources.

#### Scenario: Version accuracy
- **WHEN** a developer reads `research/framework-comparison.md`
- **THEN** version numbers SHALL match PyPI latest releases (pydantic-ai v2.16.0, harness v0.10.0, langgraph v1.2.9)

### Requirement: Durable execution documented

The upgrade opportunities docs SHALL document durable execution capabilities.

#### Scenario: Durable execution section
- **WHEN** a developer reads `research/upgrade-opportunities.md`
- **THEN** it SHALL list 4 official solutions (Temporal, DBOS, Prefect, Restate) + 2 external (Kitaru, Airflow)
- **AND** it SHALL document `TemporalDurability`, `DBOSDurability`, `PrefectDurability` capabilities

### Requirement: Streaming v3 documented

The deep dive docs SHALL document LangGraph streaming v3.

#### Scenario: Streaming v3 section
- **WHEN** a developer reads `research/pydanticai-langgraph.md`
- **THEN** it SHALL document streaming v3 with SubgraphTransformer and content-block-centric streaming
- **AND** it SHALL note that v3 always uses `subgraphs=True`

### Requirement: Harness capability matrix accurate

The upgrade opportunities docs SHALL have accurate capability statuses.

#### Scenario: Stable capabilities
- **WHEN** a developer reads `research/upgrade-opportunities.md`
- **THEN** these capabilities SHALL be marked as "Stable": CodeMode, FileSystem, Shell, RepoContext, PyaiDocs, SlidingWindow, Compaction, LimitWarner, OverflowingToolOutput, CacheStabilityMonitor, Memory, StepPersistence, Checkpointing, SubAgents, DynamicWorkflow, Planning, RuntimeAuthoring, InputGuard, OutputGuard, ManagedPrompt, ExaSearch

#### Scenario: In-progress capabilities
- **WHEN** a developer reads `research/upgrade-opportunities.md`
- **THEN** these capabilities SHALL be marked as "In Progress": CostBudgets, ToolAccessControl, SecretMasking, StuckLoopDetection, ToolErrorRecovery

### Requirement: On-demand capabilities documented

The research docs SHALL document Pydantic AI V2 on-demand capabilities.

#### Scenario: On-demand section
- **WHEN** a developer reads `research/pydanticai-langgraph.md`
- **THEN** it SHALL document deferred-loading capabilities as a V2 feature
