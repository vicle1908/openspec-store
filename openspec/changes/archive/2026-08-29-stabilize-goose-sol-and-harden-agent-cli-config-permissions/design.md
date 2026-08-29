# Design: Stabilize Goose SOL transport and harden agent CLI config permissions

## Context

Goose 1.45.0 registers OmniRoute as a declarative custom provider
(`engine: "openai"`, `base_url: http://localhost:20128/v1`, `base_path: null`,
`supports_streaming: true`, `api_key_env: OMNIROUTE_API_KEY`) with four models:
`sh/gpt-5.6-sol`, `sh/Claude-Fable`, `ollamacloud/deepseek-v4-pro`, `ollamacloud/deepseek-v4-flash`.
The source tree matches the installed binary (workspace 1.45.0, tag
`v1.45.0-2-ga46e4b3`).

## Root cause (source-proven)

`goose-providers/src/openai.rs`:

- `is_openai_responses_model` (defined at
  `goose-provider-types/src/formats/openai.rs:1532`) regex:
  `(?:^|[-/])(?:o\d+(?:$|-)|gpt-5(?:$|[-.]))` — `sh/gpt-5.6-sol` matches via its
  `gpt-5` segment; `sh/Claude-Fable` does not.
- `should_use_responses_api(model, base_path)` (`goose-providers/src/openai.rs`:315):
  only the standard `v1/chat/completions` base path (`OPEN_AI_DEFAULT_BASE_PATH`)
  defers to model-based routing. A custom base path containing
  `chat/completions` forces the chat-completions dialect for every model on
  the provider.
- `derive_base_path("/v1")` → `v1/chat/completions`, so the current null
  `base_path` defers to the model predicate — SOL → Responses → strict
  decoder (`goose-provider-types/src/formats/openai_responses.rs`,
  `Failed to parse Responses stream event`) → heartbeat decode failure.

## Isolated matrix evidence (final; temp HOMEs; live hash-guarded)

| Variant | base_path | streaming | sh/gpt-5.6-sol | sh/Claude-Fable | ollamacloud/deepseek-v4-pro | ollamacloud/deepseek-v4-flash |
|---|---|---|---|---|---|---|
| A (baseline) | null | true | 0/3 (responses-decode) | 3/3 | 0/3 (400-catalog) | 0/3 (400-catalog) |
| B | v1/chat/completions | true | 0/3 (responses-decode) | 3/3 | — | — |
| C | chat/completions | true | 3/3 | 3/3 | 0/3 (400-catalog) | 0/3 (400-catalog) |
| D | null | false | 3/3 | 3/3 | 0/3 (400-catalog) | 0/3 (400-catalog) |

The ollamacloud 400 error is identical under A (current live behavior), C,
and D: `Model 'deepseek-v4-pro' is not available in the active live catalog for provider 'ollama-cloud'` — pre-existing OmniRoute catalog unavailability, not a
variant-caused regression. B is routing-equivalent to A (its base path is
the default constant, so it defers to the same model predicate).

Direct endpoint probes (`sh/gpt-5.6-sol`): `/v1/chat/completions` → 502;
`/chat/completions` → 200 with the expected sentinel; `/models` and
`/v1/models` → 200.

## Decision

1. The gate is baseline-relative: a candidate must not newly break any model
   that passed at baseline. Under this rule variant C is viable (`sh/gpt-5.6-sol`
   improves 0/3 → 3/3; `sh/Claude-Fable` stays 3/3; the ollamacloud failures are
   identical pre-existing 400s), and variant D is viable but with material
   `sh/Claude-Fable` latency (1–77s).
2. Preferred application is the **additive dedicated provider**
   `custom_omniroute_sh` (lower risk: the existing provider stays
   byte-identical): `engine`, `base_url`, `api_key_env`,
   `supports_streaming` mirror the live provider; `base_path` is
   `chat/completions`; models are exactly `sh/gpt-5.6-sol` and `sh/Claude-Fable`.
3. The dedicated provider passed its isolated proof in a temporary HOME:
   `sh/gpt-5.6-sol` 3/3 and `sh/Claude-Fable` 3/3 with real assistant content and nonzero
   usage; the unknown-provider negative control failed as expected
   (nonzero exit); one `sh/Claude-Fable` round via the original provider still
   passed (non-interference); the live provider hash was unchanged
   throughout; the new provider registers exactly `sh/gpt-5.6-sol` and `sh/Claude-Fable`
   with `engine: "openai"` and `base_path: chat/completions`. The
   fallback (variant C on the original provider, with a mode-600 backup and
   a single-field change) is retained only for the live application step
   should the added file misbehave.
4. The pre-existing ollamacloud catalog unavailability is recorded as a
   separate finding for OmniRoute-side catalog reconciliation; the goose
   registrations remain valid catalog entries per the archived change.
5. No goose default changes.

## Droid

`droid exec --help` (v0.202.0): `-m, --model <id>  Model ID to use
(default: claude-opus-5)`. `sessionDefaultSettings.model` governs
interactive sessions only, not `exec`. Both explicit OmniRoute custom models
pass. Disposition: document; require explicit `--model` or the existing
wrapper; no mutation.

## Permission hardening

Format-aware audit (JSON/JSONC/TOML parsed natively; YAML line-fallback),
presence-only, values never printed:

| File | Mode | Literal creds |
|---|---|---|
| `~/.pi/agent/mcp.json` | 644 | 1 (MCPR token) |
| `~/.config/opencode/opencode.json` | 644 | 2 (provider key + MCPR token) |
| `~/.kimi/config.toml` | 644 | 2 |
| `~/.kimi-code/config.toml` | 644 | 5 |

Already mode 600 with literal credentials (no action): `~/.factory/mcp.json`, `~/.cce/config.toml`, `~/.codex/config.toml`.
OMP `models.yml` credential fields are environment references, not
literals, so it is not a candidate.

Kimi's effective config is `~/.kimi-code/config.toml` (0.39.x); the legacy `~/.kimi/config.toml` is
hardened as well because it contains literals.

Rotation (user-owned, never automated): MCPR tokens, the OpenCode literal
provider key, and Kimi keys appeared in earlier session tool output.

## Risks / rollback

- The goose change is additive: one new provider file. Rollback = delete the
  file. The existing provider is hash-verified byte-identical before and
  after. (Fallback path: single-field change with mode-600 backup and atomic
  restore.)
- chmod changes permissions only; SHA-256 identity proven before/after;
  timestamped mode-600 backups kept outside Git until archive, then removed
  (they duplicate secrets).
- All probes run in isolated temp HOMEs first; live application is gated on
  the isolated matrix passing 3/3 per model.
