# CLI Dialect Disposition Matrix — Canonical Evidence

Change: `reconcile-omniroute-native-dialects`
Generated: 2026-08-30 (Asia/Ho_Chi_Minh)
Method: disposable candidate configs (isolated HOME / daemon socket / CODEX_HOME /
FACTORY_HOME_OVERRIDE / provider config), real gateway credential in child env only,
bounded probes with exact sentinels. No live user config was modified.

Canonical model IDs (extracted from proposal.md programmatically):
- `pm/Claude-Fable` — Anthropic Messages native
- `sh/gpt-5.6-sol` — OpenAI Responses native

## Legend

- **Native** — CLI's documented native protocol surface for that dialect
- **Chat fallback** — versionless `POST http://localhost:20128/chat/completions`, exception per design principle 3
- **FBC** — fallback class (captured native failure that justifies the exception)

## Matrix

| CLI | PM route (pm/Claude-Fable) | SH route (sh/gpt-5.6-sol) | PM evidence | SH evidence |
|---|---|---|---|---|
| claude-code | Native Messages (profile helper) | n/a — PM client | PASS `CANDIDATE_CLAUDE_PM_OK` | n/a |
| codex | n/a — SH client | Native Responses (`wire_api="responses"`, selectable profile) | n/a | PASS `CANDIDATE_CODEX_PROFILE_OK` rc=0 via `--profile omniroute` |
| prime-agent | Native Messages (Anthropic provider) | Native Responses (responses provider) | PASS `CANDIDATE_PRIME_PM_OK` | PASS `CANDIDATE_PRIME_SH_OK` |
| pi | Native Messages (Anthropic provider) | Native Responses (responses provider) | PASS `CANDIDATE_PI_PM_OK` | PASS `CANDIDATE_PI_SH_OK` |
| omp | Native Messages (omniroute provider, Anthropic-messages dialect) | Chat fallback (FBC-1: Responses route exceeded the 240s bound with no usable output; no decoder error observed) | PASS | PASS via `CANDIDATE_OMP_SH_CHAT_OK` |
| kimi-code | Native Messages (Anthropic provider) | Chat fallback (FBC-2: Responses strict decode defect `response.in_progress.response` missing `sequence_number` → `provider.api_error` rc=1) | PASS `CANDIDATE_KIMI_PM_OK` | PASS via chat `CANDIDATE_KIMI_CHAT_OK` |
| grok | Native Messages (base /v1 required) | Chat fallback (FBC-3: Responses `serialization error: missing field sequence_number` rc=1) | PASS `CANDIDATE_GROK_PM_OK` | PASS via chat `CANDIDATE_GROK_CHAT_OK` |
| goose | Native Messages (Anthropic provider) | Chat fallback (FBC-4: Responses stream decode defect; native non-stream PASSED `CANDIDATE_GOOSE_SH_NOSTREAM_OK` but goose operates streaming by default) | PASS `CANDIDATE_GOOSE_PM_OK` | PASS via chat `CANDIDATE_GOOSE_CHAT_OK` |
| opencode | Native Messages (Vercel Anthropic adapter, baseURL /v1) | Native Responses (responses-capable adapter) | PASS `CANDIDATE_OPENCODE_PM_OK` | PASS `CANDIDATE_OPENCODE_SH_OK` |
| kilo | Native Messages (Anthropic provider) | Native Responses (responses provider) | PASS `CANDIDATE_KILO_PM_OK` | PASS `CANDIDATE_KILO_SH_OK` |
| droid | Native Messages (customModels Anthropic-messages) | Native Responses (customModels responses) | PASS `CANDIDATE_DROID_PM_OK` | PASS `CANDIDATE_DROID_SH_OK` |
| copilot-cli | Native Messages (BYOK Anthropic endpoint) | Native Responses (BYOK OpenAI Responses endpoint) | PASS `CANDIDATE_COPILOT_PM_OK` | PASS `CANDIDATE_COPILOT_SH_OK` |
| cline | Blocked/unverified (PM probe not executed; do not reuse SH evidence) | Native Responses control blocked (FBC-5); Chat fallback only | BLOCKED — no PM evidence | PASS via chat `CANDIDATE_CLINE_CHAT_OK` (SH only; fallback linked to blocked SH control) |

## Fallback justification classes (FBC)

1. **OMP Responses lifecycle timeout** — isolated probe exceeded the 240-second bound with zero usable output and no provider/decoder error; versionless chat route passed in the retained candidate probe.
2. **kimi-code Responses strict decode defect** — `response.in_progress.response` event
   missing `sequence_number` triggers decoder error `provider.api_error`; captured rc=1.
3. **grok Responses serialization defect** — `serialization error: missing field
   sequence_number`; captured rc=1 in disposable-root probe.
4. **goose Responses streaming defect** — stream decode failure; native non-stream
   probe passed (`CANDIDATE_GOOSE_SH_NOSTREAM_OK`), but goose operates streaming
   by default, so chat fallback applies for live use.
5. **cline Anthropic-surface lockout** — CLI's own auth command rejects custom
   base URLs for the Anthropic provider; runtime client-side key validation
   rejects non-`sk-ant-*` credentials (the OmniRoute gateway key format),
   blocking both native Anthropic paths. OpenAI-compatible custom base URL
   works and reaches the versionless chat route natively.

## Notes

- Codex earlier baseline (live config, `wire_api="responses"` claimed in
  `~/.codex`) timed out at 180s; the isolated canonical probe
  passes in ~60s. Disposition for codex live config apply: native Responses.
- Claude-code PM probe used profile-bound `apiKeyHelper` (helper script echoes
  the gateway credential), isolated `CLAUDE_CONFIG_DIR`.
- All probes: `--ephemeral`/`--no-session`-equivalent modes, read-only or no
  tool surfaces, exact-sentinel assertions, value-blind evidence capture.
