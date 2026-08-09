## Why

The validated Hermes Agent `moa:default` runtime is not represented by a canonical OpenSpec capability or a maintained operational runbook, while stale direct-provider fields and a duplicate-primary fallback entry remain in `config.yaml`. This change reconciles specification, documentation, and configuration with the live MoA contract and records reproducible evidence without exposing credentials.

## What Changes

- Add a canonical `hermes-moa-configuration` capability for default model selection, exact `default`/`deep`/`fast` preset contracts, provider-level one-million-token context declarations, privacy, fallback, validation, and rollback.
- Add a maintained operational runbook under `docs/governance/hermes-moa-configuration.md` covering architecture, preset selection, inspection, health checks, cost/latency, partial failures, and rollback.
- Remove obsolete direct-provider `model.base_url` and `model.key_env` fields after source inspection confirms the MoA virtual-provider resolver uses `moa://local` and a placeholder key instead.
- Remove the duplicate `moa:default` first fallback because it resolves to the same backend identity as the primary and Hermes skips it before advancing.
- Preserve direct-provider fallbacks in order: `shopapikey:fable-5`, `giaoduc:Advance`, then `cockpit:gpt-5.6-luna`.
- Record sanitized validation evidence for YAML shape, normalized CLI output, direct inference, real MoA response/tool-call continuation, focused change validation, full-store validation, and store health.

## Capabilities

### New Capabilities

- `hermes-moa-configuration`: Govern the validated local Hermes MoA model topology, operational documentation, failover, and verification contract.

### Modified Capabilities

- None. Existing TDT application specs do not own the local Hermes runtime configuration.

## Impact

- **Configuration:** `/Users/androidteam/.hermes/config.yaml` (`model` stale-field cleanup and `fallback_providers` deduplication only).
- **Canonical specification:** `openspec/specs/hermes-moa-configuration/spec.md` after archive.
- **Documentation:** `docs/governance/hermes-moa-configuration.md`.
- **Runtime behavior:** primary remains `moa:default`; MoA presets remain unchanged; fallback skips one redundant same-primary entry and begins with the first viable direct provider.
- **Secrets:** credentials remain in `.env`; evidence records status and model/provider identities only.

## Non-Goals

- Do not change the three MoA preset model assignments, reasoning levels, token limits, temperatures, cadence, or privacy filter.
- Do not modify Hermes Agent framework source or upstream official documentation.
- Do not change delegation, compression, cron routing, approvals, tools, MCP servers, provider credentials, or provider endpoints.
- Do not rewrite archived historical changes solely because they describe superseded configurations.
- Do not stage or commit unrelated active changes.

## Rollback

Restore the pre-change sanitized configuration backup or re-add only the removed fallback entry and direct-model metadata if a verified runtime regression requires it. Rollback SHALL preserve secrets outside committed artifacts and SHALL be followed by `hermes config check`, `hermes config get model`, and a MoA smoke test.
