# Design: Cline provider registry cleanup

## Root Cause

Cline 3.0.61 resolves a provider ID only when that ID is registered in `~/.cline/data/settings/models.json` or is a built-in provider ID. The installed settings file contained three custom OmniRoute entries that were not registered. Explicit runs through those IDs failed with `Unknown or disabled provider` before any HTTP request was made.

The working OmniRoute route in Cline is the built-in `openai-compatible` provider with model `sh/gpt-5.6-sol` and `baseUrl http://localhost:20128`. That provider is registered and has passed a real `OMNIROUTE_DIALECT_OK` sentinel.

## Cleanup4 State

The cleanup4 apply removed exactly the three unregistered custom provider IDs and preserved the working `openai-compatible` provider. The default was repaired from the removed stale entry to the verified working provider. The file mode remained `0600`, and the pre/post SHA-256 values are recorded in `evidence/cline-provider-cleanup4-sentinel.json`.

## Correct Apply Strategy

1. Read `providers.json` and `models.json`; compute the stale set programmatically as settings provider IDs minus registry provider IDs minus built-in provider IDs. Never hand-type provider IDs.
2. Confirm the retained set contains the working `openai-compatible` provider and that its model and endpoint match the verified source pair.
3. Create a timestamped mode-600 backup before mutation.
4. Remove exactly the computed stale IDs with a same-directory atomic replace and preserve mode `0600`.
5. Repair `lastUsedProvider` only if it points to a removed stale ID; otherwise preserve it.
6. Verify JSON parsing, remaining provider IDs, the repaired default, the positive sentinel, and negative resolution failures for each removed ID.

## Verification

- **Positive:** an explicit sentinel through `openai-compatible` with model `sh/gpt-5.6-sol` exits `0` and returns `OMNIROUTE_DIALECT_OK` with no authentication, reconnect, or unknown-provider markers.
- **Negative:** each removed provider ID exits non-zero with `Unknown or disabled provider`.
- **Static:** `openspec validate fix-cline-stale-provider-registry --strict --store openspec-store` passes with zero issues, and `route-contract-check.py --phase candidate` passes all 17 checks.
- **Evidence:** value-blind only; record provider IDs, model, endpoint, mode, SHA-256 hashes, exit statuses, sentinel booleans, and the backup path. Never record credential values.

## Rollback

Restore the recorded mode-600 backup atomically if parsing or the positive sentinel fails. Cleanup4 did not require rollback; its backup path is retained in `evidence/cline-provider-cleanup4-sentinel.json`.
