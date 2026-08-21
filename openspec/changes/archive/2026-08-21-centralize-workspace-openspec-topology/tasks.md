## 1. Establish the cleanup transaction

- [x] 1.1 Record the registered-store identity, global `defaultStore`, active-change inventory, and a per-repository fingerprint of every existing local `openspec/` directory; verify the ledger proves `/Users/androidteam/Developer/openspec-store/openspec` is the only current store corpus.
- [x] 1.2 Create and verify one isolated worktree and sole writer assignment for each affected repository before mutation; verify each worktree's base SHA, branch, and pre-existing dirty paths are recorded and unrelated work is excluded.

## 2. Remove redundant pointer-only roots

- [x] 2.1 In the `agent-core`, `agent-docs-sync`, `agent-harness`, `browser-cli`, and `code-daily-scan` worktrees, preflight that `openspec/` contains only the tracked `config.yaml` pointer, remove it with Git-aware scoped deletion, and verify unscoped and explicit-store commands resolve `openspec-store`.
- [x] 2.2 In the `go-microservices`, `jira-daily-reports`, `jira-epic-report`, `jira-kanban-from-spreadsheet`, and `jira-skill` worktrees, preflight that `openspec/` contains only the tracked `config.yaml` pointer, remove it with Git-aware scoped deletion, and verify unscoped and explicit-store commands resolve `openspec-store`.
- [x] 2.3 In the `ops-automation-suite`, `tdt-core`, `tdt-observability`, `tdt-sheets`, and `webhook-receiver` worktrees, preflight that `openspec/` contains only the tracked `config.yaml` pointer, remove it with Git-aware scoped deletion, and verify unscoped and explicit-store commands resolve `openspec-store`.
- [x] 2.4 For every pointer-only repository, verify the removed path no longer exists, `git diff --check` is clean, no non-OpenSpec file changed, and the repository-specific test or validation command selected at preflight still passes.

## 3. Migrate the ai-harness-skills schema resource

- [x] 3.1 In an isolated `ai-harness-skills` worktree, run GitNexus impact analysis for each source-resource resolver consumer and add focused red tests covering source-checkout discovery, bundled resource discovery, installer materialization, and doctor validation without an `openspec/` source directory.
- [x] 3.2 Move the `harness-13` schema/templates to a package-owned non-`openspec` resource location, introduce a single source-resource resolver, and update the CLI, installer, doctor, and affected tests; verify source resources are byte-equivalent and the old repository-local `openspec/` directory is absent.
- [x] 3.3 Run the focused schema-resource, installer, CLI, and doctor tests plus the repository's required lint/type gates; verify installed target projects still receive the expected `openspec/schemas/harness-13` output while the source repository has no `openspec/` directory.

## 4. Verify and hand off

- [x] 4.1 Run a workspace-wide directory audit and prove that only `/Users/androidteam/Developer/openspec-store/openspec` remains; verify none of the audited repository-local paths or compatibility links were recreated.
- [x] 4.2 Run `openspec store list --json`, global-default and explicit `--store openspec-store` resolution probes from representative cleaned worktrees, `openspec store doctor`, and strict shared-store validation; record command exits and selected roots without exposing credentials.
- [x] 4.3 Produce a final redacted ownership/rollback ledger containing every worktree, commit or uncommitted handoff state, removed path, schema resource destination, verification result, and excluded/blocked repository; verify no unrelated active change was archived, synced, or modified.
