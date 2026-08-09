# agent-core-model-resolution (Delta)

## ADDED Requirements

### Requirement: Model Settings Propagation

CLI agents SHALL apply `ModelSettings` behavior fields (`thinking`, `temperature`,
`max_tokens`, `top_p`, `service_tier`, `extra_model_settings`) to the runtime
model via pydantic-ai's model settings API.

#### Scenario: CLI agent uses behavior settings

- Given `~/.tdt/config.yaml` contains `model.thinking: high` and `model.temperature: 0.7`
- When a CLI agent (review, propose, explore) is invoked
- Then the runtime model SHALL receive `thinking: "high"` and `temperature: 0.7`

#### Scenario: No behavior settings configured

- Given `~/.tdt/config.yaml` has no `thinking`, `temperature`, etc. under `model:`
- When a CLI agent is invoked
- Then the runtime model SHALL use pydantic-ai defaults (no `model_settings` kwarg)

### Requirement: Fallback Model Settings Consistency

When `create_fallback_model()` receives a `model_settings` dict, ALL models
in the fallback chain (primary + fallbacks) SHALL receive the same settings.

#### Scenario: Fallback chain receives consistent settings

- Given `create_fallback_model("anthropic:Advance", ["nhà cung cấp dịch vụ AI-chat:gpt-4o"], model_settings={"thinking": "high"})`
- When the FallbackModel is created
- Then both the primary and fallback models SHALL have `thinking: "high"` applied
