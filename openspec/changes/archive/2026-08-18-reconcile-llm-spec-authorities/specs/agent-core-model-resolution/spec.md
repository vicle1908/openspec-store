## ADDED Requirements

### Requirement: Provider-specific reasoning effort validation sets

The canonical schema SHALL accept the union effort vocabulary (`minimal`, `low`, `medium`, `high`, `xhigh`, `max`) in `models.<alias>.reasoning_effort` and `defaults.reasoning_effort`. At route construction, agent-core SHALL validate the effort against the closed provider-specific set selected by the route's model kind: Anthropic routes SHALL accept `low`, `medium`, `high`, `max`; OpenAI Chat and OpenAI Responses routes SHALL accept `minimal`, `low`, `medium`, `high`, `xhigh`. An effort value that is schema-valid but unsupported by the selected model kind SHALL fail before credential access or model instantiation, identifying the model kind and the rejected value.

#### Scenario: Anthropic route rejects xhigh

- **GIVEN** a canonical model declares `reasoning_effort: xhigh`
- **AND** its route selects model kind `anthropic`
- **WHEN** the route behavior is validated for construction
- **THEN** construction SHALL fail identifying `xhigh` as unsupported for the Anthropic route
- **AND** no credential access or model instantiation SHALL occur

#### Scenario: OpenAI route rejects max

- **GIVEN** a canonical model declares `reasoning_effort: max`
- **AND** its route selects model kind `openai_chat` or `openai_responses`
- **WHEN** the route behavior is validated for construction
- **THEN** construction SHALL fail identifying `max` as unsupported for the OpenAI route

#### Scenario: Schema accepts the union vocabulary

- **GIVEN** canonical configuration declares any of `minimal`, `low`, `medium`, `high`, `xhigh`, or `max` as a reasoning effort
- **WHEN** canonical schema validation runs
- **THEN** the value SHALL be accepted at the schema layer
- **AND** provider-specific rejection SHALL occur only at route construction

#### Scenario: Effort maps to the provider-native request field

- **GIVEN** a route with a supported effort value
- **WHEN** request settings are built
- **THEN** Anthropic routes SHALL carry the effort as the Anthropic effort setting
- **AND** OpenAI routes SHALL carry the effort as the OpenAI reasoning effort setting
