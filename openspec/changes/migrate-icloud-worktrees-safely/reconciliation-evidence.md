# Hydrated-only reconciliation evidence

- **Source root:** `/Users/androidteam/Developer/WHO-project-worktrees/`
- **Destination root:** `/Users/androidteam/Developer/vds-content-migration/WHO-project/`
- **Manifest:** `/Users/androidteam/Developer/vds-content-migration/migration-manifest.json`
- **Observed result:** 16,114 manifest entries; approximately 3.1 GB at the destination; six files in the sensitive quarantine (aggregate only; no names or contents recorded).
- **Provenance:** This records a deliberate, already-executed hydrated-only reconciliation run for operational evidence. It was outside the explicit seven-file non-sensitive allowlist and outside the restricted-copy contract; it is not a general recovery snapshot and must not be generalized as one.
- **Safety status:** No dataless batches were authorized or started. The source was preserved and not deleted, moved, or otherwise mutated.
- **Verification scope:** Verification was limited to the 16,114 destination entries represented by the manifest. This note records aggregate/value-blind evidence only.
- **Gate status:** This out-of-contract execution does **not** close tasks 2.1, 2.4, 3.1, 3.2, any 4.x task, or 5.1. Those tasks remain governed by the explicit restricted-copy contract and their existing evidence requirements.
