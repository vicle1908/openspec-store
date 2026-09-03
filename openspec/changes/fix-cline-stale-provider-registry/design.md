# Design: Cline provider registry cleanup

## Root Cause

Cline's installed runtime has two provider lanes: built-in provider IDs and
custom provider IDs loaded from `~/.cline/data/settings/models.json`. The
settings file had stale custom entries (codex-compatible, codex-omniroute-chat, openai-omniroute-chat) without matching model
registry entries. The installed runtime therefore reports `Unknown or disabled
provider` for those IDs. The built-in `openai-compatible` provider is independently
registered by Cline and reaches the OmniRoute fallback.

The canonical Cline fallback is model `sh/gpt-5.6-sol` at
`http://localhost:20128/chat/completions`. Earlier archived evidence recorded a
noncanonical model state, but the current pre-apply record shows the canonical
model already present; the corrective apply asserts and preserves it rather
than relying on a cross-model sentinel.

## Previous Probe Failures

- Attempt 1 removed the working provider due to display-layer identifier
  confusion; its positive control failed and the file was rolled back from a
  mode-600 backup.
- Attempt 2 correctly removed stale IDs but ran negative controls against the
  live file. Cline's settings manager saved each explicit unknown selection,
  reintroducing those IDs. The live file then drifted and the route checker
  failed. This change retains that failure as evidence and never uses live
  negative controls again.

## Correct Apply Strategy

1. Parse live `providers.json` and `models.json`.
2. Extract the installed Cline built-in provider IDs from the installed bundle
   and generated provider-ID declaration. Compute
   `stale = settings_ids - registry_ids - builtin_ids`.
3. Assert the computed set excludes the built-in `openai-compatible` provider and that
   the retained entry has base URL `http://localhost:20128`.
4. Create a timestamped mode-600 backup before mutation.
5. Atomically remove exactly `stale`, assert/retain the canonical model
   `sh/gpt-5.6-sol`, and repair `lastUsedProvider` only if it points to a removed ID.
6. Run the positive sentinel once through the live retained provider. Run each
   negative control only in a temporary isolated Cline home.
7. Confirm the live settings file remains semantically equal to the expected
   post-apply document after all probes. Roll back atomically on any failure.

## Verification

- Positive live route: provider `openai-compatible`, model `sh/gpt-5.6-sol`, base URL
  `http://localhost:20128`, versionless endpoint `/chat/completions`, exit 0, exact
  `OMNIROUTE_DIALECT_OK`, and no auth/reconnect/unknown-provider error.
- Negative isolated controls: each removed ID exits non-zero with
  `Unknown or disabled provider`; no live settings file is touched.
- Post-apply JSON parses, mode remains 0600, unrelated settings are preserved,
  stale IDs are absent, and the default points to the retained provider.
- OpenSpec strict validation and the archived 17-check route contract are run
  before closure.

## Rollback

Restore the recorded mode-600 backup atomically if parsing, semantic
comparison, or the positive sentinel fails. Temporary negative-control homes
are removed after evidence capture.
