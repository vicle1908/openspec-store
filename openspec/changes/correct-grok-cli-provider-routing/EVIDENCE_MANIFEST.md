# Evidence Manifest: correct-grok-cli-provider-routing

Date: 2026-08-29 · Grok CLI 1.0.5 (5115b46bc909) stable · Store: openspec-store

All evidence below is sanitized: statuses, exit codes, model IDs, durations, and outcomes only. No credential values, authorization headers, request bodies, or raw responses are retained.

## 1. Backup and baseline

- Backup: `~/.grok/config.toml.bak-correct-grok-cli-provider-routing.20260829T083434`
  - mode 600, sha256 `d60fdaf97e7117ad0be9bcb84a608fe642a9a9f72a0401447b54b56e0de9397c`
  - restore check: `cmp` byte-identical → PASS
  - kept in the `~/.grok` backup lineage, outside the git-tracked store, because the config embeds a pre-existing MCP server token (see §5 note)
- Baseline (final config, OmniRoute at 20128):
  - `grok models` lists 8 models: 7 custom + `grok-4.6` (xAI-native); default `cockpit-sol`
  - Providers: shopapikey (api.phanmemvip.shop/v1, chat_completions, env HERMES_CUSTOM_SHOPAPIKEY_API_KEY) · phanmemvip (api.phanmemvip.shop/v1, chat_completions, env HERMES_CUSTOM_PHANMEMVIP_API_KEY) · cockpit (localhost:51006/v1, chat_completions, env HERMES_CUSTOM_COCKPIT_API_KEY) · omniroute (localhost:20128/v1, chat_completions, env OMNIROUTE_API_KEY)
  - Defaults: default=cockpit-sol, web_search=grok-4.6, session_summary=cockpit-sol, fork_secondary_model=cockpit-sol

## 2. Configuration contract validation

Task 2.1 — programmatic assertions over `~/.grok/config.toml`: **18/18 PASS**
(all four providers api_backend=chat_completions; omniroute base_url=<http://localhost:20128/v1> with env_key=OMNIROUTE_API_KEY; default/web_search/session_summary/fork_secondary unchanged; exactly 7 custom model entries; no legacy giaoduc provider; per-model context windows 1050000/200000; no literal api_key in provider blocks)

## 3. Credential scan

Task 2.2 — provider credential value scan (values withheld; presence checks only):

- All six provider credential values (HERMES_CUSTOM_SHOPAPIKEY/PHANMEMVIP/COCKPIT/ANTIGRAVITY/LOCALHOST_51006_API_KEY, OMNIROUTE_API_KEY): **ABSENT** from `~/.grok/config.toml` and from every artifact in this change directory
- Pattern scan of change directory (pmv_/agt_/mcpr_/sk-/xai- value prefixes): **no hits**

**Pre-existing observation (out of change scope):** `~/.grok/config.toml` embeds a literal MCP server token (`MCPR_TOKEN` for the mcp-router server) in `[mcp_servers.mcp-router.env]`. It predates this change, is not a provider credential, and is unchanged by this change. Flagged for a separate hardening change (indirect it through env like provider keys); reason the config backup is stored outside the git-tracked store.

## 4. Live catalog check

Task 2.3 — fresh `GET http://localhost:20128/v1/models` (Bearer via environment):

- `sh/Claude-Fable`: context_length=1050000 → matches registered `context_window` PASS
- `sh/Claude-Fable`: context_length=200000 → matches registered `context_window` PASS

## 5. Sentinel verification matrix (one turn per model)

Task 3.1 — prompt "Reply with exactly: OK", spaced to respect the observed gateway rate limit:

| Model | Exit | Duration | Exact match | Status |
| --- | --- | --- | --- | --- |
| shopapikey-claude-fable | 0 | 13s | yes | PASS |
| phanmemvip-sol | 0 | 12s | yes | PASS |
| cockpit-sol | 0 | 13s | yes | PASS |
| cockpit-luna | 0 | 13s | yes | PASS |
| cockpit-terra | 0 | 11s | yes | PASS |
| omniroute-sol | 0 | 15s | yes | PASS |
| omniroute-claude-fable | 0 | 13s | yes | PASS |

7/7 PASS. No serialization, authentication, or reconnect errors. `omniroute-claude-fable` verified under the final 20128 port.

## 6. Tool-call verification matrix (one probe per provider)

Task 3.2 — disposable `echo TOOLCALL_OK` bash probe in /tmp work dir; no outside-root mutation:

| Provider | Model probed | Exit | Duration | Exact marker | Status |
| --- | --- | --- | --- | --- | --- |
| cockpit | cockpit-sol | 0 | (session) | yes | PASS |
| omniroute | omniroute-sol | 0 | (session, 20128) | yes | PASS |
| shopapikey | shopapikey-claude-fable | 0 | (session) | yes | PASS |
| phanmemvip | phanmemvip-sol | 0 | 13s | yes | PASS |

4/4 PASS. Each provider completed a real tool call end-to-end through the chat_completions streaming path.

## 7. Failure classification

Task 3.3 — zero failures across both matrices; nothing to classify. The only failure mode observed during the 2026-08-29 diagnosis was `429 rate_limit_error` from api.phanmemvip.shop under rapid sequential calls — classified as an environment gate, mitigated by call spacing; not a routing failure.

## 8. Known-broken protocol combinations (routing constraints)

Task 4.2 — combinations that must not be re-enabled for these gateways; these are response-shape incompatibilities, NOT authentication failures:

| Backend | Gateway | Observed failure |
| --- | --- | --- |
| messages | api.phanmemvip.shop (both keys) | `serialization error: missing field signature` — /v1/messages returns Chat Completions objects; thinking blocks carry no signature |
| responses | api.phanmemvip.shop | `serialization error: missing field model` — streaming `response.created` omits `model`; non-streaming /v1/responses returned 502/timeout |
| responses | OmniRoute | streaming `response.created` omits `model` + malformed SSE heartbeat frame (same two-part defect documented for goose in `omniroute-agent-cli-routing`) |
| messages | OmniRoute `sh/*` | empty response (`upstream_empty_response`) |
| chat_completions (non-streaming) | OmniRoute `sh/*` | `upstream_empty_response` — `sh/*` is streaming-only (grok CLI always streams, so out of request path) |
| messages | cockpit (Claude-Fable model) | 404 `model_not_available` — model not in key scope; cockpit works via chat_completions |

Identical failures on grok 1.0.3 and 1.0.5 → gateway response-shape mismatch, not a CLI regression.
