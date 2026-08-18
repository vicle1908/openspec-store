## Why

The canonical LLM specs contain four spec-text accuracy bugs that contradict the
implemented code. The `reconcile-agent-llm-contract-and-acceptance-v3` change
(2026-08-17) aligned the *implementation* across 6 repos but left the *spec text*
carrying stale claims. These bugs cause readers to reach wrong conclusions about
what the system actually supports, and they create false "conflicts" between specs
that don't exist in code.

## What Changes

- **Fix protocol enum in master spec**: `provider-model-profile-resolution` says
  protocol MUST be `messages` or `responses`, but the code enum
  (`tdt_core/provider_model_profile.py:27`) has three values: `messages`,
  `openai_chat`, `responses`. Add `openai_chat` to the spec text.

- **Correct registry claim in master Purpose**: The master spec Purpose says the
  canonical schema "replaces the separate packaged `environment-key-registry.json`".
  Reality: `auth_env`+canonical schema replaced only the `api_key_env` YAML field.
  The registry itself is still active (18 entries, loaded by
  `EnvironmentKeyRegistry.from_resource()`, used by `credential_entry()` and
  `resolve_agent_profile()`). Correct the Purpose to state what was actually replaced.

- **Document provider-specific effort split**: The canonical schema accepts all 6
  effort values (`minimal, low, medium, high, xhigh, max`), but agent-core validates
  against provider-specific sets at construction time: OpenAI accepts
  `{minimal, low, medium, high, xhigh}` (no `max`), Anthropic accepts
  `{low, medium, high, max}` (no `minimal`/`xhigh`). Neither spec documents this
  two-layer design. Add it to `agent-core-model-resolution`.

- **Clarify Claude Code spec authority**: Two specs govern Claude Code provider
  selection through different mechanisms (`claude-code-provider-routing` via env-var
  launchers, `claude-code-provider-profile-resolution` via settings.json + apiKeyHelper).
  Neither states which owns what. Add a cross-reference and authority statement to both.
  Also fix the TBD Purpose in `claude-code-provider-profile-resolution`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `provider-model-profile-resolution`: Add `openai_chat` to the protocol enum
  requirement; correct the Purpose statement about what the registry was replaced by.
- `agent-core-model-resolution`: Add provider-specific effort validation sets to the
  "Canonical route behavior and run settings" requirement.
- `claude-code-provider-routing`: Add authority statement clarifying relationship to
  `claude-code-provider-profile-resolution`.
- `claude-code-provider-profile-resolution`: Fix TBD Purpose; add authority statement
  clarifying relationship to `claude-code-provider-routing`.
- `register-custom-provider-credentials`: Update scenarios from the retired
  `providers.*.api_key_env` field to the canonical `providers.*.auth_env` field, and
  describe the actual runtime validation mechanism (`CredentialResolver.resolve()`
  over provider-bound route references) instead of a registry lookup at resolution
  time (`credential_entry()` has zero callers in the ecosystem).

## Impact

- **Specs only** — no code changes. All four fixes correct spec text to match
  already-implemented behavior.
- **No breaking changes** — the code is already correct; this aligns documentation.
- **Affected specs**: 5 canonical LLM specs in `openspec/specs/`.
- **Ownership**: tdt-core (protocol enum, registry), agent-core (effort split),
  Claude Code config (launcher vs profile authority).
