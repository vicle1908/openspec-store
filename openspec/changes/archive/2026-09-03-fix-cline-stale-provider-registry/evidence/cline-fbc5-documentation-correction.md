# Cline FBC-5 Documentation Correction

## Scope

Archived artifacts are immutable. This document supersedes only the stale
provider-ID and route details in the archived FBC-5 narrative; it does not edit
archived bytes.

## Archived Claims Requiring Correction

The archived document
`archive/2026-08-31-reconcile-omniroute-dialects-archive-gaps/evidence/cline-fbc5-resolution.md`
contains the following historical claims:

- Lines 7-11 describe custom provider IDs and say `codex-compatible` is the accepted
  custom-base-URL provider, then record model `sh/codex` and a versioned
  `/v1` base URL.
- Lines 15-16 claim the live sentinel was proven through that provider/model
  pair.
- Lines 22-29 classify `codex-compatible` as the Cline fallback provider and
  `sh/codex` as the resolved SH route.

Those claims are stale for the installed Cline 3.0.61 runtime and the current
configuration. They must not be reused as the current route contract.

## Current Authoritative Classification

The installed Cline runtime recognizes `openai-compatible` as the built-in provider
for this route. The current settings file contains only that provider after
cleanup. Its canonical route is:

- provider: `openai-compatible`
- model: `sh/gpt-5.6-sol`
- base URL: `http://localhost:20128`
- endpoint: versionless `/chat/completions`
- PM `pm/Claude-Fable`: not servable through this Cline provider surface

The unregistered custom IDs removed by this change are exactly:
`codex-compatible`, `codex-omniroute-chat`, `openai-omniroute-chat`.
Explicit negative controls for each ID fail with `Unknown or disabled provider`
in isolated temporary homes. The live positive sentinel through the retained
built-in provider exits 0 with `OMNIROUTE_DIALECT_OK`.

## Evidence

- `cline-provider-cleanup4-preapply.json` records the parsed pre-apply provider
  set, bundle-derived built-in-ID source, computed stale set, and mode-600
  backup.
- `cline-provider-cleanup4-sentinel.json` records the positive live result,
  isolated negative controls, repaired default, and post-probe hash without
  credential values.
- The archived `route-contract-check.py --phase candidate` result passes all
  17 checks after the correction.

## Security and Provenance

No archived file was edited. This correction records provider IDs, model IDs,
endpoint paths, hashes, statuses, and modes only; it records no credential
values.
