# Live Baseline Evidence: reconcile-omniroute-native-dialects

Captured 2026-08-29 (Asia/Ho_Chi_Minh). All values are value-blind. No API-key values, authorization headers, raw request bodies, or raw provider responses are retained.

## Gateway registry

- Endpoint: `http://localhost:20128`
- `GET /v1/models` with the shell-sourced gateway credential: HTTP 200
- Catalog size: 975 models
- `pm/*` rows: `pm/Claude-Fable`, `pm/Claude-Opus`, `pm/Claude-Sonnet`, `pm/default`
- `sh/*` rows: `sh/Claude-Fable`, `sh/Claude-Opus`, `sh/Claude-Sonnet`, `sh/codex`, `sh/codex-5.6`, `sh/codex-x`, `sh/default`, `sh/gpt-4o`, `sh/gpt-5.4`, `sh/gpt-5.5`, `sh/gpt-5.6`, `sh/gpt-5.6-sol`, `sh/o3`, `sh/o4-mini`
- `pm/Claude-Fable`: present; context 200,000; capabilities vision/tool calling/reasoning
- `sh/gpt-5.6-sol`: present; context 1,050,000; maximum output 128,000; capabilities vision/tool calling/reasoning/thinking; effort tiers `none`, `low`, `medium`, `high`, `xhigh`
- `pm/Claude-Fable[1m]`: absent from the catalog
- Invalid key against `/v1/models`: HTTP 401

## Native protocol probes

### `pm/Claude-Fable` through Anthropic Messages

- `POST /v1/messages`, non-stream: HTTP 200; model metadata `Claude-Fable`; separate thinking and text blocks in the long thinking probe; usage present; stop reason `end_turn`
- `POST /v1/messages`, stream: HTTP 200; 39 events; observed event kinds include `ping`, `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`; no malformed JSON notes
- Tool round-trip: first request HTTP 200 with `tool_use` for `get_weather`; continuation HTTP 200; final text reflected the supplied tool result

### `sh/gpt-5.6-sol` through OpenAI Responses

- `POST /v1/responses`, non-stream with reasoning effort `high`: HTTP 200; response model `gpt-5.6-sol`; output types `reasoning` and `message`; final text sentinel `pong`; usage present
- `POST /v1/responses`, stream: HTTP 200; 38 events; terminal event `response.completed`; no malformed JSON notes in the fast probe; `response.created.response.model` was absent
- Function round-trip: first request HTTP 200 with `get_weather`; continuation HTTP 200; final text reflected the supplied function output

## Fallback route probes

- Versioned `POST /v1/chat/completions` with `sh/gpt-5.6-sol`: HTTP 502
- Versionless `POST /chat/completions` with `sh/gpt-5.6-sol`: HTTP 200; final text sentinel `pong`
- Versionless `POST /chat/completions` with `pm/Claude-Fable`: HTTP 200; final text sentinel `pong`
- Versionless streaming chat requests returned HTTP 200 for both models; event fields are client-specific Chat Completions chunks and are not native Messages/Responses evidence

## Installed CLI identity and effective surfaces

| Product | Executable/version | Effective surface | Current relevant state | Mode |
|---|---|---|---|---|
| Claude Code | `~/.local/bin/claude`, 2.1.251 | `~/.claude/settings.json`, profiles, helpers, `~/.zshrc` | direct Anthropic provider; profile mechanism available | settings 0644 |
| Codex | `/opt/homebrew/bin/codex`, 0.150.1 | `~/.codex/config.toml` | `omniroute` Responses provider already present; top-level default is local Cockpit | 0600 |
| Grok Build | `~/.local/bin/grok`, 1.0.5 | `~/.grok/config.toml` | `omniroute` currently Chat Completions at `/v1`; models include `sh/gpt-5.6-sol` and `sh/Claude-Fable` | 0600 |
| goose | `/opt/homebrew/bin/goose`, 1.45.0 | `~/.config/goose/config.yaml`, `custom_providers/*.json` | dedicated `custom_omniroute_sh` chat provider exists; existing provider also contains SH rows | config 0644; dedicated file 0600 |
| Kimi Code | `/opt/homebrew/bin/kimi`, 0.39.0 | `~/.kimi-code/config.toml` | `omniroute` is OpenAI Chat; aliases point at `sh/gpt-5.6-sol` and `sh/Claude-Fable`; default is direct shopapikey | 0600 |
| Kilo | `~/.npm-global/bin/kilo`, 7.4.23 | `~/.config/kilo/kilo.jsonc` | one OpenAI-compatible `omniroute` provider; several SH models; default `omniroute/sh/codex` | 0600 |
| OpenCode | `/opt/homebrew/bin/opencode`, 1.18.25 | `~/.config/opencode/opencode.json` | one OmniRoute provider using `@ai-sdk/openai`, with per-model chat endpoint hints | 0600 |
| Pi | `/opt/homebrew/bin/pi`, 0.84.4 | `~/.pi/agent/models.json` | `omniroute` Responses provider contains SH models including `sh/Claude-Fable` | 0600 |
| Prime Agent | `/opt/homebrew/bin/prime-agent`, 0.8.1-beta.564.1 | `~/.prime/agent/models.json` | `omniroute` Responses provider contains `sh/codex` and `sh/gpt-5.6-sol` | 0600 |
| Droid | `/opt/homebrew/bin/droid`, 0.202.0 | `~/.factory/settings.json` | OmniRoute custom models use OpenAI provider for both SH rows | 0644 |
| omp | `/opt/homebrew/bin/omp`, 18.0.10 | `~/.omp/agent/models.yml`, `config.yml` | `omniroute` Responses provider contains the SH catalog including `sh/Claude-Fable`; no OmniRoute role assignment | models 0644, config 0600 |
| Cline | `/opt/homebrew/opt/nvm/.../cline`, installed | `~/.cline/data/settings/providers.json` | OpenAI-compatible and OpenAI-native entries; custom endpoint candidate | 0600 |
| GitHub Copilot CLI | `/opt/homebrew/bin/copilot`, 1.0.40 | `COPILOT_PROVIDER_*` BYOK environment surface | installed help documents OpenAI Responses and Anthropic BYOK | n/a |
| Cursor Agent | `~/.local/bin/cursor-agent`, 2026.07.09 | `~/.cursor/cli-config.json` | no custom base URL field observed | config 0644 |
| Auggie | `~/.npm-global/bin/auggie` | `~/.augment/.auggie.json` plus session auth | vendor session state only | config 0644 |
| Qoder | `~/.qoder/entry/qoder` | `~/.qoder/settings.json` | vendor model only; no custom provider block | config 0644 |
| agy/Antigravity | `/opt/homebrew/bin/agy`, 1.1.22 | `~/.gemini/antigravity*` | IDE/extension settings; no custom provider file | settings 0600 |

Aliases deduplicated: `codex`, `grok`, and `cursor-agent` each have multiple PATH entries; the first resolved canonical executable is recorded above. `kimi-code` and `fable-5` are product/skill names, not separate installed executables in this PATH.

## Pre-apply CLI probe findings

- Current OMP explicit Responses probe and current Pi one-shot probe exceeded a 180-second bound with no usable output; classify as lifecycle/extension startup findings, not gateway protocol evidence. No config mutation occurred.
- Current Kimi Code explicit route returned exit 1 after 28 seconds with upstream `503 Chat admission capacity is temporarily unavailable`; classify as provider capacity, not a model-ID correction.
- These bounded failures do not override the raw gateway validation and must be re-tested with isolated no-session/no-extension candidates before apply.

## Mechanical acceptance checks

- `/opt/homebrew/bin/python3 evidence/route-contract-check.py --phase baseline`: exit 1 with `SUMMARY FAIL phase=baseline`; this is the expected pre-apply negative control because the candidate contract is not yet present. Retained output: `evidence/baseline-route-contract-result.txt`.
- `/opt/homebrew/bin/python3 evidence/route-contract-check.py --phase candidate`: exit 1 before apply; expected stale/missing PM-native bindings and shell route were reported, while the active no-`dlg` invariant passed. The candidate phase is the post-apply green gate.
- `/opt/homebrew/bin/python3 evidence/inventory-check.py evidence/cli-inventory.json`: exit 0; 17 products resolved and classified, with alternate installations distinguished from same-target aliases.
- Evidence utilities passed `/opt/homebrew/bin/python3 -m py_compile`.
