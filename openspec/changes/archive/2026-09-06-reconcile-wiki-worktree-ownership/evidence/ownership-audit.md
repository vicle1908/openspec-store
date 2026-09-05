# Ownership Audit: `wiki-cron-validator`

## 1. Executive Summary

- **Target Path**: `/Users/androidteam/Developer/wiki-cron-validator`
- **Canonical Repository**: `/Users/androidteam/Developer/wiki`
- **Classification**: `RECLAIMABLE` (clean detached worktree, 0 unique commits ahead of main, 0 uncommitted changes, 0 active locks/references)
- **Current State**: **PRESERVED** (no deletion or retirement executed; this is a read-only audit)
- **Governing Change**: `reconcile-wiki-worktree-ownership`

---

## 2. Git Worktree Inventory

### Command: `git -C ~/Developer/wiki worktree list`

```
/Users/androidteam/Developer/wiki                3b610d5 [main]
/Users/androidteam/Developer/wiki-cron-validator 3b610d5 (detached HEAD)
```

### Git Directory Layout
- **Canonical `.git` path**: `/Users/androidteam/Developer/wiki/.git` (directory, main repo)
- **Worktree `.git` pointer**: `/Users/androidteam/Developer/wiki-cron-validator/.git` (77-byte pointer file)
- **Common git directory**: `/Users/androidteam/Developer/wiki/.git` (verified via `git rev-parse --git-common-dir`)
- **Status in `wiki-cron-validator`**: `Not currently on any branch. nothing to commit, working tree clean`
- **Stashes**: 0 (`git stash list` empty)

---

## 3. Commit History

### wiki-cron-validator HEAD
```
3b610d5 docs(wiki): update knowledge concepts, entities, and refresh references
```

### Recent commits (wiki-cron-validator):
```
3b610d5 docs(wiki): update knowledge concepts, entities, and refresh references
3d439c2 feat(wiki-lint): extend to 6-check feature parity with old cron contract
fe96ce9 feat: add deterministic wiki integrity validator
f926254 fix: repair wiki frontmatter and relative link integrity
0ef5e98 Update wiki: mcp-router 13 servers/142 tools, fix stale pages, add body links
1fffb69 docs: align OpenSpec lifecycle validation gates
95a9dac docs: fix wiki version precision for pydantic-ai
030f07c docs: update agent-core entity page for harness 0.23.0 capabilities
f3672c6 fix(wiki): add 4 missing pages to index.md
d8c9a91 Modernize agent-core LLM loading article
```

### Branches in wiki-cron-validator:
```
* (no branch)
+ main
  review-hermes-cron-wiki-fixes
```

---

## 4. Orca Orchestration Database Audit

- **Database Path**: `~/Library/Application Support/orca/orchestration.db`
- **Query**: `SELECT worktree_id FROM worker_terminal_resources WHERE worktree_id LIKE '%wiki-cron-validator%';`
- **Finding**: **0 matches**. No active or historical Orca tasks bound to this worktree path.

---

## 5. OpenSpec Registry Audit

- **Active Changes** (`openspec list --json`): Only this governing change (`reconcile-wiki-worktree-ownership`) contains "wiki" in its name. No other active changes reference `wiki-cron-validator` as a workspace or edit root.
- **Archived References**:
  - `2026-08-25-repair-hermes-cron-run-reliability`: Referenced `implement-wiki-cron-validator` branch; fast-forwarded to `wiki/main` at `3d439c2`.
  - `2026-09-05-root-cleanup-residual`: Recorded `wiki-cron-validator` as non-goal pending owner review.
  - `2026-09-05-workspace-lifecycle-dryrun-2026-09`: Recorded `wiki-cron-validator` under `REVIEW_REQUIRED`.
  - `2026-09-05-reconcile-wiki-worktree-ownership` (prior archived): Classified as `RECLAIMABLE`.

---

## 6. System & Runtime Reference Checks

| Check | Command | Result |
|-------|---------|--------|
| Open file handles | `lsof +D /Users/androidteam/Developer/wiki-cron-validator` | None |
| LaunchAgents | `launchctl list \| grep -i wiki` | None |
| Crontab | `crontab -l \| grep -i wiki` | None |
| Ecosystem scanner | `workspace-worktree-scan.sh \| grep -i wiki` | Correctly identifies as LINKED |

### Scanner Output:
```
/Users/androidteam/Developer/wiki worktrees=2 extra=1 dirty_paths=0 trash_nonempty=0 prunable=0
/Users/androidteam/Developer/wiki-cron-validator LINKED (status checked; counts owned by /Users/androidteam/Developer/wiki) dirty_paths=0 trash_nonempty=0
/Users/androidteam/Developer/wiki-mcp-server worktrees=1 extra=0 dirty_paths=0 trash_nonempty=0 prunable=0
```

---

## 7. Tree Verification & Comparison

- **Revision HEAD (wiki-cron-validator)**: `3b610d5d27d366b34b74a189bde861edbc41cfe5`
- **Revision HEAD (wiki)**: `3b610d5d27d366b34b74a189bde861edbc41cfe5`
- **Tree diff** (`diff <(git ls-tree -r HEAD) <(git ls-tree -r main)`): **Exit code 0, 0 differences**. All tracked blobs, modes, and paths match identically.

---

## 8. Classification

- **Classification**: `RECLAIMABLE`
- **Justification**:
  1. **Canonical source exists**: `/Users/androidteam/Developer/wiki` at `main` branch contains identical commit `3b610d5`.
  2. **No data loss risk**: 0 uncommitted changes, 0 untracked files, 0 stashes.
  3. **No active consumers**: 0 Orca runs, 0 active OpenSpec tasks, 0 open file handles, 0 launchctl jobs, 0 crontab entries.
  4. **Scanner aware**: Ecosystem scanner correctly identifies as linked worktree.
  5. **Historical reference**: Was created for wiki-lint/cron-validator work that has been completed and merged.

---

## 9. Additional: wiki-mcp-server Note

The scanner also detected `/Users/androidteam/Developer/wiki-mcp-server` as a separate worktree with 1 worktree, 0 extra. It is on `main` branch at commit `93b5dd1 chore: initialize repo with gitignore`. This is a distinct entity and outside the scope of this audit.
