# Design: pydantic-ai LLM Settings Integration

## Architecture

```
config.yaml / env vars
        │
        ▼
┌─────────────────────────┐
│  foundation/settings.py │
│  ModelSettings          │──── new fields: thinking, temperature,
│  (pydantic-settings)    │     max_tokens, service_tier
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  sdk/agents.py          │
│  build_agent()          │──── injects Thinking capability
│                         │     builds model_settings dict
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  _ai/agent.py           │
│  AgentRuntime           │──── passes model_settings to
│                         │     pydantic_ai.Agent.run()
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  pydantic_ai.settings   │
│  ModelSettings (dict)   │──── thinking, temperature, etc.
│  + Thinking capability  │──── provider-adaptive reasoning
└─────────────────────────┘
```

## Design Decisions

### 1. Thinking via Capability, not raw model_settings

**Decision:** Use `pydantic_ai.capabilities.Thinking` capability for thinking, not raw `model_settings={'thinking': ...}`.

**Rationale:** The Thinking capability handles provider translation automatically (Anthropic adaptive thinking, OpenAI reasoning_effort, etc.) without consumers needing provider-specific knowledge. It also supports the effort-level abstraction (`'minimal'`/`'low'`/`'medium'`/`'high'`/`'xhigh'`).

### 2. Settings layering: config defaults → per-call overrides

**Decision:** `build_agent()` merges config-level model_settings with per-call overrides. Config provides defaults; `model_settings` parameter on `run()`/`run_stream()` overrides.

**Rationale:** Consumers want sensible defaults from config but need runtime flexibility (e.g., "use high thinking for this complex query").

### 3. Provider-agnostic config keys

**Decision:** Expose `thinking`, `temperature`, `max_tokens`, `service_tier` as top-level config keys. Provider-specific settings (`anthropic_thinking`, `openai_reasoning_effort`) are exposed through `extra_model_settings` dict.

**Rationale:** Most consumers think in terms of "reasoning effort" not "Anthropic adaptive thinking budget_tokens." Provider-specific knobs belong in the escape hatch dict.

### 4. Clean-break: remove dead `AgentConfig.thinking`

**Decision:** Remove the unused `thinking: str | bool | None` field from `AgentConfig`.

**Rationale:** It was never wired to anything. Keeping it creates confusion about which mechanism controls thinking.

## New Settings Fields

### `ModelSettings` additions (foundation/settings.py)

```python
class ModelSettings(BaseSettings):
    # ... existing fields ...

    # NEW: LLM behavior defaults
    thinking: str | bool | None = None          # ThinkingLevel: True/'low'/'medium'/'high'/'xhigh'
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=1_000_000)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    service_tier: Literal['auto', 'default', 'flex', 'priority'] | None = None
    extra_model_settings: dict[str, Any] = {}   # Provider-specific escape hatch
```

### Config YAML shape

```yaml
model:
  primary: "anthropic:Advance"
  fallback: []
  # NEW fields
  thinking: "medium"           # or true/false/"low"/"high"/"xhigh"
  temperature: 0.7
  top_p: 0.9
  max_tokens: 4096
  service_tier: "auto"
  extra_model_settings:        # provider-specific overrides
    anthropic_thinking:
      type: "adaptive"
    openai_reasoning_summary: "detailed"
```

### Env var overrides

```bash
MODEL_THINKING=high
MODEL_TEMPERATURE=0.5
MODEL_TOP_P=0.9
MODEL_MAX_TOKENS=8192
MODEL_SERVICE_TIER=flex
```

### Thinking value mapping

The `thinking` field accepts these values:
- `true` → Thinking capability with default effort (provider decides)
- `false` → No Thinking capability injected (may be silently ignored for always-on models)
- `'minimal'` → Lowest reasoning effort
- `'low'` → Low effort (fast, fewer reasoning tokens)
- `'medium'` → Balanced effort
- `'high'` → High effort (thorough reasoning, more tokens)
- `'xhigh'` → Maximum effort (Anthropic only: Claude Opus 4.7+, Sonnet 5+)

## Why Not AgentSpec Directly?

pydantic-ai v2.18.0 has `Agent.from_file()` and `Agent.from_spec()` which accept `model_settings` directly. agent-core builds its own config layer because:

1. **Multi-provider resolution** — agent-core resolves proxies across giaoduc, cockpit, and shopapikey providers. AgentSpec doesn't know about TDT's provider map.
2. **TDT config integration** — settings come from `~/.tdt/config.yaml` with env var overrides, not from agent YAML files.
3. **Authority policy** — agent-core injects capability authority based on security policy. AgentSpec has no authority concept.
4. **Harness capabilities** — agent-core composes pydantic-ai-harness capabilities (Planning, SubAgents, etc.) alongside pydantic-ai capabilities. AgentSpec handles only built-in capabilities.
5. **Fallback chains** — agent-core's `FallbackModel` with configured fallback order. AgentSpec doesn't support this.

The config layer is a necessary integration point, not unnecessary abstraction.

## Merge Semantics

Config defaults → per-call overrides use **shallow merge** (last-write-wins for top-level keys):

```python
# Config defaults from ModelSettings
config_settings = {'temperature': 0.7, 'max_tokens': 4096}

# Per-call override replaces entire top-level keys
run_settings = {'temperature': 0.2}  # overrides temperature, keeps max_tokens

merged = {**config_settings, **run_settings}
# Result: {'temperature': 0.2, 'max_tokens': 4096}
```

Provider-specific nested dicts (e.g., `anthropic_thinking`) are NOT deep-merged. Callers who override should provide the complete value.

## Build Agent Flow

```python
def build_agent(
    profile=None, model=None, tools=None, toolsets=None,
    capabilities=(), authority_policy=None, name=None,
    instructions="", flavors=None,
    model_settings=None,      # NEW: per-call overrides
    thinking=None,            # NEW: explicit thinking override
):
    # 1. Resolve model (existing)
    # 2. Build Thinking capability from config + overrides
    # 3. Build model_settings dict from config defaults + overrides
    # 4. Pass model_settings to BaseAgent → AgentRuntime
```

## Security Hardening

### extra_model_settings validation

The `extra_model_settings` dict is a necessary escape hatch but must be validated:

```python
_EXTRA_MODEL_SETTINGS_BLOCKLIST = frozenset({
    'extra_headers',   # Could inject auth headers
    'extra_body',      # Could manipulate request body arbitrarily
})

_SENSITIVE_KEYS = frozenset({
    'api_key', 'secret', 'token', 'password', 'authorization'
})

@field_validator('extra_model_settings')
@classmethod
def _validate_extra_model_settings(cls, v: dict[str, Any]) -> dict[str, Any]:
    blocked = set(v.keys()) & _EXTRA_MODEL_SETTINGS_BLOCKLIST
    if blocked:
        raise ValueError(
            f"Blocked keys in extra_model_settings: {blocked}. "
            "Use provider-specific keys (anthropic_thinking, etc.)"
        )
    sensitive = {k for k in v if k.lower() in _SENSITIVE_KEYS}
    if sensitive:
        raise ValueError(f"Sensitive keys not allowed: {sensitive}")
    return v
```

### Serialization safety

`model_dump()` already excludes `api_key`. Add `extra_model_settings` to exclusion:

```python
def model_dump(self, **kwargs: Any) -> dict[str, Any]:
    kwargs.setdefault("exclude", set())
    if isinstance(kwargs["exclude"], set):
        kwargs["exclude"].update({"api_key", "extra_model_settings"})
    return super().model_dump(**kwargs)
```

### Range validators

```python
temperature: float | None = Field(default=None, ge=0.0, le=2.0)
max_tokens: int | None = Field(default=None, ge=1, le=1_000_000)
```

### Thinking compatibility warning

Log a warning when thinking is configured for a model that may not support it (e.g., non-reasoning models). The `Thinking` capability handles provider translation, but operators should know when their config may be ineffective.

## Testing Strategy

1. **Unit tests:** `ModelSettings` field validation, env var overrides, config.yaml loading
2. **Integration tests:** `build_agent()` produces correct capability list when thinking is configured
3. **Contract tests:** `model_settings` dict flows through to `AgentRuntime.run()` with correct merge semantics

## Compatibility

- **Backward compatible:** Existing `build_agent()` calls without new params work unchanged.
- **New fields are optional:** All additions default to `None`/empty, preserving current behavior.
- **`AgentConfig.thinking` removal is breaking:** Any code referencing this dead field will break — acceptable since it was never functional.
