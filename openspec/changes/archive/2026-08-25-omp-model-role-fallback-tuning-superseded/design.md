# Design: omp-model-role-fallback-tuning

## Context

`/Users/androidteam/.omp/agent/config.yml` currently binds `smol`/`commit` to `shopapikey/fable-5:xhigh`, `task` to `giaoduc/Advance:xhigh`, leaves `tiny`/`vision` unset (falling through to the flagship `default`), and defines a single `retry.fallbackChains.default` ending in omniroute. Runtime evidence on 2026-08-25: `giaoduc/Advance` → `401 invalid_api_key`; cockpit luna serving live; shopapikey fable-5 succeeding same-day; antigravity catalog cached authoritative with `gemini-3.7-flash` (`text+image`, reasoning) — note there is no 3.7 lite variant; lite ids exist only at 2.5/3.1. This change is a delta against the existing `omp-provider-routing` capability, which already owns role allocation, isolated-profile validation, and the "no live mutation until isolated testing succeeds" gate.

Fallback semantics per OMP `docs/settings.md`: roles without a chain inherit `default`; keys containing `/` bind chains to a model across role reassignment; `provider/*` keys cover every model of a provider and `provider/*` entries swap provider keeping the id (missing ids skipped); selectors accept `:thinking` suffixes. Thinking budgets: `xhigh` = `max` = 32768 tokens.

## Goals / Non-Goals

**Goals:**
- High-frequency roles land on `google-antigravity/gemini-3.7-flash` at explicit `:high` effort per the user's high-effort direction.
- Every heavy role keeps a proven primary plus two-hop fallback covering both model-level and provider-level failure.
- Omniroute fully out of active routing without deleting its catalog definition.
- All nine final role selectors pass the isolated-profile smoke test before live mutation.

**Non-Goals:**
- Credential repair: if `giaoduc/Advance:xhigh` fails its acceptance test with `401 invalid_api_key`, the user must repair `HERMES_CUSTOM_GIAODUC_API_KEY` outside this change's scope. This change verifies and blocks; it does not modify credentials, provider definitions, or `models.yml` (including the known cosmetic `gpt-5.6-terra` name bug).
- No changes to `advisor.enabled`, `tier`, compaction, or tool settings.
- No re-enablement of omniroute routing; revisit when OmniRoute deployment/key state is resolved.

## Decisions

- **D1: flash-3.7 at `:high` for `smol`/`tiny`/`vision`.** User-directed family and effort level ("use high effort"); only fast catalog entry with confirmed image input for `vision`. Every flash selector — role bindings and the default-chain entry — carries explicit `:high`. Alternative considered `:low` for background economy — rejected per explicit user direction.
- **D2: `task` stays giaoduc per user, gated on external credential verification.** Restores prior intent. The canonical "No live config mutation without approval" requirement demands isolated testing succeed for all providers, so `giaoduc/Advance:xhigh` MUST pass its direct smoke test before apply. If it fails with `401`, apply is blocked and the user must repair the credential independently. Its model-keyed chain (`giaoduc/Advance → [fable-5, sol]`) is runtime resilience for later regressions, not a substitute for the acceptance test. Alternative (bind task to fable-5 outright) rejected — user explicitly restored giaoduc.
- **D3: default chain ordered cockpit-luna → fable-5 → giaoduc → flash:high.** Live-success first, same-day-success second; giaoduc mid-chain (not first); flash as terminal hop. Omniroute dropped entirely per user directive.
- **D4: model-selector keys over role chains for coverage.** Cockpit pair gets mutual cross-fallback then provider jump to fable-5; antigravity uses the documented `google-antigravity/* → google/* → google-vertex/* → fable-5` wildcard so any antigravity model in any role is covered without per-role duplication. No role has both a role chain and a matching model key, avoiding precedence ambiguity.
- **D5: isolated smoke test is a hard gate; live update is atomic rename.** Per the modified `Isolated profile validation` requirement, all nine role selectors are smoke-tested in a throwaway profile; every one must return pong/exit 0 before `/Users/androidteam/.omp/agent/config.yml` is touched. The complete validated `config.yml` is staged as a temp file, permissions-set to match the live original, then atomically renamed over the live path — no in-place block replacement. Verification uses `omp config list --json` for selector readback, `uv run --with pyyaml python -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" /Users/androidteam/.omp/agent/config.yml` for YAML parse, and `diff -q` against baseline backups for rollback checks. The 401→fallback recovery check is a separate resilience scenario and cannot mark the giaoduc acceptance test complete.

## Risks / Trade-offs

- **Giaoduc key repair is a blocking prerequisite** — if `HERMES_CUSTOM_GIAODUC_API_KEY` cannot be restored, apply cannot complete under the canonical gate; the fallback is a user-approved scope change (e.g., task → fable-5), not a silent workaround.
- **`:high` on background roles costs more thinking tokens** than `:low` — accepted per explicit user direction; revisit if spend/latency becomes an issue.
- **Antigravity unproven in-session** (fresh cache, no observed call) → the isolated smoke test is the gate; post-rollout failures are mitigated by the `google-antigravity/*` chain and inherited default chain behind it.
- **Cockpit is localhost (51006)** → luna↔sol cross-fallback cannot cover full-cockpit outage; second hops leave the provider by design.
