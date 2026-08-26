# Design: Migrate kimi and grok to phanmemvip

## Context

See proposal.md — Why. Verified live facts:
- phanmemvip `/v1/responses` serves both `gpt-5.6-sol` and `Claude-Fable`
  (status: completed, pong).
- grok's responses backend works (cockpit-sol → pong; phanmemvip-sol → pong);
  its messages backend fails on phanmemvip (`missing field signature`).
- OmniRoute is healthy again (200 on 20128/20129) but the `dlg/*` catalog IDs
  kimi references no longer exist; `aug/kimi-k2.6` fails (auggie CLI not
  installed); `github/kimi-k2.7-code` is in credential cooldown;
  `ollama-cloud/*` returns 401.
- kimi's moonshot-ai account: 429 suspended (insufficient balance).
- kimi custom providers use literal `api_key` (no env-var indirection in the
  binary for custom providers).

## Decisions

- **D1**: kimi default becomes `phanmemvip-sol` (gpt-5.6-sol via
  `openai_responses`), matching the user's Responses-only directive for
  phanmemvip. `Claude-Fable` is registered as a second kimi model for
  Claude-class work.
- **D2**: Dead OmniRoute `dlg/*` model entries are removed from kimi rather
  than remapped to `aug/*`/`github/*` equivalents — every tested OmniRoute
  upstream for those models is currently broken (auggie login missing,
  cooldown, 401), so remapping would trade one broken route for another.
  When OmniRoute upstreams are repaired, a follow-up change can re-add
  OmniRoute models.
- **D3**: grok's shopapikey provider switches to the responses backend.
  phanmemvip serves `Claude-Fable` over Responses (verified), eliminating the
  Messages `signature` deserialization failure. The Anthropic-only
  `extra_headers` block is removed with the backend switch.
- **D4**: kimi's moonshot-ai provider is preserved despite the suspended
  account — the config is valid and the fix is billing-side, not config-side.

## Risks / Trade-offs

- [kimi rejects the phanmemvip provider shape] → smoke test `kimi -p
  --model phanmemvip-sol` is the gate; rollback from backup on failure.
- [grok responses backend mishandles Claude-Fable] → smoke test
  `grok --model shopapikey-claude-fable -p` is the gate.
- [kimi loses all OmniRoute models] → accepted: they were already broken
  (dead catalog IDs); moonshot-ai remains for when billing is restored.

## Migration Plan

1. Timestamped backups of both config files.
2. kimi: add phanmemvip provider + 2 models, set default, remove dlg/*
   entries → smoke.
3. grok: shopapikey backend messages → responses, drop extra_headers → smoke.
4. Final giaoduc/Advance/fable-5/dlg audit for both files.
5. Archive + store commit.
