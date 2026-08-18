## MODIFIED Requirements

### Requirement: Explicit typed provider protocol

Every provider MUST declare its protocol. The closed protocol vocabulary is `messages` (Anthropic Messages), `openai_chat` (OpenAI Chat Completions), and `responses` (OpenAI Responses). The protocol determines the API format used for model requests. Inference or defaulting of protocol type SHALL NOT occur.

#### Scenario: Protocol is explicitly declared

- **WHEN** a provider is configured
- **THEN** it MUST include an explicit `protocol` field
- **AND** the protocol MUST be one of `messages`, `openai_chat`, or `responses`

#### Scenario: OpenAI Chat protocol is accepted

- **GIVEN** a provider declared with `protocol: openai_chat`
- **WHEN** the YAML is loaded and validated
- **THEN** the provider SHALL be accepted
- **AND** the protocol SHALL map to the OpenAI Chat Completions wire format

#### Scenario: Unknown protocol is rejected

- **GIVEN** a provider declared with a protocol value outside the closed vocabulary
- **WHEN** the YAML is loaded and validated
- **THEN** validation SHALL fail with the unsupported protocol value identified
