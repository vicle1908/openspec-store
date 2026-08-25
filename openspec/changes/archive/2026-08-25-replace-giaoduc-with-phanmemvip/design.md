# Design: Replace giaoduc with phanmemvip (Codex Responses API)

## Context

See proposal.md — Why. The giaoduc provider is retired; phanmemvip
(`https://api.phanmemvip.shop/v1`, Codex Responses API, key
`HERMES_CUSTOM_PHANMEMVIP_API_KEY`) is the replacement. phanmemvip is already
declared in Hermes config v39 and its key is already exported by the shared
`~/.zshenv` credential loader (`~/.config/agent-llm/load-hermes-custom-credentials.zsh`,
allowlist `^HERMES_CUSTOM_[A-Z0-9_]+_API_KEY$`). Verified live before planning:
`POST /v1/responses` with `gpt-5.6-sol` returned "pong"; `/v1/models` lists
`codex`, `gpt-5.6`, `gpt-5.6-sol`, `o3`, `o4-mini`, `gpt-4o`, `gpt-5.4`, `gpt-5.5`.

Consumers and their Responses-API dialects:

| Consumer | Config | Responses dialect |
|---|---|---|
| Hermes | `~/.hermes/config.yaml` | `api_mode: codex_responses` (already set for cockpit; phanmemvip block exists) |
| OMP | `~/.omp/agent/models.yml` | `api: openai-responses` |
| pi | `~/.pi/agent/models.json` | `"api": "openai-responses"` |
| prime-agent | `~/.prime/agent/models.json` | `"api": "openai-responses"` |
| grok | `~/.grok/config.toml` | `api_backend = "responses"` |
| goose | `~/.config/goose/custom_providers/` | `engine: openai` (Responses-capable) |

## Goals / Non-Goals

Goals:
- Full provider swap: phanmemvip added and giaoduc removed everywhere it is
  routed, in one coordinated change.
- Every migrated selector proven by a live smoke test before the giaoduc key
  is removed from `~/.hermes/.env`.

Non-goals (design-level):
- No new credential plumbing: the key already exists and is exported; this
  change only re-points consumers at it.
- No Claude Code phanmemvip launcher (deferred; shopapikey/Claude-Fable stays
  the Anthropic-side route).
- No changes to the claude-code-provider-adapter repo.

## Decisions

### D1: phanmemvip wire transport is Codex Responses everywhere

Every consumer that supported giaoduc over Anthropic Messages will carry
phanmemvip over its native Responses dialect (table above). Rationale: the
user directed "use codex response api for phanmemvip", and the endpoint was
verified to serve `/v1/responses` natively. Alternative considered: routing
phanmemvip through the existing claude-code-provider-adapter — rejected
because the adapter is cockpit-specific (hardcoded upstream key env) and only
Claude Code needs Anthropic-side translation, which shopapikey already covers.

### D2: Model is `gpt-5.6-sol` at 1M context

`gpt-5.6-sol` is the model Hermes v39 already routes for phanmemvip (fallback
#2, MoA references), so the swap keeps a single canonical model across all
consumers. Alternative: `codex` or `gpt-5.6` — rejected to avoid introducing a
second canonical model in the same change.

### D3: MoA effort mapping is 1:1

`giaoduc:Advance@high` → `phanmemvip:gpt-5.6-sol@high` in every reference
slot; deep aggregator `@max` → `@max`; default-2 aggregator `@xhigh` →
`@xhigh`. No temperature, token-limit, fanout, or policy tuning changes.
Rationale: user decision; isolates the provider variable from the tuning
variable.

### D4: goose uses `HERMES_CUSTOM_PHANMEMVIP_API_KEY` directly

goose's existing custom providers name `CUSTOM_*_API_KEY` env vars, but no
such variables are exported anywhere on this machine (goose currently relies
on keyring-stored keys). The shared loader already exports
`HERMES_CUSTOM_PHANMEMVIP_API_KEY` in every login shell, so the new
`custom_phanmemvip.json` references it directly — one credential source, no
new loader surface. Alternative: adding a `CUSTOM_PHANMEMVIP_API_KEY` alias —
rejected as redundant indirection.

### D5: Removal order is last, gated on smoke tests

The giaoduc key stays in `~/.hermes/.env` until every consumer is migrated
AND every phanmemvip selector has passed its CLI smoke test. Removing the key
first would fail-closed any missed reference. Timestamped backups precede every
live file mutation (pattern carried over from the superseded
`omp-model-role-fallback-tuning` change).

### D6: Supersede `omp-model-role-fallback-tuning`

That active change's premise (restore `task: giaoduc/Advance:xhigh`, treat the
giaoduc 401 as a credential bug) is invalidated by the retirement decision.
Its planning artifacts are abandoned; its isolated-profile smoke-test gate,
atomic-rename rollout, and md5-baseline rollback patterns are folded into this
change's tasks. The abandoned change is archived as superseded without apply.

## Risks / Trade-offs

- [A consumer still references giaoduc after key removal] → grep-audit every
  config surface for `giaoduc`/`Advance` before the key-removal step; the key
  removal is the final task and is gated on the audit returning zero hits
  outside backups.
- [Responses-API dialect mismatch per CLI (e.g., grok `responses` backend
  quirks)] → per-CLI live smoke test is the acceptance gate for each surface;
  a failing surface is rolled back from its backup and reported, not forced.
- [OMP role regression while config.yml is mid-edit] → OMP files are replaced
  via atomic rename from validated temp files, sequentially, with coordinated
  rollback (inherited requirement).
- [Hermes MoA presets reference a provider whose Responses mode differs from
  Anthropic] → Hermes already declares phanmemvip with `discover_models: true`;
  MoA validation plus a fresh `moa:default` smoke turn confirm aggregation.
- [tdt-core registry change breaks agent-core resolution] → registry edit is
  additive for phanmemvip and only removes the giaoduc entry after the
  agent-core/tdt runtime configs are confirmed giaoduc-free; run tdt-core
  tests (`uv run pytest`) as the gate.

## Migration Plan

1. Preflight: confirm `HERMES_CUSTOM_PHANMEMVIP_API_KEY` resolves; re-verify
   `/v1/responses` pong; snapshot all target files (timestamped backups).
2. Migrate consumers in dependency order: Hermes (provider block + MoA) →
   tdt-core registry → OMP → pi → prime-agent → grok → goose → zshrc/Claude
   (giaoduc removal only).
3. Per-surface smoke test immediately after each migration; rollback from
   backup on failure.
4. Final audit: `grep -r giaoduc` across all config surfaces (excluding
   backups) must return zero; then remove the key from `~/.hermes/.env`.
5. Rollback strategy: every mutated file has a timestamped backup; restore
   commands recorded in tasks.md; the giaoduc key removal is reversible by
   re-adding the entry from the backup copy.

## Open Questions

None blocking. (goose `engine: openai` Responses behavior is confirmed by the
smoke-test gate; if goose 1.45 requires a distinct engine string for
`/v1/responses`, the task captures the adjustment without changing the spec.)
