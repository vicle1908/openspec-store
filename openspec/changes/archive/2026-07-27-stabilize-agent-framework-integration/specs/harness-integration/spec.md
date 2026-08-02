## MODIFIED Requirements

### Requirement: pydantic-ai-harness dependency

`agent-core` and `agent-docs-sync` SHALL declare `pydantic-ai>=2.18.0,<2.19` and `pydantic-ai-harness[dynamic-workflow]==0.11.0`; framework code using LangGraph SHALL declare `langgraph>=1.2.9,<1.3`. Their committed `uv.lock` files SHALL resolve Pydantic AI 2.18.0, Harness 0.11.0, Monty 0.0.19 through the Harness extra, and LangGraph 1.2.9.

#### Scenario: Compatible Harness and Monty resolution

- **WHEN** `uv sync --frozen` is run in both repositories
- **THEN** both environments SHALL report Pydantic AI 2.18.0, Harness 0.11.0, Monty 0.0.19, and LangGraph 1.2.9
- **AND** Monty SHALL be selected through the Harness `dynamic-workflow` extra rather than a conflicting direct constraint
- **AND** importing `pydantic_ai_harness.dynamic_workflow.DynamicWorkflow` SHALL succeed in both environments

#### Scenario: Direct dependency ownership

- **WHEN** `agent-docs-sync` imports Pydantic AI or Harness modules
- **THEN** its project manifest SHALL declare those dependencies directly
- **AND** it SHALL not depend on `agent-core` to expose undeclared transitive packages

#### Scenario: Dependency update review

- **WHEN** implementation applies the reviewed Pydantic AI, Harness-extra, Monty-resolution, or LangGraph baseline
- **THEN** the dependency change SHALL receive explicit team review before it is applied
- **AND** both lockfiles SHALL be regenerated with `uv`

#### Scenario: Frozen reproducibility

- **WHEN** CI installs either repository
- **THEN** it SHALL use `uv sync --frozen`
- **AND** the installed version probe SHALL match the exact reviewed baseline

## ADDED Requirements

### Requirement: Explicit capability activation

An explicitly configured Harness capability SHALL either be constructed successfully with the requested policy or raise a typed, actionable configuration error. It SHALL NOT be replaced by an allow-all, empty, or absent capability.

#### Scenario: Invalid configured guard

- **WHEN** guardrail configuration is present but is neither a supported guard callable nor a supported guard capability
- **THEN** agent construction SHALL fail
- **AND** the error SHALL identify `guardrails` and the accepted contract

#### Scenario: Missing optional dependency

- **WHEN** a configured capability cannot import because its optional dependency is missing or incompatible
- **THEN** construction SHALL fail with the capability name and `uv` remediation
- **AND** the system SHALL emit a structured activation-failure event

#### Scenario: Unconfigured optional capability

- **WHEN** a capability is absent from configuration
- **THEN** it SHALL remain disabled without error

### Requirement: Public Harness imports

`agent-core` SHALL import supported stores and capabilities from public Harness modules.

#### Scenario: Step store construction

- **WHEN** step persistence selects an in-memory, file, or SQLite store
- **THEN** the store SHALL be imported from the public `pydantic_ai_harness.step_persistence` surface
- **AND** no `_store` private module import SHALL be required

#### Scenario: Upstream compatibility verification

- **WHEN** the approved Harness version is installed
- **THEN** a contract test SHALL construct every documented supported capability using only public imports

### Requirement: Typed framework-consumer boundary

`agent-core` SHALL publish PEP 561 typing metadata and its public SDK annotations
SHALL describe the framework values accepted by supported consumers.

#### Scenario: Consumer static analysis

- **WHEN** `agent-docs-sync` imports and composes the installed `agent-core` SDK
- **THEN** strict mypy SHALL analyze the real framework types rather than replacing them with `Any`
- **AND** Pyright SHALL report no source errors or warnings
- **AND** public gateway, tool-registry, configuration-constructor, and asynchronous workflow-handler contracts SHALL type-check without consumer-specific casts

#### Scenario: Repository quality gates

- **WHEN** archive verification runs in either repository
- **THEN** Ruff SHALL report no diagnostics
- **AND** strict mypy SHALL report no diagnostics under the repository's production and test-double policies
- **AND** the configured Python language-server checker SHALL report no source errors or warnings
