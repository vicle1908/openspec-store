# Design: OmniRoute Namespace-to-Dialect Reconciliation

## Design principles

1. **The namespace is part of the route contract.** `pm/Claude-Fable` and `sh/gpt-5.6-sol` are not interchangeable aliases.
2. **Native protocol first.** Use Anthropic Messages for `pm/Claude-Fable` and OpenAI Responses for `sh/gpt-5.6-sol` when the consumer has a documented native surface.
3. **Fallback is evidence-driven.** A client may use versionless Chat Completions only after its native path is shown to be incompatible; the fallback must retain the exact requested model ID and must not be described as native Messages or Responses.
4. **Thinking is a separate acceptance axis.** Connectivity, final text, reasoning separation, tool calls, and stream lifecycle are recorded independently.
5. **Registration is not default selection.** Existing defaults and non-OmniRoute providers remain unchanged unless separately approved.
6. **One writer per file.** Every changed file receives a mode-600 backup and hash, an atomic replacement, parse validation, a real sentinel, and immediate rollback on failure.
7. **No framework workarounds.** Vendor binaries, bundled source, and OmniRoute Docker artifacts are read-only evidence surfaces.

## Live gateway baseline

Captured 2026-08-29 from `http://localhost:20128`:

| Check | Result |
|---|---|
| `GET /v1/models` with the shell-sourced gateway credential | HTTP 200; 975 models |
| `pm/Claude-Fable` catalog row | Present; context 200,000; vision/tool/reasoning |
| `sh/gpt-5.6-sol` catalog row | Present; context 1,050,000; max output 128,000; vision/tool/reasoning/thinking; effort `none/low/medium/high/xhigh` |
| `POST /v1/messages` with `pm/Claude-Fable`, non-stream | HTTP 200; Anthropic response with thinking and text blocks; usage present |
| `POST /v1/messages` with `pm/Claude-Fable`, stream | HTTP 200; `ping → message_start → content_block_start/delta/stop → message_delta → message_stop` |
| `pm/Claude-Fable` Messages tool round-trip | HTTP 200 tool call, HTTP 200 continuation, tool result reflected in final text |
| `POST /v1/responses` with `sh/gpt-5.6-sol`, non-stream | HTTP 200; `model=gpt-5.6-sol`; reasoning and message output; usage present |
| `POST /v1/responses` with `sh/gpt-5.6-sol`, stream | HTTP 200; 38 events; terminal `response.completed`; fast stream had no malformed JSON |
| `sh/gpt-5.6-sol` Responses function round-trip | HTTP 200 function call, HTTP 200 continuation, tool result reflected in final text |
| versioned `/v1/chat/completions`, `sh/gpt-5.6-sol` | HTTP 502; not an approved fallback |
| versionless `/chat/completions`, `sh/gpt-5.6-sol` | HTTP 200; exact sentinel |
| versionless `/chat/completions`, `pm/Claude-Fable` | HTTP 200; exact sentinel |
| invalid key against `/v1/models` | HTTP 401 |

The current deployment is loopback-only and inference can be keyless while model discovery remains authenticated. The configuration still uses the external `OMNIROUTE_API_KEY` reference wherever the consumer supports it.

## Thinking and stream caveats

- `pm/Claude-Fable` accepts Anthropic thinking requests and returned a separate thinking block plus a text block in a long bounded probe. Native Anthropic clients SHALL expose their documented thinking/effort control rather than injecting an OpenAI `reasoning.effort` field.
- `sh/gpt-5.6-sol` accepted Responses `reasoning.effort=high` and returned a reasoning output item plus a message. Native Responses clients SHALL map their high/xhigh controls only to the live effort set.
- OmniRoute Responses streaming has a known slow-phase defect: a heartbeat can omit required `response` and `sequence_number` fields, and `response.created` can omit the nested model. Strict client decoders must use the proven versionless chat route or remain blocked; no vendor bundle hotfix is allowed.
- The catalog has no `pm/Claude-Fable[1m]` row. Client-local selectors such as Claude Code's historical `[1m]` convention must not be sent as the OmniRoute wire model unless a fresh client probe proves that the suffix is stripped before transmission.

## Consumer matrix and ownership

| Product | Installed surface | Preferred route | Fallback/decision | Ownership |
|---|---|---|---|---|
| Claude Code 2.1.251 | `~/.claude/settings.json`, `~/.claude/profiles/`, `~/.claude/helpers/`, `~/.zshrc` | `pm/Claude-Fable` via Anthropic Messages; dedicated profile/helper/launcher — applied live by the archived owner | Do not force `sh/gpt-5.6-sol`; Claude Code is an Anthropic Messages consumer | Externally owned by archived `2026-08-30-add-claude-code-omniroute-pm-launcher`; this change: verify/preserve only (task 4.1 scope note) |
| Codex 0.150.1 | `~/.codex/config.toml` | `sh/gpt-5.6-sol` via `model_providers` Responses and a selectable profile | No native Messages surface; do not register PM as if it were Messages | This change; preserve top-level default |
| Grok Build 1.0.5 | `~/.grok/config.toml` | PM Messages candidate; SH Responses candidate | If strict Responses parsing fails, use root/versionless Chat Completions for SH; retain exact `sh/gpt-5.6-sol` | This change |
| goose 1.45.0 | `~/.config/goose/custom_providers/*.json` | PM custom `anthropic` engine; SH custom `openai` Responses candidate | Installed strict Responses decoder is known to reject OmniRoute slow heartbeat/model shape; use dedicated versionless chat provider for SH, and PM only if native probe passes | This change; no goose source edits |
| Kimi Code 0.39.0 | `~/.kimi-code/config.toml` | Separate `anthropic` PM provider and `openai_responses` SH provider | Kimi Code does not read shell env vars as provider credentials; retain existing mode-600 literal-key exception if required | This change; legacy `~/.kimi/config.toml` is inactive and separately classified |
| Kilo 7.4.23 | `~/.config/kilo/kilo.jsonc` | Official custom provider APIs: Anthropic Messages PM and OpenAI Responses SH | If installed runtime rejects one native provider, add only the proven root chat fallback for that model | This change |
| OpenCode 1.18.25 | `~/.config/opencode/opencode.json` | `@ai-sdk/anthropic` PM and `@ai-sdk/openai` SH Responses | Per-model/provider package override; fallback to `@ai-sdk/openai-compatible` only if native probe fails | This change |
| Pi 0.84.4 | `~/.pi/agent/models.json` | Separate `anthropic-messages` PM and `openai-responses` SH providers | Fallback `openai-completions` only for a client-specific decoder issue | This change; keep MCP config untouched |
| Prime Agent 0.8.1-beta.564.1 | `~/.prime/agent/models.json` | Separate `anthropic-messages` PM and `openai-responses` SH providers | No default change; provider IDs remain selectable | This change; supersedes the archived narrow change's stale single-provider assumption |
| Droid 0.202.0 | `~/.factory/settings.json` | Custom model `provider=anthropic` PM and `provider=openai` SH | If the installed OpenAI custom path is chat-only, use `generic-chat-completion-api` at the proven root path; verify before changing | This change; no bare-exec default change |
| omp 18.0.10 | `~/.omp/agent/models.yml` | Separate `anthropic-messages` PM and `openai-responses` SH providers | Chat fallback only after native client probe; do not assign OmniRoute to roles without approval | This change |
| Cline 1.x installed CLI | `~/.cline/data/settings/providers.json` and `cline auth` | Native Anthropic/OpenAI-compatible surface is a candidate | Persistent key handling and exact provider schema must pass an isolated probe; otherwise leave unchanged or use a documented wrapper | This change only if proven |
| GitHub Copilot CLI 1.0.40 | Environment-based BYOK (`COPILOT_PROVIDER_*`) | PM with `COPILOT_PROVIDER_TYPE=anthropic`; SH with `TYPE=openai`, `WIRE_API=responses` — both proven via env opt-in probes | Persistent `.zshrc` launchers DEFERRED (`.zshrc` is protected by other active changes); the proven route remains `COPILOT_PROVIDER_*` environment opt-in; no global env default change | No `.zshrc` write by this change; COPILOT opt-in surface preserved only (task 4.5 scope note) |
| Cursor Agent 2026.07.09 | `~/.cursor/cli-config.json` | None identified | No documented custom base URL in installed CLI; unchanged | Out of scope/unchanged |
| Auggie 0.36+ | `~/.augment/.auggie.json` plus OAuth session | None identified | Vendor session endpoint; unchanged | Out of scope/unchanged |
| Qoder | `~/.qoder/settings.json` | None identified | Current config has vendor model only; unchanged | Out of scope/unchanged |
| Antigravity/agy | `~/.gemini/antigravity*` | None identified | IDE/extension state, no custom provider file; unchanged | Out of scope/unchanged |
| Gemini/fable-5 executable | Not installed on PATH | None | No executable to configure; Kimi Code is separately covered | Out of scope |

The matrix is a classification, not a claim that every preferred route has already passed its product-specific CLI probe. Product-specific probes are an apply gate.

### Version drift reconciliation (2026-08-30)

The consumer matrix records planning-time versions. Current zsh-resolved canonicals (`evidence/cli-inventory.json`): codex 0.151.0 (matrix: 0.150.1), cursor-agent 2026.08.25 (matrix: 2026.07.09), omp 18.0.11 (matrix: 18.0.10), pi 0.84.4 (matrix: 0.84.4 — current). Codex's profile mechanism is version-sensitive and was re-probed on the resolved 0.151.0 binary with PASS (`evidence/codex-profile-mechanism-result.json`: positive arm rc=0 with exact sentinel; negative and no-flag controls rc=1, no public host contact), so no matrix assumption depends on 0.150.x-only behavior. Cursor Agent is an out-of-scope unchanged surface; its version drift is cosmetic with no route impact. The pi/omp upgrades change no candidate template contract; the binding gate is post-apply live verification on the current binaries (tasks 5.1–5.4). Matrix version cells are retained as historical capture values.

## Per-CLI protocol and thinking acceptance map

The following table is the executable decision contract for candidate probes. A row is not eligible for live apply until its native route or its named fallback has a captured result.

| Product | PM provider field and expected wire shape | SH provider field and expected wire shape | Thinking assertion | Fallback criterion |
|---|---|---|---|---|
| Claude Code | profile `ANTHROPIC_BASE_URL=http://localhost:20128`, `ANTHROPIC_MODEL=pm/Claude-Fable`, `apiKeyHelper`; Anthropic `message_start` plus thinking/text blocks | Not forced: Claude Code is an Anthropic Messages client and SH Messages timed out | `CLAUDE_CODE_EFFORT_LEVEL` is session control; proof requires a thinking block or documented client normalization | No SH registration if Messages-only; do not mislabel a chat route as Claude-native |
| Codex | No native Messages field; PM is not registered as a Messages route | `model_providers.<id>.wire_api=responses`, `base_url=.../v1`, model `sh/gpt-5.6-sol`; Responses reasoning/message output | `model_reasoning_effort=high|xhigh`, `model_reasoning_summary=detailed`; proof requires response completion and reasoning metadata | No Chat fallback in Codex unless a future Codex release documents one |
| Grok | `api_backend=messages`, provider base `http://localhost:20128/v1` (Grok adds the `/messages` path), model `pm/Claude-Fable`; parse streaming Messages output | Preferred `api_backend=responses`, `/v1` base, model `sh/gpt-5.6-sol`; parse `response.completed` and model/text | PM: native thinking event; SH: Responses reasoning event with `high|xhigh` | If Grok reports `serialization error: missing field model` or equivalent on SH Responses, use `api_backend=chat_completions` with root base and record exact error |
| goose | `engine=anthropic`, root base URL, `pm/Claude-Fable`; Anthropic stream parser | Preferred `engine=openai`, `/v1` base, `sh/gpt-5.6-sol`; current strict decoder is known to reject slow Responses heartbeat/model shape | `preserves_thinking=true` for Anthropic; `GOOSE_THINKING_EFFORT`/OpenAI reasoning only where runtime emits it | If Responses decoder fails, dedicated `engine=openai`, `base_path=chat/completions` root-effective provider; PM may use native only if its probe passes |
| Kimi Code | provider `type=anthropic`, root base, alias model `pm/Claude-Fable`; `capabilities` includes `thinking` and `tool_use` | provider `type=openai_responses`, `/v1` base, alias model `sh/gpt-5.6-sol`; `capabilities` includes `thinking` and `tool_use` | alias `default_effort=high`, top-level `thinking.enabled=true`, `effort=xhigh`; inspect normalized stream | Native types are supported; fallback only if a native decoder failure is reproduced |
| Kilo | provider `npm=@ai-sdk/anthropic`, baseURL `/v1` (SDK emits `/v1/messages`), PM model; model `options.thinking.type=enabled` and budget | provider `npm=@ai-sdk/openai`, `/v1` base, SH model; model reasoning options use Responses fields | PM `thinking.budgetTokens`; SH `reasoningEffort=high`, `reasoningSummary=auto`; structured output must retain reasoning/message separation | Replace only the failed model with `@ai-sdk/openai-compatible` at the client-appropriate root or versionless endpoint and exact model ID |
| OpenCode | provider `npm=@ai-sdk/anthropic`, baseURL `/v1` (SDK emits `/v1/messages`), PM model; Anthropic thinking options | provider `npm=@ai-sdk/openai`, `/v1` base, SH model; Responses model options | PM `thinking.type=enabled`, `budgetTokens`; SH `reasoningEffort=high`, `reasoningSummary=auto` | Per-model `@ai-sdk/openai-compatible` only after native package failure; use the proven client-appropriate root/versionless endpoint and exact model ID |
| Pi | `api=anthropic-messages`, root base, PM model; parse `thinking` content | `api=openai-responses`, `/v1` base, SH model; parse reasoning/message events | PM provider/model reasoning true; SH `thinkingLevelMap` maps only live tiers (`off→none`, `low/medium/high/xhigh` as supported) | `openai-completions` only for a client-specific decoder regression |
| Prime Agent | provider `api=anthropic-messages`, root base, PM model, env-name credential | provider `api=openai-responses`, `/v1` base, SH model, env-name credential | `--thinking high|xhigh`; model `reasoning=true`; output mode must show separate reasoning where available | No downgrade unless native probe fails; provider remains selectable |
| Droid | custom model `provider=anthropic`, root base, PM model | custom model `provider=openai`, `/v1` base, SH model; if runtime is chat-only use generic chat root | `--reasoning-effort high` plus `showThinkingInMainView`; accept only provider-supported output | Switch only SH to `generic-chat-completion-api` at root if OpenAI custom path is proven chat-only |
| omp | provider `api=anthropic-messages`, root base, PM model | provider `api=openai-responses`, `/v1` base, SH model | PM `thinking.mode=anthropic-*`; SH `thinking.mode=effort` with live effort map; no role assignment | `openai-completions` only after native OMP decoder failure |
| Cline | Native Anthropic provider candidate; exact PM model/base URL | OpenAI-compatible chat candidate; exact SH model/root fallback | `--thinking` or provider-native normalized reasoning; record whether thinking is exposed | Chat-only fallback if Cline cannot persist native provider type or env-safe credential |
| GitHub Copilot CLI | `COPILOT_PROVIDER_TYPE=anthropic`, root base, `COPILOT_MODEL=pm/Claude-Fable` | `COPILOT_PROVIDER_TYPE=openai`, `/v1` base, `COPILOT_PROVIDER_WIRE_API=responses`, `COPILOT_MODEL=sh/gpt-5.6-sol` | `--effort high|xhigh` and `--enable-reasoning-summaries` where supported | One explicit launcher per dialect; no mixed-provider process or global env default |

The static checker in `evidence/route-contract-check.py` verifies the final namespace/dialect bindings. Runtime acceptance additionally requires the exact CLI sentinel, child exit code, thinking/reasoning evidence, and tool/function continuation where the product exposes tools.

### Captured native failure classes (isolated probes, 2026-08-30)

Each class is a proven, reproduced blocker on the native SH route with preserved evidence; the live disposition is the named fallback. Canonical evidence: `evidence/cli-disposition-matrix.md`.

| Class | CLI | Native SH route result | Live disposition |
|---|---|---|---|
| FBC-1 | omp | Responses route exceeded the bounded probe timeout with no usable output; no decoder error was observed | `openai-completions` provider at versionless chat route |
| FBC-2 | Kimi Code | strict Responses decoder rejects a `response.in_progress.response` heartbeat missing `sequence_number` | versionless chat fallback |
| FBC-3 | Grok | Responses serialization error `missing field sequence_number` in stream | `api_backend=chat_completions`, root base |
| FBC-4 | goose | strict Responses stream decode defect in CLI operating mode (streaming); non-stream probe passed | dedicated `engine=openai`, `/v1` base plus `base_path=chat/completions` |
| FBC-5 | Cline | native provider lockout: custom base URL rejected for the native provider and key validation rejects non-`sk-ant-*` keys | chat-fallback-only client: codex-compatible provider, custom base URL, versionless chat route |

Native routes that passed isolated probes and are eligible for live apply as native: prime-agent, pi, kilo, opencode, droid, copilot-cli, codex (SH `wire_api="responses"`), claude-code (PM only), kimi-code (PM), goose (PM), grok (PM), omp (PM), kilo/opencode (both), and all PM rows of the FBC CLIs.
## Configuration patterns

Candidate files under `evidence/candidate-templates/` are **overlay/profile inputs**, not wholesale replacements for user configuration. The apply implementation SHALL merge only the named provider/model/profile entries into the live file, preserving all baseline providers, defaults, roles, fallback chains, permissions, and unrelated settings. Codex's `omniroute.config.toml` is a selectable profile; it SHALL be installed beside the existing `config.toml` without changing the latter's top-level model/provider. OMP's `models.yml` overlay SHALL not modify `config.yml` roles or retry chains. A missing field in an overlay means “inherit the frozen baseline,” never “delete the live field.”

### Anthropic Messages

Use the CLI's native Anthropic provider type, host-root base URL where the client appends `/v1/messages`, exact model `pm/Claude-Fable`, and the CLI's own thinking control. Do not use the `sh/Claude-Fable` model with an OpenAI provider.

### OpenAI Responses

Use the CLI's native Responses provider type, base URL `http://localhost:20128/v1`, exact model `sh/gpt-5.6-sol`, and a supported reasoning effort (`high` or `xhigh`). Do not infer that a successful raw Responses request means a strict client decoder will accept every stream event.

### Versionless Chat fallback

Use only where the native path is rejected by the installed client. The effective request target must be `http://localhost:20128/chat/completions`, not the failing versioned path. The fallback registration must be explicitly named as chat-compatible and must not be used to claim native reasoning/message semantics.

### Credentials

Preferred references are:

- `OMNIROUTE_API_KEY` through each CLI's documented environment syntax;
- a Claude Code helper that sources the existing shell environment without printing it;
- Goose `api_key_env`;
- Cline's pre-existing literal credential field (`providers.openai-native.settings.apiKey`) is preserved byte-for-byte at mode 600; this change introduces no new literal credential in Cline (classification: `evidence/cline-credential-classification.md`);
- Kimi Code's existing mode-600 literal key only because its installed contract does not resolve ordinary shell variables for provider credentials.

No key values are retained in OpenSpec evidence, backups copied into Git, or review bundles.

## Apply and rollback

1. Freeze the live catalog and route evidence.
2. Capture a value-blind baseline manifest and mode-600 backup for every target file. The manifest SHALL include every candidate provider identity, default/role/fallback selector, file mode, existence flag, and hash.
3. Build each candidate in a disposable HOME/profile where the CLI supports it.
4. Parse candidate configuration using the CLI's native schema or parser.
5. Run a bounded explicit sentinel, then a thinking and tool probe where supported. Retained results SHALL contain only structured booleans, sizes, hashes, exit codes, and enumerated diagnostic classes; no free-form CLI output.
6. Replace only one file/provider surface at a time with an atomic rename and explicit file mode. Active files with literal credentials SHALL be mode 600. Env-reference-only catalog files may retain their existing mode; any `0644→0600` tightening SHALL be listed explicitly in the candidate manifest.
7. Re-run the explicit sentinel and a no-override default probe; record default identity separately and compare it with the exhaustive baseline manifest.
8. Restore that file immediately if parse, route, thinking, or tool gates fail.
9. Preserve all unrelated user configuration and archived OpenSpec history. Live apply SHALL NOT begin while the independent plan review has a FAIL, UNKNOWN, or NOT_REVIEWED approval-critical edge.

## Non-goals and unresolved decisions

- Defaults are not changed by this design.
- Whether Cline's and Copilot's user-facing default should become an OmniRoute route is deferred; the first implementation is explicit, opt-in route selection.
- The existing legacy Kimi file is not treated as the effective v0.39 configuration. Its retired `dlg/*` entries are recorded as inactive legacy state rather than silently rewritten.
