## MODIFIED Requirements

### Requirement: Provider configuration SHALL match the live protocol

Each Grok custom provider SHALL declare the protocol its configured model and endpoint actually serve. The OmniRoute PM provider SHALL use Anthropic Messages for `pm/Claude-Fable` at the Claude-Fable client-specific base URL `http://localhost:20128/v1` (Claude-Fable appends `/messages`, so the effective request is `POST http://localhost:20128/v1/messages`). The OmniRoute SH provider SHALL prefer OpenAI Responses for `sh/gpt-5.6-sol`; if Grok's installed strict decoder rejects the live Responses stream, the provider MAY use the proven versionless Chat Completions fallback with the exact SH model. A provider SHALL NOT claim Messages or Responses when its required fields are absent.

#### Scenario: OmniRoute native protocols are selected per namespace

- **WHEN** Grok's OmniRoute model aliases are inspected
- **THEN** the PM alias SHALL resolve to an `api_backend = "messages"` provider with `base_url = "http://localhost:20128/v1"`
- **AND** the SH alias SHALL resolve to an `api_backend = "responses"` provider with `base_url = "http://localhost:20128/v1"` when the native probe passes
- **AND** the SH alias SHALL resolve to a root `chat_completions` provider only when fallback evidence names the native decoder failure

#### Scenario: incompatible native response is recorded

- **WHEN** a Messages or Responses response omits fields required by Grok's decoder
- **THEN** the configuration SHALL select the compatible documented backend or remain unverified
- **AND** the evidence SHALL classify the failure as a protocol/decoder issue, not an authentication failure

#### Scenario: Chat Completions provider succeeds

- **WHEN** Grok CLI sends a streaming request through a provider configured for Chat Completions
- **THEN** the provider SHALL return parseable Chat Completions chunks and the CLI SHALL produce the assistant response without a serialization error

#### Scenario: Incompatible protocol is rejected or excluded

- **WHEN** a provider endpoint returns a response shape missing required Messages or Responses fields
- **THEN** the configuration SHALL NOT claim that incompatible backend, and verification SHALL record the endpoint and parser failure without classifying it as an authentication failure

### Requirement: OmniRoute SHALL use the canonical local API surface

The Grok OmniRoute registrations SHALL use port 20128 and the exact client-specific base URL: `http://localhost:20128/v1` for the Grok Messages and Responses providers because Grok appends the protocol path (`/messages` or `/responses`). The configured model IDs SHALL be `pm/Claude-Fable` and `sh/gpt-5.6-sol`. Existing providers and the selected default model SHALL remain unchanged unless explicitly approved.

#### Scenario: OmniRoute registration is verified

- **WHEN** Grok loads the corrected OmniRoute providers
- **THEN** it SHALL retain `OMNIROUTE_API_KEY` environment indirection
- **AND** it SHALL forward the exact PM or SH model ID without rewriting the namespace
- **AND** it SHALL not use `sh/Claude-Fable` as the PM Messages model

#### Scenario: fallback route is versionless and evidence-backed

- **WHEN** Grok cannot decode the SH Responses stream
- **THEN** the fallback provider SHALL target `http://localhost:20128/chat/completions`
- **AND** the versioned `/v1/chat/completions` route SHALL not be substituted for SH
- **AND** the native decoder failure and fallback sentinel SHALL both be retained

#### Scenario: OmniRoute service is stopped

- **WHEN** the local OmniRoute service is not listening
- **THEN** the request SHALL NOT complete against another provider or a rewritten model identifier
- **AND** the CLI SHALL surface a provider-specific connection failure after exhausting its retry budget

#### Scenario: OmniRoute model is unavailable

- **WHEN** the selected `sh/*` model identifier is not servable by the upstream package
- **THEN** the CLI SHALL surface the gateway's provider-specific error without substituting a different provider or model identifier

#### Scenario: OmniRoute credential is absent on the keyless route

- **WHEN** `OMNIROUTE_API_KEY` is unset and the deployment serves inference without a key
- **THEN** the request MAY complete on the configured endpoint and model identifier
- **AND** the CLI SHALL NOT route the request to another provider or rewrite the model identifier
