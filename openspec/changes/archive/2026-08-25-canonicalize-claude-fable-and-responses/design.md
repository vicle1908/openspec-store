# Design: Canonicalize Claude-Fable and phanmemvip Responses transport

## Context

See proposal.md — Why. Verified facts: the shopapikey endpoint's model list is
`Claude-Opus, Claude-Sonnet, Claude-Fable, default`; `fable-5` still resolves
(server-side alias returning `"model":"Claude-Fable"`), so the rename is
non-breaking canonicalization. goose 1.45 engines are `openai|anthropic|ollama`
(goose-docs `ProviderEngine` enum); its OpenAI engine auto-routes `gpt-5*`
models to the Responses format via `is_openai_responses_model()`. The Claude
cockpit adapter is docker-mapped `127.0.0.1:8788:8787`.

## Decisions

- **D1**: Rename `fable-5` → `Claude-Fable` everywhere, preserving the `[1m]`
  suffix in Claude Code selectors (`Claude-Fable[1m]`). The OMP illustrative
  alias `shopapikey-fable-5` becomes `shopapikey-claude-fable` in spec
  examples only (live OMP uses `provider/model` selectors, not aliases).
- **D2**: phanmemvip transport rule is codified in `omp-provider-routing` as
  the owner of cross-consumer provider transport facts (it already carries the
  wire-protocol requirement pattern).
- **D3**: goose `engine: "openai"` — the only engine that reaches the
  Responses format for `gpt-5.6-sol`; `engine: "anthropic"` would use the
  Messages protocol, violating the user's Responses-only directive.
- **D4**: cockpit profile scenario aligns to live port 8788 (docker-mapped);
  the host-native 8787 instance remains valid for `~/.zshrc`'s direct export
  but the profile file uses 8788.

## Risks / Trade-offs

- [A consumer hardcodes `fable-5` in a place the rename misses] → final
  `grep -r fable-5` audit across all config surfaces before archive.
- [goose engine switch changes behavior] → goose smoke test with
  `custom_phanmemvip` after the engine change is the gate.
- [Claude Code rejects `Claude-Fable[1m]` selector] → shopapikey launcher
  smoke after the profile/settings rename; rollback from backups on failure.

## Migration Plan

1. Timestamped backups of all target files.
2. Rename in consumer configs (Claude settings/profile → OMP → pi →
   prime-agent → grok → goose shopapikey → zshrc cline → ~/.tdt → Hermes
   shopapikey block).
3. goose engine fix + smoke.
4. Per-surface smoke with `Claude-Fable`.
5. Final `fable-5` audit → archive → store commit.
