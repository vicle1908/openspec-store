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

- [ ] Modify the main `developer-code-intelligence` spec to identify Graphify-Labs `graphifyy` as the official provider
- [ ] Remove stale alternate-provider claims from the main spec
- [ ] Validate the resulting spec and cross-repository references

## 1. Create reviewed repository inventory

### 1.1 Define inventory format

Create `openspec-store/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` with columns:

```text
canonical_root<TAB>default_branch<TAB>gitnexus_enabled<TAB>graphify_enabled
```

### 1.2 Populate inventory

- [ ] Include only explicitly approved repositories
- [ ] Use canonical absolute paths under `~/Developer/`
- [ ] Record each repository's actual default branch
- [ ] Exclude workspace root and non-repositories
- [ ] Deduplicate linked worktrees by Git common directory

### 1.3 Validate inventory

- [ ] Reject paths outside approved workspace roots
- [ ] Reject missing/non-Git paths
- [ ] Reject missing default branches
- [ ] Compute and log normalized inventory SHA-256
- [ ] Add a test fixture for path escape and unlisted repository

## 2. Implement central refresh script

Create `openspec-store/scripts/knowledge-refresh/refresh-knowledge-indexes.sh`.

### 2.1 Shell safety and environment

- [ ] Use Bash with `set -euo pipefail`
- [ ] Use absolute tool paths or explicit PATH
- [ ] Never print credentials or environment secrets
- [ ] Use canonical path resolution before operating
- [ ] Create bounded log directory

### 2.2 Inventory and target validation

- [ ] Load and validate the reviewed inventory
- [ ] Validate Git common directory and configured branch
- [ ] Exclude unlisted repositories
- [ ] Record inventory digest in each run

### 2.3 State guards

- [ ] Skip dirty repositories/worktrees with `skipped_dirty`
- [ ] Skip merge/rebase/cherry-pick state with `skipped_merge_state`
- [ ] Skip detached, ephemeral, and >30-day stale worktrees
- [ ] Skip uninitialized provider state with `skipped_uninitialized`

### 2.4 PID-aware locks

- [ ] Implement canonical-path-derived lock identifiers
- [ ] Acquire via atomic `mkdir`
- [ ] Record PID, owner, timestamp, and canonical target
- [ ] Reclaim only when owner PID is dead
- [ ] Never steal a live lock based on age
- [ ] Release locks using `trap`
- [ ] Add lock-busy, dead-owner, and cleanup tests

### 2.5 GitNexus refresh

- [ ] Verify GitNexus 1.6.9
- [ ] Run `gitnexus analyze . --index-only --default-branch <inventory-branch>`
- [ ] Apply five-minute per-target timeout
- [ ] Capture target HEAD before execution
- [ ] Verify indexed revision after execution
- [ ] Report `superseded` when HEAD changes during execution
- [ ] Never enable embeddings, PDG, `--force`, or package fallback

### 2.6 Graphify refresh

- [ ] Verify Graphify-Labs `graphifyy` 0.9.42
- [ ] Detect active `graphify watch` for the target root
- [ ] Report `watcher_active` and skip scheduled Graphify for watched roots
- [ ] Run routine `graphify update .`
- [ ] On missing/corrupt graph or update failure, run bounded `graphify extract . --code-only`
- [ ] Set `GRAPHIFY_VIZ_NODE_LIMIT=0` for foreground refresh
- [ ] Preserve last usable output on failure
- [ ] Verify `graphify-out/graph.json` parses after success

### 2.7 Worktree refresh

- [ ] Enumerate worktrees using `git worktree list --porcelain`
- [ ] Refresh only worktrees with existing `.gitnexus/` or `graphify-out/`
- [ ] Report missing state as `skipped_uninitialized`
- [ ] Keep worktree indexes independent from main checkout

### 2.8 Timeouts and logs

- [ ] Enforce five-minute per-target timeout
- [ ] Enforce two-hour overall timeout
- [ ] Log target, provider, status, duration, target revision, indexed revision
- [ ] Rotate logs to a bounded size
- [ ] Emit machine-readable event lines

## 3. Implement status command

Create `openspec-store/scripts/knowledge-refresh/knowledge-status.sh`.

### 3.1 Human output

- [ ] List every inventoried repository
- [ ] List all eligible worktrees
- [ ] Report GitNexus status: `FRESH`, `STALE`, `UNKNOWN`, `UNINITIALIZED`
- [ ] Report Graphify status: `FRESH`, `STALE`, `WATCHER`, `UNKNOWN`, `UNINITIALIZED`
- [ ] Report dirty file count and branch
- [ ] Report lock state and active owner

### 3.2 JSON output

- [ ] Implement `--json`
- [ ] Emit bounded valid JSON
- [ ] Include inventory digest and generation timestamp
- [ ] Include provider version and indexed/current revisions

## 4. Implement post-merge dispatcher and installer

Create `openspec-store/scripts/knowledge-refresh/install-hooks.sh`.

### 4.1 Managed block

- [ ] Add `knowledge-gitnexus-post-merge-start/end` markers
- [ ] Dispatcher only; no lock acquisition in hook
- [ ] Dispatch asynchronously to central refresh script
- [ ] Check configured default branch
- [ ] Preserve Graphify-owned hook blocks byte-for-byte

### 4.2 Installation

- [ ] Enumerate approved inventory only
- [ ] Resolve Git common directory
- [ ] Install once per common directory
- [ ] Back up hooks before mutation
- [ ] Make installation idempotent
- [ ] Validate hooks with `sh -n`
- [ ] Provide rollback using backups

### 4.3 Hook tests

- [ ] Local merge to default branch dispatches
- [ ] Non-default branch does not dispatch
- [ ] Dirty tree dispatch is safely skipped by central script
- [ ] Existing Graphify behavior remains unchanged
- [ ] Repeated installation produces no diff
- [ ] Linked worktrees do not duplicate the block

## 5. Implement and install LaunchAgent

### 5.1 Plist

Create `openspec-store/scripts/knowledge-refresh/com.developer.index-refresh.plist.template`:

- [ ] `StartCalendarInterval` at 02:30 local time
- [ ] No persistent keep-alive key for the batch job
- [ ] Absolute `/bin/bash` and script paths
- [ ] Explicit PATH containing `~/.npm-global/bin`, `~/.local/bin`, Homebrew, and system paths
- [ ] Explicit HOME and WorkingDirectory
- [ ] Separate stdout/stderr log paths

### 5.2 Lifecycle

- [ ] Install with `launchctl bootstrap gui/$(id -u)`
- [ ] Verify with `launchctl print gui/$(id -u)/com.developer.index-refresh`
- [ ] Trigger manually with `launchctl kickstart -k gui/$(id -u)/com.developer.index-refresh`
- [ ] Capture launchd stdout/stderr
- [ ] Do not claim durable `graphify watch` lifecycle in this change

## 6. Documentation and specification alignment

### 6.1 AGENTS.md

- [ ] Remove nonexistent weekly cron claim
- [ ] Document actual LaunchAgent, inventory, status command, and local-hook scope
- [ ] Document Graphify-Labs/graphify identity and version

### 6.2 `.claude/CLAUDE.md`

- [ ] Replace stale GitNexus warning with automated refresh guidance
- [ ] Replace stale Graphify warning with `graphify update .` guidance
- [ ] Document dirty-tree and watcher limitations
- [ ] Remove nonexistent weekly cron claim

### 6.3 OpenSpec main specs

- [ ] Correct `developer-code-intelligence` Graphify provider identity
- [ ] Add scheduled-refresh authorization scenario to `gitnexus-stable-contract`
- [ ] Keep `workspace-index-freshness` as a separate new capability
- [ ] Do not modify `refresh-gitnexus-index-groups` unless an independent relationship requires it

## 7. Verification gates

### 7.1 Static gates

- [ ] `bash -n` all shell scripts
- [ ] `plutil -lint` LaunchAgent
- [ ] `openspec validate ecosystem-index-freshness-automation --strict`
- [ ] Full stale-reference sweep across proposal, design, spec, tasks, main specs, docs, and scripts
- [ ] Verify no alternate Graphify provider, legacy pin, age-only lock stealing, or wrong CLAUDE path remains

### 7.2 Functional gates

- [ ] Refresh script runs against a disposable clean repo
- [ ] GitNexus refresh uses exact pinned command
- [ ] Graphify update succeeds on a clean fixture
- [ ] Graphify extract repair succeeds on a clean fixture
- [ ] Dirty repository is skipped
- [ ] Merge-state repository is skipped
- [ ] Live lock causes clean skip
- [ ] Dead lock is reclaimed
- [ ] Watcher-active Graphify target is skipped
- [ ] Hook installer is idempotent
- [ ] Hook syntax passes for all approved repositories
- [ ] Status table and JSON parse correctly
- [ ] LaunchAgent loads, prints, and kickstarts successfully

### 7.3 Evidence

- [ ] Save redacted version/digest evidence
- [ ] Save inventory digest
- [ ] Save hook installation manifest
- [ ] Save functional test results
- [ ] Save final status JSON
- [ ] Record known limitation: `post-merge` covers local merge/merge-pull only, not remote PR merge or `git pull --rebase`
