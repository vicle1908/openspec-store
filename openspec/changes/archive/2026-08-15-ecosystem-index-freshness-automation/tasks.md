# Tasks: Ecosystem Index Freshness Automation

## 0. Provider and prerequisite reconciliation

### 0.1 Record official provider identity

- [x] Record Graphify upstream as `https://github.com/Graphify-Labs/graphify`
- [x] Record PyPI package `graphifyy`, CLI `graphify`, version `0.9.42`
- [x] Record GitNexus version `1.6.9`
- [x] Remove all obsolete alternate-provider references from this change

### 0.2 Complete Graphify upgrade evidence

- [x] Upgrade `graphifyy` from 0.9.38 to 0.9.42 using `uv tool install --python 3.12 --force 'graphifyy[all,postgres]==0.9.42'`
- [x] Update Graphify skills with `graphify install --strict`
- [x] Validate FIFO/non-regular-file extraction does not hang
- [x] Validate same-length rewrite through `graphify update .`
- [x] Validate `built_at_commit` provenance on full extraction
- [x] Restart and verify the active watcher after upgrade
- [x] Update `go-microservices/scripts/knowledge-tools.sh` legacy pin to 0.9.42

### 0.3 Correct upstream provider contract

- [x] Modify the main `developer-code-intelligence` spec to identify Graphify-Labs `graphifyy` as the official provider
- [x] Remove stale alternate-provider claims from the main spec
- [x] Validate the resulting spec and cross-repository references

## 1. Create reviewed repository inventory

### 1.1 Define inventory format

Create `openspec-store/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` with columns:

```text
canonical_root<TAB>default_branch<TAB>gitnexus_enabled<TAB>graphify_enabled
```

### 1.2 Populate inventory

- [x] Include only explicitly approved repositories
- [x] Use canonical absolute paths under `~/Developer/`
- [x] Record each repository's actual default branch
- [x] Exclude workspace root and non-repositories
- [x] Deduplicate linked worktrees by Git common directory

### 1.3 Validate inventory

- [x] Reject paths outside approved workspace roots
- [x] Reject missing/non-Git paths
- [x] Reject missing default branches
- [x] Compute and log normalized inventory SHA-256
- [x] Add a test fixture for path escape and unlisted repository

## 2. Implement central refresh script

Create `openspec-store/scripts/knowledge-refresh/refresh-knowledge-indexes.sh`.

### 2.1 Shell safety and environment

- [x] Use Bash with `set -euo pipefail`
- [x] Use absolute tool paths or explicit PATH
- [x] Never print credentials or environment secrets
- [x] Use canonical path resolution before operating
- [x] Create bounded log directory

### 2.2 Inventory and target validation

- [x] Load and validate the reviewed inventory
- [x] Validate Git common directory and configured branch
- [x] Exclude unlisted repositories
- [x] Record inventory digest in each run

### 2.3 State guards

- [x] Skip dirty repositories/worktrees with `skipped_dirty`
- [x] Skip merge/rebase/cherry-pick state with `skipped_merge_state`
- [x] Skip detached, ephemeral, and >30-day stale worktrees
- [x] Skip uninitialized provider state with `skipped_uninitialized`

### 2.4 PID-aware locks

- [x] Implement canonical-path-derived lock identifiers
- [x] Acquire via atomic `mkdir`
- [x] Record PID, owner, timestamp, and canonical target
- [x] Reclaim only when owner PID is dead
- [x] Never steal a live lock based on age
- [x] Release locks using `trap`
- [x] Add lock-busy, dead-owner, and cleanup tests

### 2.5 GitNexus refresh

- [x] Verify GitNexus 1.6.9
- [x] Run `gitnexus analyze . --index-only --default-branch <inventory-branch>`
- [x] Apply five-minute per-target timeout
- [x] Capture target HEAD before execution
- [x] Verify indexed revision after execution
- [x] Report `superseded` when HEAD changes during execution
- [x] Never enable embeddings, PDG, `--force`, or package fallback

### 2.6 Graphify refresh

- [x] Verify Graphify-Labs `graphifyy` 0.9.42
- [x] Detect active `graphify watch` for the target root
- [x] Report `watcher_active` and skip scheduled Graphify for watched roots
- [x] Run routine `graphify update .`
- [x] On missing/corrupt graph or update failure, run bounded `graphify extract . --code-only`
- [x] Set `GRAPHIFY_VIZ_NODE_LIMIT=0` for foreground refresh
- [x] Preserve last usable output on failure
- [x] Verify `graphify-out/graph.json` parses after success

### 2.7 Worktree refresh

- [x] Enumerate worktrees using `git worktree list --porcelain`
- [x] Refresh only worktrees with existing `.gitnexus/` or `graphify-out/`
- [x] Report missing state as `skipped_uninitialized`
- [x] Keep worktree indexes independent from main checkout

### 2.8 Timeouts and logs

- [x] Enforce five-minute per-target timeout
- [x] Enforce two-hour overall timeout
- [x] Log target, provider, status, duration, target revision, indexed revision
- [x] Rotate logs to a bounded size
- [x] Emit machine-readable event lines

## 3. Implement status command

Create `openspec-store/scripts/knowledge-refresh/knowledge-status.sh`.

### 3.1 Human output

- [x] List every inventoried repository
- [x] List all eligible worktrees
- [x] Report GitNexus status: `FRESH`, `STALE`, `UNKNOWN`, `UNINITIALIZED`
- [x] Report Graphify status: `FRESH`, `STALE`, `WATCHER`, `UNKNOWN`, `UNINITIALIZED`
- [x] Report dirty file count and branch
- [x] Report lock state and active owner

### 3.2 JSON output

- [x] Implement `--json`
- [x] Emit bounded valid JSON
- [x] Include inventory digest and generation timestamp
- [x] Include provider version and indexed/current revisions

## 4. Implement post-merge dispatcher and installer

Create `openspec-store/scripts/knowledge-refresh/install-hooks.sh`.

### 4.1 Managed block

- [x] Add `knowledge-gitnexus-post-merge-start/end` markers
- [x] Dispatcher only; no lock acquisition in hook
- [x] Dispatch asynchronously to central refresh script
- [x] Check configured default branch
- [x] Preserve Graphify-owned hook blocks byte-for-byte

### 4.2 Installation

- [x] Enumerate approved inventory only
- [x] Resolve Git common directory
- [x] Install once per common directory
- [x] Back up hooks before mutation
- [x] Make installation idempotent
- [x] Validate hooks with `sh -n`
- [x] Provide rollback using backups

### 4.3 Hook tests

- [x] Local merge to default branch dispatches
- [x] Non-default branch does not dispatch
- [x] Dirty tree dispatch is safely skipped by central script
- [x] Existing Graphify behavior remains unchanged
- [x] Repeated installation produces no diff
- [x] Linked worktrees do not duplicate the block

## 5. Implement and install LaunchAgent

### 5.1 Plist

Create `openspec-store/scripts/knowledge-refresh/com.developer.index-refresh.plist.template`:

- [x] `StartCalendarInterval` at 02:30 local time
- [x] No persistent keep-alive key for the batch job
- [x] Absolute `/bin/bash` and script paths
- [x] Explicit PATH containing `~/.npm-global/bin`, `~/.local/bin`, Homebrew, and system paths
- [x] Explicit HOME and WorkingDirectory
- [x] Separate stdout/stderr log paths

### 5.2 Lifecycle

- [x] Install with `launchctl bootstrap gui/$(id -u)`
- [x] Verify with `launchctl print gui/$(id -u)/com.developer.index-refresh`
- [x] Trigger manually with `launchctl kickstart -k gui/$(id -u)/com.developer.index-refresh`
- [x] Capture launchd stdout/stderr
- [x] Do not claim durable `graphify watch` lifecycle in this change

## 6. Documentation and specification alignment

### 6.1 AGENTS.md

- [x] Remove nonexistent weekly cron claim
- [x] Document actual LaunchAgent, inventory, status command, and local-hook scope
- [x] Document Graphify-Labs/graphify identity and version

### 6.2 `.claude/CLAUDE.md`

- [x] Replace stale GitNexus warning with automated refresh guidance
- [x] Replace stale Graphify warning with `graphify update .` guidance
- [x] Document dirty-tree and watcher limitations
- [x] Remove nonexistent weekly cron claim

### 6.3 OpenSpec main specs

- [x] Correct `developer-code-intelligence` Graphify provider identity
- [x] Add scheduled-refresh authorization scenario to `gitnexus-stable-contract`
- [x] Keep `workspace-index-freshness` as a separate new capability
- [x] Do not modify `refresh-gitnexus-index-groups` unless an independent relationship requires it

## 7. Verification gates

### 7.1 Static gates

- [x] `bash -n` all shell scripts
- [x] `plutil -lint` LaunchAgent
- [x] `openspec validate ecosystem-index-freshness-automation --strict`
- [x] Full stale-reference sweep across proposal, design, spec, tasks, main specs, docs, and scripts
- [x] Verify no alternate Graphify provider, legacy pin, age-only lock stealing, or wrong CLAUDE path remains

### 7.2 Functional gates

- [x] Refresh script runs against a disposable clean repo
- [x] GitNexus refresh uses exact pinned command
- [x] Graphify update succeeds on a clean fixture
- [x] Graphify extract repair succeeds on a clean fixture
- [x] Dirty repository is skipped
- [x] Merge-state repository is skipped
- [x] Live lock causes clean skip
- [x] Dead lock is reclaimed
- [x] Watcher-active Graphify target is skipped
- [x] Hook installer is idempotent
- [x] Hook syntax passes for all approved repositories
- [x] Status table and JSON parse correctly
- [x] LaunchAgent loads, prints, and kickstarts successfully

### 7.3 Evidence

- [x] Save redacted version/digest evidence
- [x] Save inventory digest
- [x] Save hook installation manifest
- [x] Save functional test results
- [x] Save final status JSON
- [x] Record known limitation: `post-merge` covers local merge/merge-pull only, not remote PR merge or `git pull --rebase`
