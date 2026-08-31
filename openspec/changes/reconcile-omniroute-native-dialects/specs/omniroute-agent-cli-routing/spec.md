## MODIFIED Requirements

### Requirement: OmniRoute registrations SHALL use live namespace IDs with credential indirection

Every OmniRoute model registration added or corrected by this change SHALL use one of the live requested namespace/model pairs: `pm/Claude-Fable` for the Anthropic Messages route or `sh/gpt-5.6-sol` for the OpenAI Responses route. The exact model ID SHALL be present in a fresh `GET http://localhost:20128/v1/models` response at apply time. Retired `dlg/*` inference routes SHALL NOT be added to or retained in an active OmniRoute registration owned by this change. Credentials SHALL use `OMNIROUTE_API_KEY` through the CLI's documented environment, helper, or provider-key mechanism; literal credentials are prohibited except for the documented Kimi Code limitation when its installed provider contract cannot resolve shell variables.

#### Scenario: Requested namespace IDs are validated against the live catalog

- **WHEN** an OmniRoute model entry is added or corrected
- **THEN** `pm/Claude-Fable` or `sh/gpt-5.6-sol` SHALL exist in the fresh live model response
- **AND** the entry SHALL preserve the exact namespace and punctuation
- **AND** no new `dlg/*` entry SHALL be written

#### Scenario: Credentials remain external

- **WHEN** a changed CLI supports environment-backed provider credentials
- **THEN** the configuration SHALL reference `OMNIROUTE_API_KEY` or an approved helper
- **AND** no literal credential value SHALL appear in the configuration, OpenSpec artifacts, logs, process arguments, or evidence
- **AND** the Kimi Code limitation SHALL be recorded if its mode-600 provider field must retain an existing literal value

## ADDED Requirements

### Requirement: Namespace and native wire dialect SHALL be bound explicitly

A consumer that supports Anthropic Messages SHALL route `pm/Claude-Fable` through its Anthropic Messages implementation and SHALL target the OmniRoute `/v1/messages` route. A consumer that supports OpenAI Responses SHALL route `sh/gpt-5.6-sol` through its Responses implementation and SHALL target the OmniRoute `/v1/responses` route. A model SHALL NOT be registered under the other native dialect merely because a cross-dialect raw request happens to return HTTP 200.

#### Scenario: Claude namespace uses Anthropic Messages

- **WHEN** a CLI's native Anthropic provider is configured for OmniRoute
- **THEN** its effective wire model SHALL be `pm/Claude-Fable`
- **AND** its effective request SHALL be `POST http://localhost:20128/v1/messages`
- **AND** it SHALL NOT use `sh/Claude-Fable` as the Claude model for that provider

#### Scenario: GPT namespace uses OpenAI Responses

- **WHEN** a CLI's native Responses provider is configured for OmniRoute
- **THEN** its effective wire model SHALL be `sh/gpt-5.6-sol`
- **AND** its effective request SHALL be `POST http://localhost:20128/v1/responses`
- **AND** its reasoning control SHALL use a live-supported effort tier

### Requirement: Chat Completions SHALL be an exception-only fallback

A CLI SHALL use the Chat Completions dialect for an OmniRoute requested model only when its native Messages or Responses implementation is unavailable or fails a product-specific compatibility gate. The fallback SHALL be selected from live endpoint evidence, SHALL preserve the exact requested model ID, and SHALL use the versionless `http://localhost:20128/chat/completions` target in the current deployment. The failing versioned `http://localhost:20128/v1/chat/completions` route SHALL NOT be substituted for `sh/gpt-5.6-sol`.

#### Scenario: Native client incompatibility selects the proven fallback

- **WHEN** a bounded product-specific probe demonstrates that the installed client cannot decode the required native stream
- **THEN** the configuration MAY select a documented Chat Completions provider
- **AND** the provider SHALL target the empirically proven versionless route
- **AND** the evidence SHALL name the native decoder failure and the fallback route separately

#### Scenario: Native route passes

- **WHEN** the product-specific native probe returns the exact sentinel, supported thinking output, and required tool lifecycle
- **THEN** the native provider SHALL remain selected
- **AND** the change SHALL NOT downgrade it to Chat Completions merely for uniformity

### Requirement: Thinking configuration SHALL match the requested model and provider dialect

Each changed CLI SHALL declare reasoning/thinking only through fields supported by its native provider implementation. `pm/Claude-Fable` SHALL use Anthropic thinking controls or the CLI's documented Anthropic effort mapping; `sh/gpt-5.6-sol` SHALL use OpenAI Responses reasoning effort from `none`, `low`, `medium`, `high`, or `xhigh`. A client SHALL NOT send an OpenAI `reasoning.effort` field on the Anthropic Messages route or an Anthropic `thinking` body on the Responses route unless its documented adapter explicitly translates that field.

#### Scenario: PM thinking is separated from answer text

- **WHEN** a native Anthropic Messages client invokes `pm/Claude-Fable` with thinking enabled
- **THEN** the provider request SHALL use the client's Anthropic thinking control
- **AND** the response SHALL be parsed with thinking and answer content as separate semantic blocks where the client exposes them
- **AND** a successful final answer alone SHALL NOT be recorded as proof that thinking was enabled

#### Scenario: SH reasoning effort is accepted

- **WHEN** a native Responses client invokes `sh/gpt-5.6-sol` with `high` or `xhigh` effort
- **THEN** the request SHALL use the client's Responses reasoning control
- **AND** the response SHALL preserve reasoning/message separation or report the client's documented normalization
- **AND** an unsupported effort value SHALL be rejected or downgraded only according to the CLI's documented behavior

### Requirement: Installed CLI support SHALL be classified before mutation

The change SHALL maintain a matrix for every installed coding-agent CLI, including executable identity, version, effective configuration surface, native protocol support, credential mechanism, default identity, and ownership classification. Unsupported, unconfigured, vendor-auth-only, alias, and separate-change-owned surfaces SHALL remain unchanged unless a later evidence-backed task explicitly reclassifies them.

#### Scenario: Matrix prevents unsupported mutation

- **WHEN** a CLI has no documented custom endpoint or environment/provider surface that can express the requested route
- **THEN** its configuration SHALL remain unchanged
- **AND** the evidence SHALL record the exact observed reason and classification

#### Scenario: Alias is verified once

- **WHEN** multiple command names resolve to the same canonical executable
- **THEN** the matrix SHALL identify the canonical executable and avoid duplicate mutation or duplicate success claims

### Requirement: Native route acceptance SHALL be client-specific

A raw HTTP success SHALL establish gateway protocol availability only. A CLI route SHALL be accepted only after a bounded explicit client call proves the exact model selection, final assistant content, exit status, configured endpoint, thinking/reasoning behavior where supported, and tool-call lifecycle where supported. Explicit-route evidence SHALL remain distinct from configured-default evidence.

#### Scenario: Raw success is not promoted to CLI success

- **WHEN** a raw Messages or Responses probe returns HTTP 200
- **THEN** the corresponding CLI SHALL remain unverified until its native invocation is separately exercised
- **AND** the evidence SHALL preserve the raw protocol result and CLI result as separate dimensions

#### Scenario: Default route is checked separately

- **WHEN** an explicit OmniRoute model selector passes
- **THEN** the CLI SHALL still receive a no-provider/no-model sentinel probe
- **AND** the resulting default provider/model SHALL be recorded independently
- **AND** an existing default SHALL not be changed implicitly

### Requirement: Per-file rollback SHALL cover dialect regressions

Every user configuration file mutated by this change SHALL receive a mode-600 backup and byte hash before mutation. A parse failure, wrong endpoint, wrong model namespace, thinking mismatch, tool lifecycle failure, or client decoder regression SHALL trigger immediate atomic restoration of that file without reverting unrelated user changes.

#### Scenario: Dialect regression rolls back one file

- **WHEN** a post-apply sentinel proves that a CLI is using the wrong namespace or dialect
- **THEN** only that file SHALL be restored atomically from its pre-apply backup
- **AND** the CLI SHALL be reported as blocked or unchanged
- **AND** independent CLI verification SHALL continue
