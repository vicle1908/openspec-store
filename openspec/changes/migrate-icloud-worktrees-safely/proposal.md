## Why

The iCloud project tree contains worktrees whose Git backing state is unresolved, dataless metadata, potentially unique local changes, and sensitive-looking files; migration must preserve source state and fail closed rather than delete or bulk-copy unverified content.

## What Changes

- Add a metadata-only inventory and evidence contract for iCloud worktrees, including `.git` pointer type, `st_flags`, `SF_DATALESS` observations, exact metadata errors, and unknown hydration state.
- Add capacity and readability gates that distinguish logical-size projections from successfully readable bytes.
- Define a bounded restricted-file pilot procedure that excludes `.git`, performs destination read-back verification, and records per-file bytes, hashes, and errors in access-restricted external evidence; OpenSpec references only aggregate/status metadata.
- Define an authorized manual copy procedure for targeted non-destructive file or pointer capture under explicit user authorization: requires same-filesystem temporary destination, flush/fsync, atomic no-overwrite install, destination read-back hash verification, source preservation on failure, and value-blind external evidence logging.
- Quarantine pilot content when local content detection finds sensitive assignments; keep the general recovery destination unavailable for further batches until retained pilot content is independently dispositioned, and keep the secret gate blocked.
- Require local snapshot or verified clone/replacement validation before any iCloud source deletion.
- Prohibit bulk deletion of linked worktrees and preserve unresolved local-only, orphaned, detached, staged, unstaged, and untracked state.
## Capabilities

### New Capabilities

- `icloud-worktree-migration-safety`: Metadata-only inventory, capacity/secret gates, bounded restricted copying, quarantine handling, replacement verification, and deletion authorization for iCloud worktrees.

### Modified Capabilities

None.

## Impact

- Planning artifacts and value-blind evidence live under this change in the registered `openspec-store`.
- Implementation and source data remain outside the OpenSpec store; this change does not authorize moving or deleting iCloud files by itself.
- Existing `remediate-2026-09-06-archive-gaps` remains untouched; its explicit no-iCloud boundary is preserved.
- Existing evidence is referenced by metadata-only artifact paths; sensitive contents and raw sensitive paths are not copied into OpenSpec artifacts.

## Non-Goals

- No iCloud source deletion or move in this planning change.
- No bulk removal of the 46 worktrees.
- No assumption that a linked-worktree `.git` pointer proves a surviving backing store.
- No assumption that `SF_DATALESS` proves the entire tree is unreadable.
- No copying of `.git`, `.env*`, credential, token, password, secret, key, or certificate paths into the general recovery destination; any targeted manual copy of `.git` pointers or metadata into restricted evidence storage requires explicit, separate user authorization naming the exact source paths.
- No claim that the bounded restricted-file pilot generalizes to all worktrees: the restricted external pilot manifest records 7 copied and destination-verified allowlisted files across its recorded entries, with no read failures and Git excluded. Per-file details remain access-restricted external evidence; the remaining 11 allowlisted candidates were not copied.
- Separate restricted reconciliation evidence records four files later quarantined after content scanning; quarantine outcomes are not attributed to the pilot manifest.
- No archive modification or archive-gap remediation.
