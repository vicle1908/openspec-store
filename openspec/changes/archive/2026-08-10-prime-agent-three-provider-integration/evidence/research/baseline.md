# Research Baseline

Captured: 2026-08-09

## Prime Agent source identity

- Repository: `/Users/androidteam/Developer/prime-agent`
- Stable tag: `v0.7.1`
- Stable commit: `95afd319a78ae017a41241d50b013d656a0685ce`
- Audited current HEAD: `a18809e00ea30638584d87b3afea7285a9d7296c`
- The current HEAD is newer than the stable tag; release-specific claims were checked against `v0.7.1` source.

## Static execution evidence

- `npm ci`: native exit 0; 354 packages installed; audit summary reported 6 findings (5 high, 1 moderate).
- `npm run check`: native exit 0.
  - Biome: 900 files checked, no fixes.
  - TypeScript validation: passed.
  - Installer render check: passed.
  - Browser smoke check: passed.
- Production-only `npm audit --omit=dev --audit-level=high`: nonzero with 4 findings (3 high, 1 moderate). Findings are a rollout risk; no `npm audit fix` was applied.

## Provider discovery evidence

Credential values were never displayed or retained. Presence-only checks found all three named credential environment variables available. Authenticated model-catalog probes returned HTTP 200 JSON for:

- shopapikey: expected `fable-5` present;
- giaoduc: expected `Advance` present;
- cockpit: expected `gpt-5.6-sol`, `gpt-5.6-luna`, and `gpt-5.6-terra` present.

These are discovery/connectivity results only. They do not prove Prime Agent native inference, request shape, authentication header compatibility, streaming, tools, usage, or errors.

## Isolated registry evidence

A temporary `PRIME_AGENT_CODING_AGENT_DIR` loaded the proposed five models through Prime Agent's real model registry. `prime-agent model list` showed the intended provider/model pairs. The temporary probe directory was removed afterward. No global Prime Agent binary or `~/.prime/agent` state was created.

## Installer evidence

A reviewed copy of the official installer was retained as `install.sh` under this directory.

- Source URL: `https://app.primeintellect.ai/prime-agent/install.sh`
- Captured size: 45,265 bytes
- SHA-256: `38d14a1be73b325652c7ce8342e3bf19335721837192855a7907732caf8e6d04`
- This hash identifies the captured bytes; it is not an upstream signature. Re-fetch and compare before apply. Any change requires re-inspection and review.
