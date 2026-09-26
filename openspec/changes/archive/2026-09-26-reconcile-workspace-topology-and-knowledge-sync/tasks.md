# Tasks

## 1. Documentation Reconciliation

- [x] 1.1 Reconcile `docs/WORKSPACE_TOPOLOGY.md` by removing the nonexistent `shared/` directory and documenting universal workspace meta-roots (`docs/`, `scripts/`, `wiki/`, `data/`, `sensitive-quarantine/`) directly at `~/Developer/`.
  - Verification: Verify with `grep -F "shared/" docs/WORKSPACE_TOPOLOGY.md` that no phantom wrapper remains.
- [x] 1.2 Document auxiliary domain directories (`apps/`, `ai-tooling/`, `study/`, `migration-archives/`, `legacy/`, `cursor-account-manager-build/`, `main-db-migrations/`, `ntu-keynote/`) in `docs/WORKSPACE_TOPOLOGY.md`.
  - Verification: Compare listed top-level directories against `ls -d /Users/androidteam/Developer/*/`.
- [x] 1.3 Update `wiki/concepts/openspec-change-lifecycle.md` and `wiki/concepts/workspace-domain-topology.md` to reference `platform/openspec-store` and current organization namespaces.
  - Verification: Run `grep -n "platform/openspec-store" wiki/concepts/openspec-change-lifecycle.md`.

## 2. Automation & Knowledge Sync Path Fixes

- [x] 2.1 Patch both `~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh` and `platform/openspec-store/scripts/knowledge-refresh/sync-notion-knowledge.sh` to point `OPENSPEC_STORE_ROOT` and Python `store_specs` discovery to `${WORKSPACE_ROOT}/platform/openspec-store`, dynamically scan active changes, and verify `diff -u` between the two files is empty.
  - Verification: Run `diff -u /Users/androidteam/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh /Users/androidteam/Developer/platform/openspec-store/scripts/knowledge-refresh/sync-notion-knowledge.sh` and verify exit code 0 and empty output.
- [x] 2.2 Add a fail-closed assertion in both `sync-notion-knowledge.sh` copies that aborts with an explicit error code if spec discovery returns zero specifications.
  - Verification: Inspect the embedded Python script error handling block in both copies and verify identical behavior via `diff -u`.
- [x] 2.3 Reconcile `knowledge-refresh-inventory.tsv` from `~/Developer/scripts/knowledge-refresh/` to `platform/openspec-store/scripts/knowledge-refresh/`, and update `knowledge-refresh-approval.sha256` in both directories to `5a0366fa97474a8acae28546df9054b551fcb5f0143d3582bc5bc501eb469acc`.
  - Verification: Run `diff -u /Users/androidteam/Developer/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv /Users/androidteam/Developer/platform/openspec-store/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` and verify exit code 0; run `diff -u /Users/androidteam/Developer/scripts/knowledge-refresh/knowledge-refresh-approval.sha256 /Users/androidteam/Developer/platform/openspec-store/scripts/knowledge-refresh/knowledge-refresh-approval.sha256` and verify exit code 0.
## 3. Verification & Validation

- [x] 3.1 Execute a dry-run test with `bash scripts/knowledge-refresh/sync-notion-knowledge.sh --dry-run --section specs` and verify that all ~422 specifications are enumerated in `.knowledge-refresh/openspec-domain-catalog.md`.
  - Verification: Inspect generated catalog summary line in `.knowledge-refresh/openspec-domain-catalog.md` to confirm count >= 420.
- [x] 3.2 Verify that `openspec/specs/` remains completely unmodified and untracked in git, confirming delta spec isolation (`changes/.../specs/...`) is strictly maintained.
  - Verification: Run `git -C platform/openspec-store status -s openspec/specs` and confirm zero changes.
- [x] 3.3 Run `bash /Users/androidteam/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh --check` and verify it passes cleanly without inventory SHA-256 mismatch.
  - Verification: Command exits with status code 0 and outputs no inventory mismatch error.
- [x] 3.4 Validate change artifacts in `openspec-store` using `openspec validate reconcile-workspace-topology-and-knowledge-sync --store openspec-store --strict --json`.
  - Verification: CLI returns exit code 0 and valid status.
