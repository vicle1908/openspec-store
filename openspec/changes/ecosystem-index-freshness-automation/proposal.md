# Proposal: Ecosystem Index Freshness Automation

## Why

GitNexus and Graphify knowledge-graph indexes across the workspace go stale because no automated workspace refresh exists. Graphify post-commit hooks are installed in all 18 repositories via `graphify hook install`, but they only rebuild the AST on code changes — they do not refresh GitNexus. There is no nightly scheduled refresh, no reviewed repository inventory, and no status command. Documentation in `AGENTS.md` and `.claude/CLAUDE.md` claims weekly crons that do not exist.

## Additional Problems

1. **Post-local-merge lag**: After a developer runs `git merge` or `git pull` locally, agents get stale GitNexus results. The existing workspace post-merge hooks handle Graphify refresh; GitNexus has no equivalent trigger.

2. **Worktree blindness**: The workspace uses git worktrees extensively. Most worktrees lack `.gitnexus/` or `graphify-out/` state. Agents working in worktrees get no index refresh.

3. **Dirty-tree indexing risk**: Both CLIs operate on filesystem contents, not committed HEAD. Scheduled refresh with dirty working trees may index local edits rather than committed state.

4. **No reviewed inventory**: There is no tracked list of which repositories should be refreshed, what their default branch is, or what their lock identity is. Dynamic discovery cannot satisfy the exact-repository-set requirement in `gitnexus-stable-contract`.

## Official Tool Identity

| Tool | Source | Package | CLI | Current Version | License |
|---|---|---|---|---|---|
| Graphify | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | `graphifyy` (PyPI) | `graphify` | 0.9.42 | Apache-2.0 |
| GitNexus | [gitnexus](https://www.npmjs.com/package/gitnexus) | `gitnexus` (npm) | `gitnexus` | 1.6.9 | PolyForm NC |

## Non-Goals

- Changing GitNexus or Graphify CLI internals
- Embeddings or PDG refresh (expensive, should remain on-demand)
- Touching AgentMemory (already fully automated via LaunchAgent)
- Graphify version upgrade (completed as prerequisite for this change)

## Affected Ownership Boundaries

- **openspec-store**: New tracked scripts, inventory, templates, and delta specs
- **Workspace root** (`~/Developer/`): Installed scripts, LaunchAgent, symlinks
- **go-microservices**: Existing `knowledge-tools.sh` legacy pin updated to 0.9.42
- **AGENTS.md** (`~/Developer/AGENTS.md`): Fix stale cron claims (line 360)
- **CLAUDE.md** (`~/Developer/.claude/CLAUDE.md`): Update staleness warnings (lines 63, 66, 122)

## What Changes

### Part 1: Reviewed repository inventory

A tracked, versioned inventory file under `openspec-store/scripts/knowledge-refresh/` lists every repository eligible for automated refresh, with canonical paths, default branches, and tool toggles. This replaces dynamic discovery as the authorization mechanism.

### Part 2: Central refresh script

A single entry-point script reads the inventory, validates entries, checks dirty/merge state, coordinates locks, runs official refresh commands, and verifies post-run revision equality.

### Part 3: Non-blocking post-merge dispatcher

A workspace-managed post-merge hook block dispatches asynchronously to the central script. The hook itself never acquires a lock.

### Part 4: Nightly LaunchAgent

Modeled after AgentMemory's proven pattern. `StartCalendarInterval` at 02:30. No persistent keep-alive key. Absolute paths. `launchctl bootstrap` / `kickstart`.

### Part 5: Status command

Reports per-repo freshness, dirty-tree status, worktree state, and lock state. Human-readable table and `--json` output.

### Part 6: Idempotent hook installer

A tracked script installs the workspace-managed GitNexus block into each repository's hooks. Preserves Graphify-owned marker blocks byte-for-byte. Deduplicates by Git common directory.

### Part 7: Documentation accuracy

Fix stale claims in `~/Developer/AGENTS.md` (line 360) and `~/Developer/.claude/CLAUDE.md` (lines 63, 66, 122).
