# Design: claude-code-model-effort-alias-routing

## Scope and Ownership

This is a successor to `claude-code-three-provider-routing`. It owns only the provider model-selection/effort contract and the cockpit adapter's effort translation. The shell surface is `~/.zshrc`; the code surface is `~/Developer/claude-code-provider-adapter`; the specification surface is this change in `~/Developer/openspec-store`.

The adapter containerization change is a separate completed change. This design assumes the existing healthy adapter container and `cockpit_up`/`cockpit_down` lifecycle helpers remain in place.

## Claude Code Configuration Contract

Claude Code v2.1.227 resolves model and effort independently:

1. `ANTHROPIC_MODEL` selects an alias or provider model ID. It accepts `[1m]` suffixes for extended context.
2. `ANTHROPIC_DEFAULT_FABLE_MODEL` pins the provider model used by the built-in `fable` alias.
3. `ANTHROPIC_CUSTOM_MODEL_OPTION` registers one provider-specific ID as a custom model-picker entry.
4. The matching `_SUPPORTED_CAPABILITIES` variable is an allowlist. Only the capabilities needed for the requested effort are declared here.
5. `CLAUDE_CODE_EFFORT_LEVEL` overrides the session effort and is the correct mechanism for `max`, which is not accepted as a persistent `effortLevel` settings-file value.

### `[1m]` Suffix Semantics

The `[1m]` suffix is a Claude Code context-window hint. It is stripped before the provider request. The wire model IDs are the bare base names without the suffix.

```
Claude selector:  fable[1m]
Pinned model:     fable-5[1m]
Wire model:       fable-5          (suffix stripped by Claude Code)
```

This is confirmed for all three profiles by local request capture.

The adapter does NOT need to handle `[1m]` because the suffix never reaches it.

## Launcher Environment Contract

```sh
# shopapikey: official family alias -> provider-specific Fable ID with 1M context
ANTHROPIC_BASE_URL=https://api.phanmemvip.shop
ANTHROPIC_MODEL=fable[1m]
ANTHROPIC_DEFAULT_FABLE_MODEL=fable-5[1m]
ANTHROPIC_DEFAULT_FABLE_MODEL_SUPPORTED_CAPABILITIES=effort,xhigh_effort
CLAUDE_CODE_EFFORT_LEVEL=xhigh

# giaoduc: custom provider model ID with 1M context
ANTHROPIC_BASE_URL=https://api.giaoduc.online
ANTHROPIC_MODEL=Advance[1m]
ANTHROPIC_CUSTOM_MODEL_OPTION=Advance[1m]
ANTHROPIC_CUSTOM_MODEL_OPTION_NAME=Advance 1M
ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES=effort,xhigh_effort
CLAUDE_CODE_EFFORT_LEVEL=xhigh

# cockpit: custom provider model ID through adapter with 1M context
ANTHROPIC_BASE_URL=http://localhost:8787
ANTHROPIC_MODEL=gpt-5.6-luna[1m]
ANTHROPIC_CUSTOM_MODEL_OPTION=gpt-5.6-luna[1m]
ANTHROPIC_CUSTOM_MODEL_OPTION_NAME=gpt-5.6-luna 1M
ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES=effort,max_effort
CLAUDE_CODE_EFFORT_LEVEL=max
```

`CLAUDE_CODE_ALWAYS_ENABLE_EFFORT` is intentionally not set. Local capture proved that the capability declarations cause Claude Code to emit `output_config.effort` without that fallback switch. Adding it would broaden the request behavior unnecessarily.

The auth variable remains profile-specific:

```sh
ANTHROPIC_AUTH_TOKEN="$HERMES_CUSTOM_SHOPAPIKEY_API_KEY"
ANTHROPIC_AUTH_TOKEN="$HERMES_CUSTOM_GIAODUC_API_KEY"
ANTHROPIC_AUTH_TOKEN="$HERMES_CUSTOM_COCKPIT_API_KEY"
```

No value may be copied into a tracked file or OpenSpec artifact.

## Request-Shape Evidence

With the exact minimal capability declarations above, Claude Code sent these top-level request fields to a local capture endpoint:

| Profile | Selector sent to Claude Code | Wire model in request | Effort |
|---|---|---|---|
| shopapikey | `fable[1m]`, pinned `fable-5[1m]` | `fable-5` | `output_config.effort=xhigh` |
| giaoduc | `Advance[1m]` | `Advance` | `output_config.effort=xhigh` |
| cockpit | `gpt-5.6-luna[1m]` | `gpt-5.6-luna` | `output_config.effort=max` |

`thinking={type: adaptive, display: omitted}` and the effort beta header were also present. `CLAUDE_CODE_ALWAYS_ENABLE_EFFORT` was not set.

The adapter MUST treat `output_config.effort` as the source of truth for effort. It MUST NOT infer effort from model names or from the `thinking` display field.

## Adapter Translation

Current translation builds this subset:

```json
{
  "model": "gpt-5.6-luna",
  "input": [],
  "max_output_tokens": 64,
  "stream": false,
  "tools": []
}
```

The implementation SHALL add only the supported Responses field when present:

```json
{
  "reasoning": {"effort": "max"}
}
```

Mapping rules:

1. Read `body.get("output_config", {}).get("effort")`.
2. If the value is one of `low`, `medium`, `high`, `xhigh`, or `max`, emit `reasoning: {"effort": value}`.
3. If `output_config` is absent, omit `reasoning` and preserve existing behavior.
4. Do not forward `output_config`, `thinking`, `context_management`, or Claude-specific metadata to the Responses endpoint.
5. A malformed or unsupported effort value is a client error (HTTP 400) rather than an unvalidated upstream request.
6. Apply the same mapping for streaming and non-streaming requests because both use `_build_responses_body()`.

The direct cockpit probe already established that `reasoning.effort=max` is accepted: HTTP 200, Responses object, completed status, and exact sentinel. After implementation, the adapter probe MUST show the same field in the outbound body, and the real adapter request MUST still complete.

## Launcher Isolation and Reset

Each launcher keeps its assignments in a subshell and executes `claude "$@"`. The caller's shell MUST NOT retain another profile's model, base URL, custom option, or effort after the function exits.

`claude_reset()` MUST unset:

- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_AUTH_TOKEN`
- `ANTHROPIC_MODEL`
- `ANTHROPIC_DEFAULT_FABLE_MODEL`
- `ANTHROPIC_DEFAULT_FABLE_MODEL_SUPPORTED_CAPABILITIES`
- `ANTHROPIC_CUSTOM_MODEL_OPTION`
- `ANTHROPIC_CUSTOM_MODEL_OPTION_NAME`
- `ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION`
- `ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES`
- `CLAUDE_CODE_EFFORT_LEVEL`

It MUST preserve unrelated settings and the existing `cockpit_up`/`cockpit_down` helpers.

## Verification Order

1. Add a failing unit test for `output_config.effort` translation.
2. Implement the smallest adapter mapping and make the focused suite green.
3. Update launcher functions and run `zsh -n ~/.zshrc`.
4. Run a local capture for all three profiles and assert exact model/effort pairs. Verify wire models are bare base names without `[1m]`.
5. Run real shopapikey acceptance.
6. Run real cockpit direct and through the adapter, including the effort-mapping probe.
7. Retry giaoduc only after the provider-side burst lock has cleared; record HTTP status, resolved model, and sentinel.
8. Run focused OpenSpec validation, then full-store validation and store hygiene checks.

## Known Blocks

- Giaoduc live acceptance cannot be considered green while the provider reports the account burst lock.
- Existing adapter end-to-end text success is not effort evidence until the outbound `reasoning.effort` field is observed.
- The original routing change's checked tasks are historical evidence for its earlier contract; they do not satisfy this successor's alias/effort gates.
- `[1m]` does not prove the upstream provider supports 1M context; it only proves Claude Code accepted the selector without error. Provider-side 1M capacity must be verified separately if needed.
