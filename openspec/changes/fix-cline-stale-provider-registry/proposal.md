# Proposal: Correct Cline OmniRoute provider registry

## Why

Cline 3.0.61 accepts a custom provider ID only when that ID is registered in
its `models.json` registry. The live settings file contains three stale
custom OmniRoute IDs with no registry entry: codex-compatible, codex-omniroute-chat, openai-omniroute-chat. Explicit invocations
through those IDs fail with `Unknown or disabled provider` before making an
HTTP request. The built-in `openai-compatible` provider is the working Cline surface
for the empirically proven versionless Chat Completions fallback.

Two verification defects were found while investigating this change:

1. A first cleanup attempt selected the wrong provider because the display
   layer mangled near-identical identifiers. The per-file rollback restored the
   settings byte-for-byte.
2. A second attempt ran negative controls against the live settings file.
   Cline persisted the explicitly selected unknown IDs, reintroducing stale
   entries and changing the last-used provider. This was a probe-isolation
   defect, not a gateway failure.

The current fix derives all provider IDs from parsed files and runs negative
controls in isolated temporary Cline homes. It asserts and retains the
canonical fallback model `sh/gpt-5.6-sol`. An earlier archived attempt recorded a
noncanonical model state; the current pre-apply evidence already shows the
canonical model, so this apply does not claim an unproven model transition.

## What Changes

- Remove only the three unregistered custom IDs from Cline `providers.json`.
- Preserve the built-in `openai-compatible` provider, set its model to
  `sh/gpt-5.6-sol`, and target `http://localhost:20128`.
- Repair `lastUsedProvider` when it points at a removed stale ID.
- Capture a mode-600 backup, hashes, atomic rollback evidence, and value-blind
  live verification.
- Require negative controls to use isolated temporary homes so verification
  cannot mutate the user's live settings.

## Impact

This is a corrective local configuration change. It does not modify Cline
source, the OmniRoute server, credentials, the Cline PM route, or unrelated
providers. It does not add a native Cline PM route.

## Non-Goals

- Do not edit archived OpenSpec artifacts.
- Do not rotate, print, or copy credential values into Git.
- Do not treat a raw HTTP success or an unregistered provider entry as a
  selectable Cline route.
