## Purpose

This specification defines requirements for Consumer Composition Boundary.

## Requirements

### Requirement: Thin-kernel ownership boundary

The framework SHALL assign generic agent and workflow mechanics to public upstream contracts, reusable TDT integration and policy to `agent-core`, and domain tools, prompts, state, artifacts, and graph topology to each consumer.

#### Scenario: Upstream feature exists

- **WHEN** Pydantic AI, Harness, or LangGraph exposes a supported public contract for a required generic feature
- **THEN** `agent-core` and its consumers SHALL compose that contract
- **AND** they SHALL not create a parallel semantic model or clone the upstream constructor surface

#### Scenario: Consumer-specific behavior

- **WHEN** behavior refers to docs artifacts, planning stages, gates, reports, or domain workflow edges
- **THEN** the owning consumer SHALL implement and test it
- **AND** `agent-core` SHALL not require the concept in its public API

### Requirement: Evidence-gated promotion

A feature SHALL be promoted from a consumer into `agent-core` only when it is TDT-specific, required by at least two active consumers, absent from supported upstream contracts, and expressible without importing either consumer's domain types.

#### Scenario: Single-consumer abstraction

- **WHEN** only `agent-harness` needs stage modules or only `agent-docs-sync` needs documentation stages
- **THEN** the abstraction SHALL remain consumer-owned

#### Scenario: Shared TDT policy

- **WHEN** two active consumers require the same model-resolution, authorization, budget, audit, or tool-metadata policy
- **THEN** the policy MAY be promoted behind a narrow public protocol
- **AND** contract tests SHALL cover both consumers before promotion

### Requirement: Configuration by composition

Consumers SHALL contain a stable `agent-core` runtime profile or equivalent value object rather than subclassing framework configuration classes.

#### Scenario: Consumer configuration

- **WHEN** `agent-docs-sync` or `agent-harness` adds domain settings
- **THEN** its configuration model SHALL own a composed runtime profile field
- **AND** domain fields SHALL not extend the `agent-core` configuration inheritance hierarchy

#### Scenario: Stage override

- **WHEN** one stage needs different model, limits, instructions, toolsets, or capabilities
- **THEN** the consumer SHALL derive an immutable run-scoped copy
- **AND** the parent configuration SHALL remain unchanged

### Requirement: Compatibility matrix

The workspace SHALL test one declared compatibility matrix for the direct Pydantic AI, Harness, and LangGraph versions imported by `agent-core` and active consumers.

#### Scenario: Upstream upgrade

- **WHEN** any framework dependency is upgraded
- **THEN** `agent-core`, `agent-docs-sync`, and `agent-harness` contract suites SHALL run together
- **AND** private upstream imports or attributes SHALL fail the compatibility gate
