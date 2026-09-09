## 1. Evidence and inventory

- [x] 1.1 Reconcile existing metadata-only inventory evidence for all declared worktrees and `.git` entries, including type, flags, exact metadata errors, and unknown hydration state; verify against the persisted lstat manifest and zero source mutations. This records evidence only and does not clear hydration or replacement gates.
- [x] 1.2 Reconcile existing redacted capacity and secret-name scan evidence, recording aggregate counts and logical bytes only; verify raw sensitive paths and contents are absent from OpenSpec artifacts, while the secret gate remains blocked.
- [x] 1.3 Record and reconcile the historical and later quarantine permission snapshots as distinct restricted evidence; verify the later snapshot records `0700` directories and `0600` files while quarantine remains excluded and the secret gate remains blocked.

## 2. Restricted bounded copy

- [x] 2.1 Record and reconcile the explicit non-sensitive allowlist and `.git`/cache exclusions from the bounded pilot; verify the evidence records seven copied and destination-verified files, without generalizing that result.
- [x] 2.2 In an explicitly authorized external implementation root, implement one-exact-source-path copy transactions using a same-filesystem temporary destination, flush/close, atomic no-overwrite install, read-back verification, and restricted per-file evidence; verify source preservation on every failure, reject symlink traversal at every source and destination ancestor, and provide external repository/commit evidence to this change.
- [x] 2.3 In the same separately authorized external implementation root, reject existing destination targets unless restricted evidence independently verifies matching source byte count and SHA-256; verify a matching target is reused without writing, mismatches remain conflicts, and focused external tests prove no-write reuse and collision safety.
- [x] 2.4 Reconcile the restricted quarantine outcome separately from the original pilot destination; verify the four flagged files were quarantined from `restricted-nonsecret/`, while the original `WHO-project-worktrees/` destination still contains seven pilot files including `vds-scripts-phase128/AGENTS.md`; record its read-only permission audit and classify the destination as retained pilot content, not an empty general recovery destination. The secret gate remains blocked.

## 3. Replacement verification

- [ ] 3.1 In a separately authorized external read-only investigation, locate or reconstruct a local Git backing store without Git probes that mutate or depend on unresolved iCloud pointers; verify backing-store identity independently and attach value-blind external evidence. The prior `backing_store_research.json` is mixed local/cloud metadata and cannot satisfy this task; `backing_store_research_allowlisted.json` and `backing_store_research_structural.json` are bounded-search evidence only. Negative search, generic `.git` directory hits, or an empty research root does not complete this task.
- [ ] 3.2 In the authorized external implementation root, for each candidate replacement clone or reconstruct locally and compare declared source scope, local changes, staged/unstaged/untracked state, and detached-HEAD evidence; verify incomplete comparisons leave replacement status unresolved and provide external commit/evidence identity.
- [x] 3.3 In the authorized external investigation, reconcile readable-byte coverage against the metadata projection and dataless-entry inventory; verify capacity pass does not advance readability.

## 4. Authorization and deletion safety

- [ ] 4.1 Accept an externally produced authorization record naming exactly one source path and referencing independently recorded replacement evidence; verify absent or mismatched authorization is rejected without mutation and retain only value-blind acceptance metadata centrally.
- [x] 4.2 Accept external verification that all-worktree, glob, directory, and unbounded deletion requests are rejected before mutation; verify no source path changes and record the external result without implementing deletion centrally.
- [ ] 4.3 Accept external evidence of deletion only after exact-path authorization, replacement verification, and evidence persistence all pass; verify no rollback is assumed, no bulk deletion path exists, and no central task completion occurs without the external identity and evidence.

## 5. Closure gates

- [x] 5.1 Keep readability, secret, replacement, and deletion gates explicitly blocked until their evidence conditions are independently satisfied; verify OpenSpec status and the external execution packet agree. Planning validation and negative research are not gate closure evidence.
- [x] 5.2 Run scoped OpenSpec validation and record the result; verify planning artifacts remain value-blind and no archive is created while any gate is unresolved.
