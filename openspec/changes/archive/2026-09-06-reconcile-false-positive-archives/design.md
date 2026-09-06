## Context

The immutable archive contains 2026-09-06 ledgers for cloud-drive migration and realtime Vitest documentation whose checked-task counts conflict with directly observed active-state evidence and known verification outcomes.

## Goals / Non-Goals

**Goals:**

- Establish a value-blind claim matrix for the affected archive ledgers.
- Preserve exact task identifiers, counts, paths, and release conditions.
- Reopen unsupported approval and verification gates in the corrective change.
- Keep archive history immutable and separate from the corrective evidence.

**Non-Goals:**

- No edits under `openspec/changes/archive/`.
- No cloud, personal-data, cache, Trash, or repository cleanup.
- No rerun of the known crashing full Vitest suite as a prerequisite for this evidence record.

## Decisions

- Use the two affected archive directories as the authoritative historical inputs.
- Record the cloud discrepancy as archived 9/13 checked versus active 5/13 checked, with tasks 3.1, 3.2, 6.1, and 6.2 unsupported by the archived ledger's own checked state and requiring renewed evidence.
- Record the realtime discrepancy as archived 8/8 checked while the full-suite gate is known to terminate with exit 134; focused checks do not replace that gate.
- Keep cloud mutation tasks blocked until exact paths, exact operations, and post-action evidence exist.
- Keep the full-suite task blocked until a green full-suite run or explicit approved exclusion policy exists.
- Verify archive immutability with a path-limited Git diff and store all corrective evidence below this active change.

## Risks / Trade-offs

- A corrective record cannot repair misleading historical checkboxes; it can only make the discrepancy and release conditions durable.
- Re-running cloud operations without exact target approval could delete personal or synchronized data.
- Treating focused Vitest tests as a full-suite result would preserve the false-positive closure.
