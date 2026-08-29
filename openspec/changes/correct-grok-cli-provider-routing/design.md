## Context

Grok CLI 1.0.5 (`~/.grok`) routes four custom providers: `shopapikey` and `phanmemvip` (both `https://api.phanmemvip.shop/v1`), `cockpit` (`http://localhost:51006/v1`), and `omniroute` (local OmniRoute deployment). Live wire-level diagnosis established:

- `api.phanmemvip.shop` serves Chat Completions schema on every path, including `/v1/messages`, which returns `{"object": "chat.completion"}` objects. The Messages backend fails with `missing field signature` (thinking blocks carry no `signature`); the Responses backend fails with `missing field model` (streaming `response.created` omits `model`).
- OmniRoute `sh/*` models work only through streaming `/v1/chat/completions`. Non-streaming chat completions returns `upstream_empty_response`; `/v1/messages` returns empty; `/v1/responses` streaming omits `model` in `response.created` and emits a malformed heartbeat frame — the same two-part defect documented for strict Responses decoders in `omniroute-agent-cli-routing`.
- Cockpit serves both `responses` and `chat_completions` correctly.
- Failures are identical on grok 1.0.3 and 1.0.5, so this is a gateway-shape mismatch, not a CLI regression or credential problem. `env_key` indirection resolves correctly (`HERMES_CUSTOM_*`, `OMNIROUTE_API_KEY`).
- OmniRoute's canonical documented API surface is `http://localhost:20128/v1`. The Docker deployment additionally publishes 20129 (API bridge) and 20132 (LiveWS); 20128 and 20129 serve identical `/v1` routes, and `omniroute-agent-cli-routing` plus the official README both name 20128 canonical.

The configuration corrections were applied during diagnosis: all four providers now declare `api_backend = "chat_completions"`, OmniRoute uses `http://localhost:20128/v1`, and `sh/*` models carry per-model `context_window` values. All seven registered models passed text and tool-call probes. This change formalizes that state with a verifiable contract, backup, and sanitized evidence rather than introducing new mutations.

## Goals / Non-Goals

**Goals:**

- Make the corrected routing state the documented, evidence-backed contract for Grok CLI custom providers.
- Capture a mode-600 backup and hash of the corrected configuration so rollback is defined.
- Produce sanitized verification evidence (statuses, model IDs, backends, outcomes) for every registered model.
- Document protocol combinations that are known-broken on these gateways so future failures are classified correctly.

**Non-Goals:**

- No modification of OmniRoute, cockpit, or provider servers, including vendor bundle hotfixes (prohibited by `omniroute-agent-cli-routing`).
- No default-model changes; `cockpit-sol` remains default, and xAI-native `grok-4.6` routing is untouched.
- No archived-change edits and no new literal credentials anywhere.

## Decisions

1. **Chat Completions backend for all four providers.** It is the only dialect every gateway serves correctly for this CLI. Alternatives rejected with evidence: `messages` on phanmemvip.shop (missing `signature`), `responses` on phanmemvip.shop and OmniRoute (missing `model` in streaming events; malformed heartbeat).
2. **OmniRoute base URL `http://localhost:20128/v1`.** Canonical per the official README, `omniroute-agent-cli-routing`, and the active Prime Agent change. Port 20129 works but is a Docker-deployment detail; 20128 is the documented single-port API surface.
3. **Environment indirection retained.** `env_key` references stay; no literal key values enter config, artifacts, or evidence.
4. **Per-model context windows from the live catalog.** `sh/Claude-Fable` at 1,050,000 and `sh/Claude-Fable` at 200,000 replace the blanket 1,000,000 provider default, taken from a fresh `GET /v1/models` at apply time.
5. **Streaming-only constraint on OmniRoute `sh/*` accepted and documented.** Grok CLI always streams, so the non-streaming `upstream_empty_response` failure is out of the CLI's request path; it is recorded as a constraint, not a blocker.
6. **Verification protocol: one sentinel text call plus one disposable tool-call probe per model, spaced to respect the observed phanmemvip.shop rate limit.** A provider counts as verified only when both succeed with exact expected output and no serialization, auth, or reconnect error.
7. **Backup semantics.** The corrected state receives a fresh mode-600 backup and recorded hash. The pre-diagnosis lineage exists only as `config.toml.bak-pre-*` files that predate the `env_key` migration and contain legacy literal keys — restorable only as a last resort and treated as sensitive material.

## Risks / Trade-offs

- [Stream-only reliance on OmniRoute `sh/*`] → any future non-streaming request path fails with `upstream_empty_response`. Mitigation: documented constraint; verification probes exercise streaming only.
- [Chat Completions loses Responses-native features] (reasoning summaries, response references) → grok renders `reasoning_content` deltas and tool calls were verified end-to-end. Accepted trade-off for universal compatibility.
- [Rate limiting on phanmemvip.shop (429 observed)] → verification calls are spaced and retried once; a persistent 429 is recorded as an environment gate, not a routing failure.
- [Local service dependency: `cockpit-c` process and OmniRoute container must be running] → a stopped service is a provider-specific failure; the CLI must not silently fall back to another provider (spec requirement).
- [Catalog drift on `sh/*` IDs and context windows] → apply-time verification re-fetches `/v1/models` and compares registered IDs against it.
- [Upstream `sh/*` quirk: injected system-prompt memory observed in reasoning output] → no routing impact; sentinel expectations match the final answer only, never reasoning content.
- [Credential exposure in evidence] → evidence records statuses, model IDs, timings, and exit codes only; no headers, bodies, or key material.

## Migration Plan

1. Capture corrected-state backup: copy `~/.grok/config.toml` to a mode-600 backup, record its sha256.
2. Confirm the configuration parses and `grok models` lists all seven custom models with the expected backends.
3. Re-run the verification matrix: sentinel text call and disposable tool-call probe for every registered model across the four providers, with rate-limit spacing.
4. Record the sanitized evidence manifest inside the change directory.
5. Run strict OpenSpec validation, then commit the store change.

**Rollback:** restore the corrected-state backup atomically (this is the known-good state). The legacy `.bak-pre-*` lineage predates `env_key` indirection and contains literal keys; it is a break-glass option only.

## Open Questions

None. Whether the default model should move off `cockpit-sol` was raised and explicitly deferred; it does not affect this change.
