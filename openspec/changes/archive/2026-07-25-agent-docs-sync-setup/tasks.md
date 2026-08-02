## 0. Prerequisites

- [x] 0.1 Verify graphify CLI available: `graphify --version` (expect 0.7.15+)
- [x] 0.2 Verify gitnexus CLI available: `npx gitnexus --version` (expect 1.6.9+)
- [x] 0.3 Refresh graphify skill if stale: `graphify install` (updates skill to match CLI)

## 1. Code Quality Baseline

- [x] 1.1 Run `ruff check . --fix && ruff format .` from agent-docs-sync root to fix any lint issues
- [x] 1.2 Run `mypy src/ --strict` and document any known type issues
- [x] 1.3 Verify all 13 modified files are ready for commit (no secrets, no debug prints)

## 2. GitNexus Indexing

- [x] 2.1 Run `npx gitnexus analyze` from agent-docs-sync root
- [x] 2.2 Verify `.gitnexus/` directory created with gitnexus.json, meta.json, lbug, run.cjs
- [x] 2.3 Run `npx gitnexus status` to confirm index is current
- [x] 2.4 Run `npx gitnexus query "doc generation" -r agent-docs-sync` to verify queryability
- [x] 2.5 Run `npx gitnexus impact "CheckLinksTool" -d upstream -r agent-docs-sync` to verify impact analysis

## 3. Graphify Graph Generation

- [x] 3.1 Run `graphify update .` from agent-docs-sync root
- [x] 3.2 Verify `graphify-out/graph.json` and `graphify-out/manifest.json` exist
- [x] 3.3 Run `graphify query "sync pipeline"` to verify pipeline flow is visible
- [x] 3.4 Run `graphify path "cli.py" "sync_pipeline.py"` to verify path finding
- [x] 3.5 Run `graphify explain "CheckLinksTool"` to verify node explanation

## 4. Post-Commit Hook

- [x] 4.1 Run `graphify hook install` from agent-docs-sync root (installs post-commit + post-checkout)
- [x] 4.2 Append gitnexus refresh section to `.git/hooks/post-commit` between `# gitnexus-hook-start` / `# gitnexus-hook-end` markers
- [x] 4.3 Gitnexus section runs `npx gitnexus analyze` in background (non-blocking, skip if not found)
- [x] 4.4 Verify `graphify hook status` reports both hooks as "installed"
- [x] 4.5 Test: make a small commit and verify graphify rebuild fires automatically
- [x] 4.6 Test: verify commit prompt returns immediately (hook is non-blocking)
- [x] 4.7 Test: verify post-checkout hook fires on branch switch

## 5. Project Scaffolding

- [x] 5.1 Write CLAUDE.md with project-specific instructions (CLI, pipeline, LLM config, dev workflow)
- [x] 5.2 Write AGENTS.md documenting agent patterns (doc_sync_agent, generation_agent, flavors, tools)
- [x] 5.3 Update .gitignore with gitnexus artifact patterns (lbug, parse-cache/, parsedfile-cache/, run.cjs, gitnexus.json, meta.json)
- [x] 5.4 Update .gitignore with graphify-out/ pattern (graphify-out/, graphify-out/cache/)

## 6. Commit and Verify

- [x] 6.1 Run `git add -A` and verify staged files look correct
- [x] 6.2 Commit with message: `feat: initial agent-docs-sync setup with gitnexus, graphify, and post-commit hook`
- [x] 6.3 Verify `git status` shows clean working tree
- [x] 6.4 Verify `npx gitnexus status` shows indexed
- [x] 6.5 Verify `graphify-out/graph.json` is present and non-empty
- [x] 6.6 Verify post-commit hook is executable: `ls -la .git/hooks/post-commit`
