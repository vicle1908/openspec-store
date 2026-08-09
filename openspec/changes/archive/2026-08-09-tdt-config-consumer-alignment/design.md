# Design: TDT Config Consumer Alignment

## Architecture

```text
~/.tdt/config.yaml / TDT_HOME override
        |
        v
load_settings() -> Settings
        |
        +--> create_model/create_fallback_model -> pydantic-ai Model
        |
        +--> _build_model_settings_from_config()
        |       -> temperature, max_tokens, top_p, service_tier
        |       -> flattened extra_model_settings
        |
        +--> _build_thinking_capability()
                -> public Thinking capability
        |
        v
BaseAgent(..., capabilities=thinking_capability)
        |
        v
BaseAgent.run(model_settings=configured_defaults)
```

## Decisions

### Reuse the SDK builders

The CLI SHALL reuse `_build_model_settings_from_config()` and
`_build_thinking_capability()` from the SDK consumer path. This prevents the CLI
and SDK from applying the same `ModelSettings` fields differently.

### Apply settings at agent execution

Pydantic AI's `infer_model()` constructs model/provider objects and does not
accept a `model_settings` argument. Behavior settings belong on the agent run.
The CLI therefore passes them to `BaseAgent.run(model_settings=...)`.

### Keep thinking capability-driven

`model.thinking` is converted to the public `Thinking` capability. It is not
inserted as a raw `thinking` key in `model_settings`. This matches the SDK path
and lets the active provider translate the capability.

### Flatten provider-specific extras

`extra_model_settings` is an escape-hatch mapping. Its entries are merged into
the top-level model-settings mapping rather than nested under an
`extra_model_settings` key.

### Preserve native fallback construction

`FallbackModel` continues receiving the primary and fallback model objects as
positional arguments. Behavior settings are applied once at the agent run and
therefore govern the selected model in the chain.

### Clean break from gateway YAML

`load_settings()` reads only the canonical `model:` section. A legacy `gateway:`
section is ignored; no compatibility fallback remains.

## Documentation Alignment

- Empty/default `api_mode` means the provider/client behavior is inferred from
  the model-kind prefix.
- Provider failover guidance has one canonical section.
- Historical research documents remain historical and are not active API docs.

## Security

Secrets remain referenced by `api_key_env`; no credential values are added to
YAML, tests, specifications, or review evidence.
