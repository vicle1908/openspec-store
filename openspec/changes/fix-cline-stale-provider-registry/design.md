# Design: Cline provider registry cleanup and route correction

## Root Cause

Cline resolves a provider ID only when that ID is registered in `~/.cline/data/settings/models.json` or is a built-in provider ID. The pre-cleanup4 settings file contained three custom OmniRoute entries that were absent from the registry and failed explicit resolution with `Unknown or disabled provider`. The retained `openai-compatible` entry still used model `sh/codex`, while the source-derived Cline route contract requires `sh/gpt-5.6-sol`.

## Cleanup4 State

The cleanup4 backup is mode `0600` and SHA-256 `ef00b4b8d009678c9be1ed2841d948bef8737694d35c4f2e828936f9085d596c`, byte-identical to the recorded pre-apply state. The apply removed exactly the three stale IDs, updated `openai-compatible` from `sh/codex` to `sh/gpt-5.6-sol`, and repaired `lastUsedProvider` from `openai-omniroute-chat` to `openai-compatible`. The final file remains mode `0600`, has one provider, and hashes to `3b48ffa092515f070210c6ac5301a6273daffa37559d4a05be034863d5f27c17`.

## Correct Apply Strategy

1. Read `providers.json` and `models.json`; compute the stale set programmatically as settings provider IDs minus registry provider IDs minus built-in provider IDs. Never hand-type provider IDs.
2. Confirm the retained set contains `openai-compatible` and that `lastUsedProvider` is repaired only when it points to a removed stale entry.
3. Create a timestamped mode-600 backup before mutation and record its mode, SHA-256, and byte-identity result.
4. Remove exactly the computed stale IDs with a same-directory atomic replace and preserve mode `0600`.
5. Update the retained provider’s model to the source-derived canonical value `sh/gpt-5.6-sol` and preserve `baseUrl http://localhost:20128`.
6. Verify JSON parsing, final provider IDs, repaired default, the static route contract, a cleanup4-specific positive live sentinel, and per-ID negative controls.

## Verification

- **Static:** `openspec validate fix-cline-stale-provider-registry --strict --store openspec-store` passes with zero issues, and `route-contract-check.py --phase candidate` passes all 17 checks.
- **Positive live sentinel:** PENDING. A cleanup4-specific positive route through the final `openai-compatible` + `sh/gpt-5.6-sol` pair must be recorded before closure.
- **Negative controls:** PENDING. Each removed provider ID must be explicitly re-probed after the final state and recorded as failing with `Unknown or disabled provider`.
- **Evidence:** value-blind only; record provider IDs, model, endpoint, mode, SHA-256 hashes, exit statuses, sentinel booleans, and the backup path. Never record credential values.

## Rollback

Restore the recorded mode-600 backup atomically if parsing or the positive sentinel fails. Cleanup4 did not require rollback; its backup identity is recorded in `evidence/cline-provider-cleanup4-sentinel.json`.
