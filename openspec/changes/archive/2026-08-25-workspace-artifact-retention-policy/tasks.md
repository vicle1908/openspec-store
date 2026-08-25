## 0. Implementation surface and policy inputs

- [x] 0.1 Name the owning workspace-state path and inventory producer for the retention policy. Verify: design.md identifies `~/Developer/.workspace-retention/retention-inventory.json` and the lifecycle consumer.
- [x] 0.2 Declare `workspace-lifecycle-gated-cleanup` as the downstream consumer of this policy and define the handoff format for protected and candidate classes. Verify: both change artifacts reference the same class and policy-state values.

## 1. Retention classification contract

- [x] 1.1 Define the reviewed retention classes and policy states in the spec and confirm that each requirement has explicit WHEN/THEN scenarios. Verify: `openspec validate workspace-artifact-retention-policy --strict --store openspec-store` passes and covers active indexes, generated caches, permanent fixtures, ephemeral fixtures, runtime state, evidence, rollback, and operator-preserved files.
- [x] 1.2 Capture observed evidence from the current workspace for active index owners, generated caches, runtime state stores, tracked fixtures, temporary fixtures, retained reports, nested `_evidence`/`_backups`/`_patches`, rollback artifacts, and operator-preserved files. Verify: evidence records canonical paths and provenance without exposing secrets.

## 2. Retention inventory design

- [x] 2.1 Define the machine-readable inventory shape: path, class, policy state, owner, provenance, justification, last reference, candidate flag, and review metadata. Verify: schema validation rejects missing identity, stale provenance, and secret/request-body fields.
- [x] 2.2 Store the reviewed policy and operational inventory under `~/Developer/.workspace-retention/retention-inventory.json`. Verify: reload preserves the policy identity and rejects an unapproved or malformed inventory.
- [x] 2.3 Add provenance freshness checks bound to repository revision, evidence identity, or runtime observation time. Verify: stale or missing provenance downgrades entries to `REVIEW_REQUIRED`.

## 3. Cleanup integration contract

- [x] 3.1 Require cleanup workflows to read the retention inventory as an exclusion list and skip protected-class paths in dry-run and approved retirement flows. Verify: protected evidence, rollback, permanent fixtures, and active-index paths are skipped with recorded reasons.
- [x] 3.2 Require candidate items to be proposed for review, not deleted automatically, and require cleanup to record protected-class reasons for skipped paths. Verify: an ephemeral fixture produces a review proposal and no filesystem mutation.

## 4. Runtime ownership coverage

- [x] 4.1 Cover approved index/watchers, active processes, Orca workspaces, persistent databases/state stores, retained evidence, rollback snapshots, and operator-preserved files in the first policy. Verify: each class has an owner or explicit `UNKNOWN` result.
- [x] 4.2 Treat unavailable LaunchAgent or container adapters as `UNKNOWN` and block reclamation. Verify: adapter failure cannot produce a `RECLAIMABLE` state or deletion recommendation.
