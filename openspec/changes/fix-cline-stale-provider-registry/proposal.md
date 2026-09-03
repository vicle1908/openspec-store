# Proposal: Remove stale Cline OmniRoute provider entries

## Why

Cline 3.0.61 had three custom OmniRoute provider entries that were not registered in its `models.json` provider registry. Explicit runs through those IDs failed with `Unknown or disabled provider` before any HTTP request was made. The verified working route is the built-in `openai-compatible` provider with model `sh/gpt-5.6-sol` and `baseUrl http://localhost:20128`; that route has passed a real `OMNIROUTE_DIALECT_OK` sentinel.

## What Changes

- Remove exactly the three stale, unregistered Cline provider entries from `~/.cline/data/settings/providers.json`.
- Preserve the working `openai-compatible` provider, its model and endpoint, and all unrelated settings.
- Preserve the existing default unless it points to a removed stale provider; in that case, repair it to the verified working provider.
- Capture a mode-0600 backup, value-blind pre/post hashes and modes, and post-change live sentinel evidence.
- Add a requirement that Cline custom provider IDs used for OmniRoute must be backed by a `models.json` registry entry, with default repair when the previous default pointed to a removed stale entry.

## Impact

This is a corrective configuration change. It does not change the OmniRoute server, Cline source, credentials, or unrelated providers. The Cline default is repaired only if it previously pointed to a removed stale provider.

## Non-Goals

- Do not add a Cline PM provider without a separately proven native route.
- Do not rotate, print, or copy credential values into Git.
- Do not edit archived OpenSpec artifacts.
