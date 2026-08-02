# agent-core-integration-contract Specification

## Purpose

Defines how sibling repos and specialist agents consume agent-core, including composition patterns, public API usage, and durable scheduling.

## Requirements

### Requirement: Workspace integration contract exists

The workspace SHALL provide a canonical agent-core integration contract document for sibling repos and specialist agents under `$WORKSPACE/agent-core/docs/`.

#### Scenario: Contract document is present

- **WHEN** a developer looks under `$WORKSPACE/agent-core/docs/`
- **THEN** an integration contract document exists and describes how consumer repos use agent-core

#### Scenario: Contract defines ownership boundaries
- **WHEN** a consumer repo needs agent behavior
- **THEN** the contract states which behavior belongs in agent-core, which behavior belongs in the consumer repo adapter, and which behavior belongs in skills/tools

#### Scenario: Contract uses workspace-relative paths
- **WHEN** the contract document references workspace locations
- **THEN** it uses `$WORKSPACE`-relative paths (not a hardcoded home directory) so the guidance is portable across machines

### Requirement: Contract specifies composition-first specialization
The contract document SHALL specify that consumer repos specialize agent-core through `BaseAgent` configuration, flavors, tools, hooks, and `skill_profile`, not by subclassing agent-core runtime classes for domain behavior.

#### Scenario: Contract states the composition rule
- **WHEN** a developer reads the specialization section of the contract
- **THEN** it states that domain behavior is expressed as `BaseAgent` config (flavors/tools/hooks/`skill_profile`) and that subclassing runtime classes for domain behavior is disallowed

#### Scenario: Contract illustrates the adapter boundary with forward-looking examples
- **WHEN** the contract illustrates how repos like `ai-review` or `webhook-receiver` would adopt agent-core
- **THEN** those examples are marked as non-normative Phase 2 illustrations (no consumer adoption is required or implemented in Phase 1)

### Requirement: Contract recommends only current, validated public APIs
The contract and aligned docs SHALL recommend only APIs that exist in the current agent-core public surface, and the recommended patterns SHALL be validated as runnable, not merely free of stale references.

#### Scenario: Recommended patterns are proven against current code
- **WHEN** the contract recommends `BaseAgent(..., skill_profile=...)`, `skills.profiles` config, and the durable scheduling startup order
- **THEN** a verification step executes a minimal snippet exercising those exact signatures and it succeeds against the current agent-core build

#### Scenario: Stale patterns are absent
- **WHEN** the contract and aligned docs are scanned
- **THEN** removed/non-existent patterns (`skills.directories`, `SkillLoader.from_config()`, `MemoryFacade.from_config()`, `schedules run`) do not appear as recommendations

### Requirement: Contract specifies profile-based skill selection
The contract document SHALL specify that consumer repos select skills through `skills.profiles` and `skill_profile` rather than ad hoc directory lists.

#### Scenario: Specialist profile guidance
- **WHEN** a developer reads the skill-selection section
- **THEN** it states a specialist agent declares or references a profile and can be diagnosed with `agent-core skills doctor --profile <name>`

### Requirement: Contract standardizes durable scheduling startup order
The contract document SHALL specify the durable scheduling startup order — import scheduled modules, initialize the durable engine, then call `apply_schedules()` — and SHALL point to the runnable reference example.

#### Scenario: Startup order references the runnable example
- **WHEN** a developer reads the scheduling section of the contract
- **THEN** it documents the import → initialize → `apply_schedules()` order and links to `agent-core/scheduler_setup.py` as the canonical reference

### Requirement: The agent-core invocation contract is defined in Phase 2
Phase 1 recorded the consumer invocation contract as a Phase 2 deliverable. Phase 2 SHALL define it: a typed `AgentRequest` input and reuse of `AgentResult` as the response, with the integration contract document updated to link both.

#### Scenario: Contract document links the defined invocation contract
- **WHEN** a developer reads the integration contract document after Phase 2
- **THEN** it references `AgentRequest` as the structured input and `AgentResult` as the response, and references the runnable reference adapter without a Phase 1 deferral marker

#### Scenario: Contract links a runnable reference adapter
- **WHEN** the integration contract describes the consumer adapter pattern
- **THEN** it links the reference adapter in the existing `agent-core/examples/code_reviewer/` reference project as the executable demonstration

### Requirement: Phase 1 does not split repositories
This phase SHALL NOT move agent-core modules into separate repos or create new runtime packages.

#### Scenario: Repo split evaluation
- **WHEN** repo split is considered
- **THEN** the contract records that splitting is deferred until adapters and release-cadence evidence justify it

