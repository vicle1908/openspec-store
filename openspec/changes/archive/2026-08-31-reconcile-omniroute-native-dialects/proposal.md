# Proposal: Reconcile OmniRoute Native Dialects Across Installed Agent CLIs

## Why

The current user-level CLI configurations do not consistently bind OmniRoute model namespaces to the protocols they actually serve. Several clients still expose `sh/Claude-Fable` through an OpenAI/Responses or Chat configuration even though the intended Claude route is the dedicated `pm/Claude-Fable` namespace served through Anthropic Messages. The requested GPT route is the dedicated `sh/gpt-5.6-sol` namespace served through OpenAI Responses.

The archived changes `2026-08-28-configure-omniroute-sh-models-across-agent-clis`, `2026-08-29-add-omniroute-prime-agent-provider`, `2026-08-29-stabilize-goose-sol-and-harden-agent-cli-config-permissions`, and `2026-08-29-correct-grok-cli-provider-routing` remain historical records. This follow-up does not edit them; it reconciles their stale or client-specific routing assumptions against the current live `pm/*` and `sh/*` registry.

## What Changes

This is a config-only reconciliation change. It registers the exact live OmniRoute
namespaces on every installed agent CLI through each client's native protocol surface:

- `pm/Claude-Fable` through Claude-Fable Messages (`POST /v1/messages`)
- `sh/Cpt-5.6-sol` (exact ID per proposal) through Claude-Fable Responses (`POST /v1/responses`)
- versionless Chat Completions only as evidence-gated fallbacks (FBC classes 1-5)

Applied surfaces (11 overlay targets): Codex selectable profile, Claude-Fable, Claude-Fable,
Kilo, OpenCode, Pi, Prime Agent, Droid, omp, goose, cline. Claude Code is owned by the
archived `add-claude-code-omniroute-pm-launcher` change. No defaults changed; per-file
backups and rollback; full evidence under `evidence/`.

## Scope

This change SHALL:

- inventory every installed coding-agent CLI and deduplicate aliases, wrappers, and product names;
- use the exact live model IDs `pm/Claude-Fable` and `sh/gpt-5.6-sol`;
- configure `pm/Claude-Fable` through an Anthropic Messages surface wherever the CLI supports that native protocol;
- configure `sh/gpt-5.6-sol` through an OpenAI Responses surface wherever the CLI supports that native protocol;
- use the empirically proven versionless `/chat/completions` route only for a CLI whose native decoder or provider surface cannot consume the required native dialect;
- configure thinking/reasoning only through each CLI's documented controls and the live capability metadata;
- keep `OMNIROUTE_API_KEY` external through the CLI's supported environment or helper mechanism, with the documented Kimi Code exception retained only if its installed contract cannot resolve a shell environment reference;
- preserve existing providers and normal defaults unless a separate per-CLI default change is explicitly approved;
- back up and atomically replace each changed user configuration, with per-file rollback and real sentinel evidence;
- leave unsupported, unconfigured, vendor-auth-only, and separately owned surfaces unchanged and documented.

This change SHALL NOT:

- edit archived OpenSpec changes or canonical specifications directly;
- modify OmniRoute source, Docker images, database, connection registry, or provider credentials;
- patch any vendor CLI binary or framework source;
- use `[1m]` as an OmniRoute catalog model ID; the live catalog exposes `pm/Claude-Fable` without that suffix;
- silently route `sh/Claude-Fable` through the Responses provider as a substitute for `pm/Claude-Fable`;
- silently change a CLI's default model/provider;
- rotate, print, compare, or overwrite secret values.

## Corrected routing contract

| Namespace/model | Native protocol | Canonical OmniRoute request path | Thinking contract |
|---|---|---|---|
| `pm/Claude-Fable` | Anthropic Messages | `POST http://localhost:20128/v1/messages`; Anthropic base URL is the host root `http://localhost:20128` | Anthropic thinking enabled through the CLI's native thinking/effort control; model advertises reasoning |
| `sh/gpt-5.6-sol` | OpenAI Responses | `POST http://localhost:20128/v1/responses` | Responses reasoning effort; live tiers are `none`, `low`, `medium`, `high`, `xhigh` |
| either model, exception only | OpenAI Chat Completions | versionless `POST http://localhost:20128/chat/completions` | Preserve the CLI's documented reasoning field; do not claim native Messages/Responses semantics |

The versioned `POST /v1/chat/completions` route is not an acceptable fallback for `sh/gpt-5.6-sol` in the current deployment because it returned HTTP 502 during live validation. The versionless route returned HTTP 200 for both requested models.

## Live validation already completed

A fresh live catalog returned 975 models, including:

- `pm/Claude-Fable` — context 200,000; vision, tool calling, and reasoning;
- `sh/gpt-5.6-sol` — context 1,050,000; output limit 128,000; vision, tool calling, reasoning, and effort tiers `none/low/medium/high/xhigh`.

Raw protocol probes passed for both desired native routes:

- `pm/Claude-Fable` Messages non-stream and stream; thinking content; tool-call plus tool-result continuation;
- `sh/gpt-5.6-sol` Responses non-stream and stream; separated reasoning/message output; usage; function-call plus function-output continuation.

Known gateway/client compatibility findings remain explicit: Responses streams can omit `response.created.response.model` and can emit a malformed slow-phase `response.in_progress` heartbeat; strict decoders such as the installed Goose path require the versionless Chat Completions exception. The current `/v1/chat/completions` failure for `sh/gpt-5.6-sol` is why the fallback path must be selected empirically rather than by assuming the usual `/v1` suffix.

## Default policy

The initial apply is registration and route correction only. Existing defaults remain unchanged. A provider/model can be the correct configured route without becoming the CLI's default. Any default switch will be a separately named, explicitly approved task.

## Impact

The owned mutation surface is user-level configuration under `/Users/androidteam` plus this OpenSpec change directory. Candidate files include the native configuration files for Claude Code, Codex, Grok, goose, Kimi Code, Kilo, OpenCode, Pi, Prime Agent, Droid, omp, Cline, and the GitHub Copilot BYOK launcher/environment surface. Cursor Agent, Auggie, Qoder, Antigravity, and other vendor-auth-only or unconfigured products remain unchanged unless their installed version exposes a documented custom endpoint mechanism during the inventory gate.
