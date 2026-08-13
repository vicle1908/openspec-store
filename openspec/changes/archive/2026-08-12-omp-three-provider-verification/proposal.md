## Why

Three omp providers (shopapikey/fable-5, giaoduc/Advance, cockpit/gpt-5.6-luna)
were registered and verified through real CLI tests. The `default` role was
silently mutated during verification from `cockpit/gpt-5.6-luna:high` to
`giaoduc/Advance`. The `--model` flag was ruled out as the cause by a
disposable-profile persistence test. The actual cause remains unknown.

This change documents the verification evidence and restores the corrected
`default` role. The `default` role in `config.yml` was restored from `giaoduc/Advance` back to `cockpit/gpt-5.6-luna:high`, and `config.yml` permissions were restored from mode 600 to 644.

## What Changes

- Documents the verified state of all three providers and their role assignments.
- Records the permission restoration of `config.yml` from mode 600 back to 644.
- Preserves evidence that the earlier default-role drift cause is unknown.

## Non-Goals

- No provider registration or role reassignment beyond the corrective default-role fix.
- No cleanup of duplicate omp installations.
