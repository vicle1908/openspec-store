# Design: Migrate missed CLI surfaces to phanmemvip

## Context

See proposal.md — Why. Verified facts: phanmemvip's OpenAI side serves
`Claude-Fable` via chat-completions (pong verified); opencode 1.18.23's
ProviderConfig schema supports a per-provider `api` string field; droid has no
global default model field (per-session selection; mission models are built-in
`claude-opus-5`); cline stores provider state in
`~/.cline/data/settings/providers.json` and is re-configured via `cline auth`.

## Decisions

- **D1**: opencode phanmemvip uses `api: "responses"` (the OpenAI Responses
  dialect per the user's Responses-only directive for phanmemvip). Verified by
  `opencode run -m phanmemvip/gpt-5.6-sol` smoke. Alternative:
  `@ai-sdk/openai-compatible` npm with chat-completions — rejected because the
  user directed Responses for phanmemvip.
- **D2**: droid keeps an `anthropic`-type `Claude-Fable` entry (droid's
  anthropic provider type targets the Messages endpoint — the correct
  transport for Claude models) and gains a separate `openai`-type
  `gpt-5.6-sol` entry for the Responses surface. The Responses-only rule
  governs the phanmemvip provider, not shopapikey's Claude models.
- **D3**: cline is re-registered via `cline auth` (the CLI's own mechanism,
  matching the `~/.zshrc` launcher pattern) rather than hand-editing
  providers.json; the stale giaoduc entry is removed from providers.json.
- **D4**: goose/pi/omp/prime-agent need no changes (re-audit: zero residue);
  the new capability codifies their expected state so future drift is
  detectable.

## Risks / Trade-offs

- [opencode rejects `api: "responses"`] → smoke test is the gate; fallback is
  `@ai-sdk/openai-compatible` npm + chat-completions (recorded, re-proposed).
- [droid custom-model schema mismatch] → mirror the existing entry shape
  exactly; smoke via `droid exec`.
- [cline auth writes unexpected state] → verify providers.json after
  re-registration; backup exists.

## Migration Plan

1. Timestamped backups of the three target files.
2. opencode migration → smoke. 3. droid migration → smoke. 4. cline
   re-registration → verify. 5. Re-audit goose/pi/omp/prime-agent. 6. Final
   giaoduc/fable-5 audit across all seven CLIs. 7. Archive + store commit.
