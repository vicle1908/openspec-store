# agent-planning

## Purpose

Provides task planning capabilities for agents, enabling plan creation, item tracking with lifecycle states, and plan caching with configurable TTL.

## Requirements

### Requirement: Task planning via Planning capability

When `AgentConfig.planning` is set, `AgentRuntime` SHALL create a `Planning` capability.

#### Scenario: Planning with guidance
- **WHEN** `planning={"guidance": "Break tasks into small, verifiable steps"}`
- **THEN** `Planning(guidance="Break tasks into small, verifiable steps")` SHALL be created
- **AND** the agent SHALL have a `create_plan` / `update_plan` tool available

#### Scenario: Planning without guidance
- **WHEN** `planning={}`
- **THEN** `Planning()` SHALL be created with default guidance

### Requirement: Plan item tracking

The planning system SHALL track `PlanItem` objects with `content: str` and `status: TaskStatus`.

#### Scenario: Task lifecycle
- **WHEN** the agent creates a plan item
- **THEN** it SHALL start with `status: TaskStatus.pending`
- **AND** the agent SHALL be able to update it to `in_progress`, `completed`, or `cancelled`

### Requirement: Plan caching

Plans SHALL be cached with a configurable TTL.

#### Scenario: Cache TTL
- **WHEN** `planning={"cache_ttl": "1h"}`
- **THEN** the plan cache SHALL expire after 1 hour
