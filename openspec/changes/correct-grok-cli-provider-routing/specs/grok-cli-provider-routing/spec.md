## Purpose

Define reliable, observable routing for Grok CLI custom providers so configured gateways use compatible streaming protocols, environment-backed credentials, and verified model identifiers without silently falling back.

## ADDED Requirements

### Requirement: Provider configuration SHALL match the live protocol

Each custom provider SHALL declare the protocol that its live endpoint actually serves. Providers returning streaming Chat Completions events SHALL use the Chat Completions backend; Messages or Responses backends SHALL NOT be used when their required response fields are absent.

#### Scenario: Chat Completions provider succeeds

- **WHEN** Grok CLI sends a streaming request through a provider configured for Chat Completions
- **THEN** the provider SHALL return parseable Chat Completions chunks and the CLI SHALL produce the assistant response without a serialization error

#### Scenario: Incompatible protocol is rejected or excluded

- **WHEN** a provider endpoint returns a response shape missing required Messages or Responses fields
- **THEN** the configuration SHALL NOT claim that incompatible backend, and verification SHALL record the endpoint and parser failure without classifying it as an authentication failure

### Requirement: OmniRoute SHALL use the canonical local API surface

The OmniRoute provider SHALL use `http://localhost:20128/v1`, reference `OMNIROUTE_API_KEY` through environment indirection, and use a live `sh/*` model identifier. Existing providers and the selected default model SHALL remain unchanged unless explicitly approved.

#### Scenario: OmniRoute registration is verified

- **WHEN** Grok CLI loads the OmniRoute provider
- **THEN** it SHALL resolve the environment-backed credential, query `/v1/models` at port 20128, and forward an approved exact `sh/*` model identifier

#### Scenario: OmniRoute is unavailable

- **WHEN** the local service is stopped, the credential is absent, or the selected model is unavailable
- **THEN** the CLI SHALL report a provider-specific failure and SHALL NOT silently send the request to another provider or rewrite the model identifier

### Requirement: Credentials SHALL remain external to configuration artifacts

Provider API keys SHALL be supplied through documented environment-variable references and SHALL NOT be written as literal values to Grok CLI configuration, OpenSpec artifacts, logs, process arguments, or verification evidence.

#### Scenario: Credential indirection is loaded

- **WHEN** a configured provider is invoked from a shell that exports its declared environment variable
- **THEN** the CLI SHALL resolve the credential and authenticate the request without exposing its value in output or evidence

#### Scenario: Credential is missing

- **WHEN** the declared environment variable is unset
- **THEN** the provider request SHALL fail clearly without leaking another provider credential or mutating the configuration

### Requirement: Routing changes SHALL have real-call and tool-call evidence

A provider configuration SHALL be considered verified only after a bounded one-turn sentinel call succeeds and, for coding-agent routes, a disposable tool-call probe succeeds. Evidence SHALL record statuses, model IDs, backend, and sanitized outcomes only.

#### Scenario: Text and tool calls succeed

- **WHEN** a provider is tested with a sentinel text request and a disposable tool request
- **THEN** both calls SHALL complete successfully with the expected marker and no authentication, reconnect, or serialization error

#### Scenario: Verification fails

- **WHEN** a sentinel or tool-call probe fails
- **THEN** the provider SHALL remain flagged as unverified and the failure category SHALL be recorded without retaining credentials or raw sensitive responses
