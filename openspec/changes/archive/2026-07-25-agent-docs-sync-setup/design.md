## Context

agent-docs-sync is a Python3.14 agent (25 source files, 4 sub-packages: agents, llm, tools, workflows) that automates documentation synchronization across TDT repos. It depends on agent-core for BaseAgent, ToolRegistry, and WorkflowBuilder. It uses an LLM gateway (OmniRoute/LiteLLM) for doc generation.

Current state:
- 2 git commits, no remotes, 13 uncommitted files
- No `.gitnexus/` or `graphify-out/` directories
- No CLAUDE.md or AGENTS.md
- 17 other repos in the workspace already have gitnexus;13 have graphify

The repo's pipeline is: `detect_changes → analyze_impact → generate_updates → validate → report`, with agent-core integration via `build_sync_pipeline(use_agent=True)` and durable execution via SchedulerEngine.

## Goals / Non-Goals

**Goals:**
- Index agent-docs-sync with gitnexus so symbol-level impact analysis is available
- Generate a graphify graph so architecture-level exploration is possible
- Add CLAUDE.md and AGENTS.md to bring the repo to workspace standards
- Commit all 13 pending files to establish a clean baseline
- Use the tools to analyze agent-docs-sync's own architecture (self-documentation)

**Non-Goals:**
- Implementing any new agent-docs-sync features (that's a separate change)
- Changing the agent-docs-sync spec requirements
- Setting up CI/CD for agent-docs-sync
- Adding a git remote (user decision, not in scope)
- Modifying agent-core, tdt-core, or any other repo

## Decisions

### D1: Index order — gitnexus first, then graphify

**Decision**: Run `npx gitnexus analyze` before `graphify update .`

**Rationale**: GitNexus produces a symbol database (lbug/SQLite) that graphify can optionally reference. Running gitnexus first ensures the graph has accurate symbol data. This matches the pattern in all other repos (both tools exist, gitnexus is the deeper analysis).

**Alternative considered**: Run graphify alone — rejected because graphify produces a shallower graph without symbol-level data.

### D2: CLAUDE.md scope — project-focused, not duplicated from workspace

**Decision**: Write a project-specific CLAUDE.md that references agent-docs-sync's actual structure, not a copy of the workspace CLAUDE.md.

**Rationale**: The workspace CLAUDE.md covers all repos. agent-docs-sync needs its own focused instructions covering: CLI usage, pipeline architecture, tool list, LLM config, and dev workflow. Reference tdt-meta CLAUDE.md for workspace-wide conventions.

### D3: AGENTS.md — reference existing agent patterns

**Decision**: AGENTS.md should document agent-docs-sync's agent patterns (BaseAgent, flavors, tool registration) and reference the workspace AGENTS.md for orchestration.

**Rationale**: agent-docs-sync has specific agent patterns (generation agent, doc sync agent, flavors) that need local documentation. Cross-repo orchestration is already in workspace AGENTS.md.

### D4: Commit strategy — single commit for all 13 files

**Decision**: Commit all 13 modified files in one commit with a conventional commit message.

**Rationale**: These are all part of the same "initial implementation" batch. Splitting them adds complexity without benefit. The commit message should explain this is the baseline for the repo.

### D5: No OpenSpec change for the indexing itself

**Decision**: The gitnexus/graphify setup is a tooling operation, not a code change. No OpenSpec change is needed for the indexing step — it's a one-time setup command.

**Rationale**: OpenSpec tracks feature changes. Tooling setup is infrastructure, not feature work.

### D6: Post-commit hook — use graphify's built-in hook system

**Decision**: Use `graphify hook install` for graphify refresh, then append gitnexus refresh to the same post-commit hook via markers.

**Rationale**:
- Graphify CLI v0.7.15 (PyPI latest: 0.9.25) has a built-in `hook install` command that handles post-commit + post-checkout
- The built-in hook uses `_rebuild_code()` for **incremental** AST-only rebuilds (not full `graphify update`)
- It uses `nohup` + `disown` for truly non-blocking background execution
- It handles rebase/merge/cherry-pick skip logic
- It has marker-based idempotent install/uninstall
- GitNexus has no built-in hook — append via `# gitnexus-hook-start` / `# gitnexus-hook-end` markers
- **Existing precedent**: poems-mobile3-ios already has graphify hooks installed (only repo in workspace)

**Why this over custom hook**:
- Built-in hook is battle-tested across multiple platforms (Claude, Codex, Gemini, etc.)
- Incremental rebuild is faster than full `graphify update`
- Post-checkout hook is a bonus (rebuilds graph on branch switch)
- No need to write/maintain custom shell script

**Alternatives considered**:
- Custom post-commit script — rejected: reinventing what graphify already provides
- `git watch` / fswatch watcher — rejected: heavier, requires a daemon, overkill
- Pre-commit hook — rejected: indexes would reflect uncommitted state

### D7: Graphify Python version — use system Python fallback

**Decision**: The graphify hook's Python detection chain handles this automatically. No special configuration needed.

**Rationale**:
- graphifyy package requires Python >=3.10, <3.14 (per PyPI metadata)
- agent-docs-sync uses Python 3.14 in its venv
- The hook's `_PYTHON_DETECT` snippet tries: graphify bin shebang → python3 → python
- If graphify is installed globally (not in the venv), system Python works
- If graphify is not available at all, the hook skips gracefully (exit 0)
- **Verified**: poems-mobile3-ios has working graphify hooks — the detection chain works in practice

**Risk**: If graphify is only installed in a Python 3.14 venv, the hook will fail to import and skip. Mitigation: ensure graphify is installed globally or in a compatible venv.

## Risks / Trade-offs

- **[Risk] Graphify Python <3.14 requirement** → Mitigation: Hook's `_PYTHON_DETECT` falls back to system Python. poems-mobile3-ios has working hooks as proof. If graphify is not available, hook skips gracefully.
- **[Risk] GitNexus full reindex on every commit** → Mitigation: No incremental mode exists. For 25-file repo, full reindex is fast (<30s). Acceptable trade-off.
- **[Risk] Graphify skill file stale (0.6.7 vs CLI 0.7.15)** → Mitigation: Run `graphify install` to refresh skill file. Hook behavior is identical across versions.
- **[Risk] GitNexus SKILL.md version stale (1.6.7 vs installed 1.6.9)** → Mitigation: Minor version gap. No behavioral changes affect this use case.
- **[Risk] Uncommitted files may have issues** → Mitigation: Run ruff check + mypy before committing. The 13 files were already working.
- **[Risk] GitNexus section may conflict with future graphify hook updates** → Mitigation: Marker-based append. `graphify hook install` is idempotent and won't remove markers.
- **[Trade-off] Single commit vs. granular** → Chose single commit for simplicity. If any file needs rollback, git revert can target the commit.
- **[Trade-off] Background vs. sequential hook** → Chose background for non-blocking UX. Index may be 1-2 commits behind temporarily.

## Migration Plan

1. Verify graphify CLI is available: `graphify --version` (expect 0.7.15+)
2. Refresh skill file if stale: `graphify install` (updates skill to match CLI version)
3. Run `ruff check . --fix && ruff format .` to ensure code quality
4. Run `npx gitnexus analyze` from agent-docs-sync root
5. Run `graphify update .` from agent-docs-sync root
6. Run `graphify hook install` from agent-docs-sync root (installs post-commit + post-checkout)
7. Append gitnexus refresh section to `.git/hooks/post-commit` between markers
8. Write CLAUDE.md with project-specific instructions
9. Write AGENTS.md with agent pattern documentation
10. Update .gitignore for gitnexus/graphify artifacts
11. Run `git add -A && git commit` with conventional message
12. Verify: `graphify hook status` shows installed, post-commit hook fires on next commit

Rollback: `rm -rf .gitnexus/ graphify-out/` + `graphify hook uninstall` + `git revert HEAD` if needed.

## Open Questions

- Should agent-docs-sync get a git remote? (User decision, not in this change — deferred)
- ~~Should the graphify graph be included in .gitignore or committed?~~ **Resolved**: Both `graphify-out/` and `.gitnexus/` will be gitignored. Rationale: auto-generated, regenerable via post-commit hook, consistent with jira-skill and agent-core patterns.
