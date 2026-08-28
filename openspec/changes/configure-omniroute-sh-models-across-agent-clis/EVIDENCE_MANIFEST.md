# Evidence Manifest: configure-omniroute-sh-models-across-agent-clis

All evidence is value-blind: no credential values, hashes only where noted.
Captured 2026-08-28 (local time +07:00).

## 1. Live registry baseline

- `GET http://127.0.0.1:20129/v1/models` (Bearer `OMNIROUTE_API_KEY`): 966 models.
- Target models present with metadata:
  - `sh/gpt-5.6-sol` — context 1,050,000; vision; tool_calling; reasoning; effort tiers none/low/medium/high/xhigh.
  - `sh/Claude-Fable` — context 200,000; vision; tool_calling; reasoning.
- `dlg/*` inference routes: **0 live** (retired namespace confirmed absent).

## 2. Mutations applied (one file per CLI, official mechanisms)

| CLI | File | Change | Backup (mode 600, sha256[:12]) |
|---|---|---|---|
| pi | `~/.pi/agent/models.json` | Added `sh/gpt-5.6-sol` (ctx 1050000) + `sh/Claude-Fable` (ctx 200000) to existing `omniroute` provider (`apiKey: ${OMNIROUTE_API_KEY}`, `api: openai-responses`) | `pi-models.json` `452d45cdde0b` |
| goose | `~/.config/goose/custom_providers/custom_omniroute.json` | Added both models; fixed `api_key_env` `CUSTOM_OMNIROUTE_API_KEY` (unset in all shell/env files) → `OMNIROUTE_API_KEY`; drained 4 retired `dlg/*` entries | `goose-custom_omniroute.json` `65b300e67594` |
| goose | `~/.config/goose/config.yaml` | Backed up only; not mutated | `goose-config.yaml` `e5e6192cacdf` |
| kimi | `~/.kimi-code/config.toml` | Added aliases `or-gpt-5-6-sol` → `sh/gpt-5.6-sol`, `or-claude-fable` → `sh/Claude-Fable`; switched `omniroute` provider `type` `openai_responses` → `openai` | `kimi-config.toml` `eab9b54d7256` |

Backup directory: `~/.config/agent-llm/backups/20260828T134722-omniroute-sh-models/` (dir 700, files 600).

## 3. Sentinel results (prompt: "reply only: pong")

| CLI | Selector | Result |
|---|---|---|
| omp | `omniroute/sh/gpt-5.6-sol` | PASS — `pong`, exit 0, attribution `omniroute/sh/gpt-5.6-sol` |
| omp | `omniroute/sh/Claude-Fable` | PASS — `pong`, exit 0, attribution `omniroute/sh/Claude-Fable` |
| pi | `omniroute/sh/gpt-5.6-sol` | PASS — `pong` |
| pi | `omniroute/sh/Claude-Fable` | PASS — `pong` |
| kimi | `--model or-gpt-5-6-sol` | PASS — `pong` |
| kimi | `--model or-claude-fable` | PASS — `pong` |
| goose | `--provider custom_omniroute --model sh/gpt-5.6-sol` | BLOCKED — see §5 |

omp was already registered with both models before this change (14-model omniroute catalog); verified, not mutated. `~/.omp/agent/config.yml` untouched (no `omniroute` in `modelRoles` or fallback chains — invariant preserved).

## 4. Preservation checks

- All pre-existing providers remain in every mutated file (JSON/TOML re-parse clean after each edit).
- No default model changed: kimi `default_model = "pm-sol"` unchanged; goose `config.yaml` untouched; omp `default: phanmemvip/gpt-5.6-sol:xhigh` unchanged.
- opencode, droid, cline, prime-agent, grok: inspected, **not mutated** (outside approved set; prime-agent owned by `add-omniroute-prime-agent-provider`).

## 5. Known blocker: OmniRoute SSE heartbeat defect (server-side)

- Symptom: during slow first-token phases (>~13s), OmniRoute emits `data: {"type":"response.in_progress"}` — missing the required `response` object and `sequence_number` fields.
- Reproduced with per-event timestamps: bare event at t≈13.3s and every 15s thereafter; upstream (`api.phanmemvip.shop`) emits no such event.
- Source: `node_modules/@omniroute/open-sse/utils/sseHeartbeat.ts` (`OPENAI_RESPONSES_IN_PROGRESS` shape). The 15s default is build-inlined into the Next.js bundle; `SSE_HEARTBEAT_INTERVAL_MS=0` in the container env has **no effect** (attempted and reverted).
- Impact: goose's strict Rust Responses decoder rejects the event (`missing field sequence_number`). kimi's `openai_responses` dialect hit the same decode error; resolved by switching kimi to the `openai` chat-completions dialect (streaming chat path is clean).
- Not caused by this change: affects all slow models, pre-existing registrations included.
- Follow-up: upstream OmniRoute issue (malformed heartbeat frame); no local workaround available for Responses-dialect strict decoders.

## 6. Security notes

- `OMNIROUTE_API_KEY` value was inadvertently printed into an agent transcript during verification (shell-expansion bug). Per `standardize-zshenv-shared-secrets` R7 policy, treat as exposed; provider-side rotation remains a user action.
- kimi `config.toml` retains a literal OmniRoute key (mode 600) — no documented env indirection exists for kimi provider `api_key`; documented as the sole exception in the delta spec.
- No literal credentials appear in this change package.
