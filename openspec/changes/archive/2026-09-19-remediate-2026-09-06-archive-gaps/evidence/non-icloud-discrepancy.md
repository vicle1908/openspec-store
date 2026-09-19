# Non-iCloud Archive Discrepancy Evidence

## Scope

This read-only reconciliation covers only the Google Drive and Desktop/Documents portions of the archived cloud-drive change. iCloud operations are explicitly excluded because another agent owns that scope. The realtime archive is excluded because its later evidence is self-correcting in archive history.

## Cloud-drive archive

The archived ledger at `openspec/changes/archive/2026-09-06-cloud-drive-migration/tasks.md` contains 9 checked and 4 unchecked task items. The checked non-iCloud claims are `2.2`, `4.1`, `4.2`, and `5.1`.

Observed current path state indicates that some claimed operations may have occurred, but it does not prove authorization or the required execution chain:

- `/Users/androidteam/My Drive/TDT (1)` is absent.
- `/Users/androidteam/My Drive/VinID` is absent.
- `/Users/androidteam/Developer/go-microservices-cleanup-20260817.bundle` is absent.
- `/Users/androidteam/My Drive/tdt` and its documented keep paths remain present.
- Desktop and Documents remain present, but protected-path preservation is not established by the available evidence.

Classification: **performed-but-unverifiable where absence is directly observed; otherwise unsupported claim**. The archive evidence contains no exact approval manifest, exact deletion-target register, rollback record, or before/after verification sufficient to establish authorized execution.

## Safety and boundaries

- No archive file was edited.
- No Google Drive, Desktop/Documents, iCloud, cache, Trash, or personal-data mutation was executed.
- iCloud tasks are outside this change.
- All non-iCloud release conditions remain blocked pending exact evidence or explicit owner decisions.

## Archive immutability observation

The realtime archive evidence file `openspec/changes/archive/2026-09-06-align-realtime-vitest-docs/evidence/verification.md` has post-archive commit history (`7d06e685`, `a50f2c69`, `eb5daed0`, `9867d4a9`, `4eacc945`, `9adffbd5`), while the current working tree is clean for this path. This is recorded as an archive-provenance anomaly; the archive file is not edited or reverted by this change. The later evidence continues to record the canonical gate exit 1.
