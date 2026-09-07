## Context

Read-only audit found that the archived cloud-drive ledger has 9/13 checked tasks, with Google Drive/Desktop mutation claims unsupported by exact approvals and post-action evidence. Current path absence shows that some claimed deletions may have occurred, but absence does not establish authorization, target identity, or before/after verification.

## Goals / Non-Goals

**Goals:**

- Record exact non-iCloud cloud archive discrepancies with value-blind evidence.
- Distinguish observed absence from proven execution and authorized completion.
- Preserve release conditions for Google Drive/Desktop claims.
- Keep iCloud outside this change because another agent owns it.
- Verify archive immutability and structural validity.

**Non-Goals:**

- No archive edits.
- No iCloud move or deletion.
- No Google Drive, Desktop/Documents, cache, Trash, or personal-data mutation.

## Decisions

- Treat the archived task ledger, evidence files, and commit history as historical inputs; do not rewrite them.
- Classify `/Users/androidteam/My Drive/TDT (1)`, `/Users/androidteam/My Drive/VinID`, and `/Users/androidteam/Developer/go-microservices-cleanup-20260817.bundle` as observed absent and therefore potentially performed-but-unverifiable, not proven authorized deletions.
- Treat exact approvals, target manifests, rollback records, rclone/bisync evidence, and before/after checks as missing unless directly recorded.
- Store reconciliation evidence only in this active change. Leave the non-iCloud release gate unchecked until authorization and evidence are supplied.

## Risks / Trade-offs

- Current filesystem absence cannot prove authorized deletion or preserve personal-data intent.
- A corrective record documents historical inconsistency but cannot repair immutable archive claims.
- Excluding iCloud avoids conflicting with the separate owner and does not resolve those tasks.
