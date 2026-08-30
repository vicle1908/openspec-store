# Design: add-claude-code-omniroute-pm-launcher

## Context

- OmniRoute (docker, 127.0.0.1:20129) is the workspace AI gateway. It
  serves Claude-Fable-compatible `/v1/chat/completions` and — relevant here — a
  native Claude-Fable `/v1/messages` endpoint with model IDs namespaced by
  channel (`pm/...` = phanmemvip upstream).
- Claude Code (2.1.251) speaks the Messages protocol and can be pointed
  anywhere via `ANTHROPIC_BASE_URL`.

## Verified protocol behavior (2026-08-29, live)

| Item | Result |
|---|---|
| `POST /v1/messages?beta=true` full CC payload (thinking, output_config, tools, context_management, system, metadata) | 200, native `message` JSON, ~0.9 s |
| `POST /v1/messages/count_tokens` | 200 `{"input_tokens":N,"source":"local"}` |
| Claude Code `--settings` profile with model `pm/Claude-Fable[1m]` | PONG, exit 0 |
| `[1m]` suffix on wire model | stripped before send (capture-server proof: model sent = `pm/Claude-Fable`) |
| Auth on `/v1/messages` | loopback keyless (`REQUIRE_API_KEY=false`); `/v1/models` still 401s without key |
| `pm/*` models | `pm/Claude-Fable`, `pm/Claude-Fable`, `pm/Claude-Sonnet`, `pm/default` |

## Decisions

1. **Profile, not wrapper script.** The three-provider pattern routes via
   `claude --settings <profile>`; a separate zsh wrapper would fork the
   mechanism. The `omniroute()` zsh launcher mirrors `shopapikey()` /
   `cockpit()` exactly.
2. **Self-mapping `modelOverrides`.** Claude Code prints a cosmetic
   `[claude-code:unrecognized_model]` diagnostic for gateway aliases; the
   docs' remedy is an entry mapping the ID to itself. It does not block
   requests (verified: exit 0, correct response).
3. **`apiKeyHelper` even though keyless.** The profile-resolution spec
   requires the helper field and forbids persisted tokens. OmniRoute's
   loopback may be re-keyed later; with the helper, no config change is
   needed — the shared-tier `OMNIROUTE_API_KEY` flows automatically.
4. **`127.0.0.1` not `localhost`.** Avoids IPv6 `::1` resolution surprises
   in Node clients; matches the OmniRoute port-binding hardening pattern.
5. **1M context.** `pm/Claude-Fable[1m]` selected as default to match the
   shopapikey launcher's Fable 1M + xhigh stance. Provider-side 1M capacity
   is NOT yet proven separately (routing spec acceptance gate wording);
   selector acceptance only proves routing.

## Risks / notes

- OmniRoute `pm/...` latency varied 0.9–58 s across probes (upstream
  variance). Direct phanmemvip `/v1/messages` is comparably slow (~63 s
  round trip for a tiny prompt). `API_TIMEOUT_MS=600000` covers this.
- If OmniRoute is down, the launcher fails fast at connection time.


## Verification evidence (2026-08-29)

- 3.1/3.2 helper single-line output: env-first PASS; `env -i` fallback PASS
- 3.3 profile: no secrets in env block, mode 600 PASS
- 3.4 `omniroute -p` live: PONG, exit 0 (through OmniRoute pm channel)
- 3.5 guard with helper renamed: `Error: missing omniroute credential helper`, no launch PASS
- 3.6 `claude_reset -p` live: env cleared, global-settings resolution, PONG
- 4.2 `openspec validate add-claude-code-omniroute-pm-launcher --strict`: valid
