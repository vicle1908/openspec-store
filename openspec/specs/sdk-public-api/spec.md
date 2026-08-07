# sdk-public-api Specification

## Purpose

Defines the stable `agent-core` SDK surface, supported consumer composition contracts, and compatibility migration gates.
## Requirements
### Requirement: SDK re-exports validated consumer symbol set

The SDK SHALL expose a reviewed set of TDT-owned consumer symbols and compatibility adapters. It SHALL accept public upstream protocol values without re-exporting Pydantic AI, Harness, or LangGraph concrete classes.

| Area | Stable TDT-owned surface |
|---|---|
| Agent composition | `BaseAgent`, `AgentRequest`, `AgentResult`, `build_agent`, `ConsumerRuntimeProfile` |
| Model | `create_model`, `create_fallback_model`, `infer_model`, `FALLBACK_EXCEPTIONS` (pydantic-ai native) |
| Tool policy | `BaseTool`, `ToolMetadata`, `ToolResult`, `ToolRegistry`, `build_toolkit`, and the official-toolset adapter |
| TDT policy | budget, skills, authorization, audit, and observability inputs |
| Workflow integration | TDT checkpointer provisioning/resource helpers and compatibility adapters |

#### Scenario: Consumer imports stable TDT symbol

- **WHEN** a consumer imports a documented TDT-owned symbol from `agent_core.sdk`
- **THEN** the import SHALL resolve to the reviewed public implementation

#### Scenario: Consumer needs upstream concrete type

- **WHEN** a consumer needs `AgentCapability`, `AgentToolset`, `Hooks`, `StateGraph`, `Command`, or another upstream concrete type
- **THEN** it SHALL import that type from its public upstream package
- **AND** the SDK SHALL accept it without cloning or re-exporting the concrete class

#### Scenario: Legacy SDK export

- **WHEN** a consumer imports `WorkflowBuilder`, `WorkflowEngine`, `CommandResult`, `HookRegistry`, or another deprecated SDK symbol during the compatibility window
- **THEN** the compatibility export SHALL preserve supported behavior and emit an actionable migration warning

#### Scenario: Legacy export removal

- **WHEN** the compatibility window has elapsed and the workspace census reports zero callers
- **THEN** deprecated exports MAY be removed with migration and rollback documentation

### Requirement: ConsumerConfig composable base class

agent-core SHALL provide an immutable runtime-profile value model that composes agent-core `Settings`. Consumer domain configuration SHALL contain that profile instead of subclassing it. The existing `ConsumerConfig` name MAY remain as a compatibility alias or adapter only for the documented migration window.

#### Scenario: Consumer composes runtime profile

- **WHEN** a consumer defines domain configuration
- **THEN** it SHALL contain `runtime: ConsumerRuntimeProfile` or the documented equivalent value object
- **AND** domain fields SHALL not extend the core configuration inheritance hierarchy

#### Scenario: Legacy subclass during compatibility window

- **WHEN** an existing consumer subclasses `ConsumerConfig` during the compatibility window
- **THEN** construction SHALL preserve supported behavior
- **AND** it SHALL emit an actionable warning showing the contained-profile replacement

#### Scenario: Legacy subclass removal gate

- **WHEN** the minimum release/time window has elapsed
- **THEN** subclass compatibility SHALL remain until the workspace census reports zero active subclasses

### Requirement: Agent construction helper

agent-core SHALL provide `build_agent()` as a typed composition root requiring an explicit model or model configuration, a runtime profile, official capabilities/toolsets, and explicit TDT policy inputs. Legacy `hooks`, `harness_config`, and untyped memory inputs SHALL enter through isolated compatibility adapters only.

#### Scenario: Typed agent construction

- **WHEN** a consumer supplies a runtime profile, model, official capabilities/toolsets, and TDT policy inputs
- **THEN** `build_agent()` SHALL construct a `BaseAgent` without inspecting private upstream attributes or reconstructing supplied upstream values

#### Scenario: Missing model

- **WHEN** no model configuration is available
- **THEN** `build_agent()` SHALL fail before `BaseAgent` initialization

#### Scenario: Legacy construction

- **WHEN** a consumer supplies supported legacy hooks, `harness_config`, or memory arguments during the compatibility window
- **THEN** one adapter SHALL translate them to the typed composition path
- **AND** it SHALL emit an actionable warning

### Requirement: Consumer memory initialization

agent-core SHALL provide a TDT memory-store adapter or secure-profile factory that preserves consumer namespace, tenant, repository, correlation, retention, and authorization policy while returning public Harness `MemoryStore`/`Memory` values.

#### Scenario: Consumer initializes TDT memory

- **WHEN** a consumer requests TDT-backed memory
- **THEN** the helper SHALL return a public Harness-compatible store or capability
- **AND** storage paths and credentials SHALL resolve through centralized TDT configuration

### Requirement: Observability initialization helper

agent-core SHALL provide an observability composition helper that configures TDT logging, OpenTelemetry instrumentation, and audit correlation without creating a second agent lifecycle.

#### Scenario: Consumer initializes observability

- **WHEN** a consumer enables the documented observability profile
- **THEN** official Instrumentation/Hooks and TDT callbacks SHALL receive correlated events exactly once
- **AND** secrets SHALL not be included in logs or traces

### Requirement: Typed agent composition API

`agent_core.sdk` SHALL provide a stable composition API that accepts official Pydantic AI capabilities and toolsets without requiring consumers to encode each upstream constructor in an `agent-core` dictionary schema.

#### Scenario: Consumer supplies capabilities

- **WHEN** a consumer passes a sequence of supported `AgentCapability` instances
- **THEN** the resulting agent SHALL install those capabilities
- **AND** `agent-core` SHALL not reconstruct or reinterpret their constructor arguments

#### Scenario: Consumer supplies toolsets

- **WHEN** a consumer passes one or more supported `AgentToolset` instances
- **THEN** the resulting agent SHALL compose them with the TDT registry toolset
- **AND** tool names, schemas, retries, metadata, and ownership SHALL remain intact

#### Scenario: Invalid composition input

- **WHEN** a consumer supplies an object that is neither a supported capability, toolset, nor TDT policy input
- **THEN** construction SHALL fail with the rejected input category

#### Scenario: Upstream type ownership

- **WHEN** a consumer needs a concrete Pydantic AI or Harness capability
- **THEN** it SHALL import that type from its public upstream module
- **AND** `agent_core.sdk` SHALL accept it without re-exporting or cloning the concrete class

### Requirement: TDT policy remains explicit

The public composition API SHALL keep model/provider selection, budgets, skills, tool metadata, audit defaults, consumer authorization, model visibility, and execution authority as explicit TDT-owned inputs.

#### Scenario: Official capability with TDT policy

- **WHEN** a consumer composes an official capability with a TDT tool registry
- **THEN** the tool allowlist, visibility, approval metadata, authority grant, budget, correlation ID, and audit policy SHALL still apply

#### Scenario: High-authority capability

- **WHEN** a consumer requests filesystem write, shell, code execution, runtime authoring, external search, or network authority
- **THEN** the composition API SHALL require explicit least-privilege policy and any required operation-bound approval
- **AND** registration SHALL not enable visibility or execution by default

#### Scenario: Compatibility adapter widens authority

- **WHEN** a legacy input cannot be translated without broadening authority
- **THEN** translation SHALL fail with migration guidance
- **AND** it SHALL not silently preserve the broader behavior

### Requirement: Valid model before construction

The public SDK SHALL require either an explicit model string/instance or a default model configuration and SHALL NOT pass `None` into `BaseAgent`.

#### Scenario: Explicit model

- **WHEN** a consumer supplies a valid model string or Model instance
- **THEN** the SDK SHALL preserve that model through agent construction

#### Scenario: Default model

- **WHEN** no model is provided
- **THEN** the SDK SHALL use the configured default model from `config.settings.agent.default_model`
- **AND** it SHALL use `create_model()` to resolve the model string

#### Scenario: Invalid model

- **WHEN** an invalid model string is provided
- **THEN** construction SHALL fail before `BaseAgent` initialization with an actionable configuration error

### Requirement: Legacy SDK migration

The SDK SHALL provide a documented compatibility period of at least one published `agent-core` minor release and 30 days for legacy `harness_config` consumers. Removal SHALL additionally require a workspace census with zero active callers and a local clean-runner compatibility matrix for supported consumers. Hosted compatibility evidence SHALL be additive and SHALL remain deferred until immutable repository identities are configured and its execution is separately authorized.

#### Scenario: Legacy configuration during compatibility window

- **WHEN** a supported legacy configuration is used during the compatibility window
- **THEN** it SHALL be translated to typed composition
- **AND** a deprecation warning SHALL identify the equivalent public API

#### Scenario: Unknown or lossy legacy option

- **WHEN** a legacy configuration contains an unknown key or an upstream argument the adapter cannot preserve
- **THEN** translation SHALL fail
- **AND** it SHALL not silently drop the option

#### Scenario: Compatibility removal gate

- **WHEN** the minimum time/release window has elapsed
- **THEN** the adapter SHALL remain until repository manifests, imports, configuration files, examples, deployment bundles, and the local clean-runner consumer matrix report zero active callers or incompatibilities
- **AND** removal SHALL include migration and rollback documentation

#### Scenario: Hosted compatibility evidence is unavailable

- **WHEN** remote repository identities or hosted execution authorization are unavailable
- **THEN** the local clean-runner matrix SHALL remain valid compatibility evidence for the initial gate
- **AND** the system SHALL record hosted evidence as deferred rather than substituting guessed remotes or ambient editable paths

### Requirement: Executable SDK migration references

SDK documentation SHALL enumerate the current exported consumer symbols, compatibility-window behavior, high-authority policy inputs, and removal gates using executable or statically checked examples.

#### Scenario: Current import example

- **WHEN** the documentation check imports a documented stable symbol
- **THEN** the import SHALL resolve from the reviewed public surface
- **AND** concrete upstream types SHALL be shown from their owning package

#### Scenario: Deprecated example

- **WHEN** a deprecated compatibility example is retained
- **THEN** it SHALL show the warning and typed replacement
- **AND** it SHALL identify the release/time and zero-caller conditions for removal

### Requirement: SDK re-exports lifecycle identity and settings symbols

The SDK SHALL re-export the following symbols so consumers import only from
`agent_core.sdk`, never from internal modules:

| Symbol | Origin module |
|--------|---------------|
| `Settings` | `agent_core.foundation.settings` |
| `AuthenticatedSubject` | `agent_core.lifecycle_identity` |
| `ConfigFileResolver` | `agent_core.lifecycle_identity` |
| `IdentityStatus` | `agent_core.lifecycle_identity` |
| `SignedSubjectAssertion` | `agent_core.lifecycle_identity` |
| `SubjectResolutionRequest` | `agent_core.lifecycle_identity` |
| `SubjectResolutionResult` | `agent_core.lifecycle_identity` |

#### Scenario: Settings available from SDK
- **WHEN** a consumer imports `from agent_core.sdk import Settings`
- **THEN** the import SHALL succeed
- **AND** `Settings` SHALL be the same class as `agent_core.foundation.settings.Settings`

#### Scenario: Lifecycle identity symbols available from SDK
- **WHEN** a consumer imports `from agent_core.sdk import SubjectResolutionRequest, SubjectResolutionResult`
- **THEN** the imports SHALL succeed
- **AND** the classes SHALL be the same as their `agent_core.lifecycle_identity` originals

#### Scenario: Auth lifecycle symbols available from SDK
- **WHEN** a consumer imports `from agent_core.sdk import AuthenticatedSubject, ConfigFileResolver, IdentityStatus, SignedSubjectAssertion`
- **THEN** the imports SHALL succeed
- **AND** each class SHALL be the same as its `agent_core.lifecycle_identity` original

#### Scenario: Re-exports appear in __all__
- **WHEN** `agent_core.sdk.__all__` is inspected
- **THEN** all 7 symbols SHALL be listed in `__all__`

