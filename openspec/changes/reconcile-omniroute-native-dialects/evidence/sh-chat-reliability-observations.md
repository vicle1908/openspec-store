# sh/Claude-Fable chat-route reliability observations (2026-08-30, this session)

Value-blind probes from the reconcile-omniroute-native-dialects apply-gate work:

| # | Route | Payload | Result |
|---|---|---|---|
| 1 | `POST /v1/chat/completions` `sh/Claude-Fable` | minimal (messages+max_tokens) | HTTP 502 x5 (25s, 11s, 45s, 37s) |
| 2 | `POST /chat/completions` `sh/Claude-Fable` | minimal | HTTP 502 x2 |
| 3 | `POST /v1/chat/completions` `sh/Claude-Fable` | goose-shaped (tools + max_output_tokens + system) | HTTP 200 PONG (once), then HTTP 502 on retry |
| 4 | `POST /chat/completions` `sh/Claude-Fable` | goose-shaped | HTTP 502 |
| 5 | goose CLI live, existing `custom_omniroute_sh` (base_url `/v1`, engine Claude-Fable) | full agent payload | PONG (call log: POST /v1/chat/completions, 200, 82s, sourceFormat=Claude-Fable -> targetFormat=Claude-Fable-responses) |

Interpretation:
- The `sh/*` chat surface is intermittently 502 at the upstream/account level. Both versioned and
  versionless forms failed bare-payload probes this session, while a full goose payload succeeded once.
- OmniRoute call log confirms goose reaches `POST /v1/chat/completions` with `sh/Claude-Fable`
  and gets 200s when the upstream cooperates; the gateway translates Claude-Fable chat -> Claude-Fable-responses.
- The earlier same-day evidence (fallback-route-observations.md) recorded versionless 200s for both
  models; those results stand as captured, but the surface is NOT reliable today.
- Per `claude-code-provider-routing` spec: "A provider is rate limited/capacity error => acceptance gate
  remains pending; recorded as external blocker rather than pass."

Disposition for this change:
- goose SH chat fallback (FBC-4) config is structurally correct; the live acceptance sentinel for the
  legacy `sh/Claude-Fable` row (a preserved stale selector on the archived goose provider — NOT this
  change's requested SH model) is BLOCKED-UPSTREAM today, retry when the sh channel recovers.
- No config change can fix an upstream capacity error; do not re-apply or re-probe endlessly.
- The canonical GPT route remains `sh/gpt-5.6-sol` via Responses (/v1/responses), which is unaffected
  (design live-baseline: 200 stream + non-stream + function round-trip).

Scope note (corrected 2026-08-30): rows 1–5 probe the legacy `sh/Claude-Fable` chat rows carried by
the preserved goose providers. This change's requested SH model is `sh/gpt-5.6-sol`; its FBC-4
versionless-chat fallback evidence (`CANDIDATE_GOOSE_CHAT_OK`) is separately retained in the
disposition record and is not reclassified by these observations.
