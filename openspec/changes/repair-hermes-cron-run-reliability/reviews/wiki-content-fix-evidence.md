# Wiki Content Fix Evidence

**Date:** 2026-08-25
**Wiki commit:** `f9262547c100fa74239c988e2334acfb134ba4c9`
**Worktree:** `~/Developer/wiki-review-hermes-cron` (branch `review-hermes-cron-wiki-fixes`)

## What was done

### Task 3.1: Added `status: active` to 17 pages
Pages: architecture/agent-core-llm-loading-and-cli-verification, comparisons/knowledge-tools, concepts/go-platform-architecture, concepts/knowledge-graph-system, concepts/mcp-transport-layer, concepts/openspec-change-lifecycle, concepts/python-agent-ecosystem, entities/agent-core, entities/agentmemory, entities/gitnexus, entities/go-microservices, entities/graphify, entities/jira-skill, entities/mcp-router, entities/ollama-embedding-server, entities/tdt-core, references/agent-ecosystem-evaluation-2026-08.

### Task 3.2: Reference page date semantics
- Added `created: 2026-08-23` (Git creation date)
- Preserved `date: 2026-08-20` (semantic document date)

### Task 3.3: Fixed 16 broken relative links
- `comparisons/knowledge-tools.md`: 7 occurrences (4 patterns: `../entities/graphify.md`, `../entities/gitnexus.md`, `../entities/agentmemory.md`, `../concepts/knowledge-graph-system.md`)
- `concepts/mcp-transport-layer.md`: 5 occurrences (4 patterns: `../entities/mcp-router.md`, `../entities/gitnexus.md`, `../entities/agentmemory.md`, `../entities/graphify.md`)
- `entities/mcp-router.md`: 4 occurrences (4 patterns: `../concepts/mcp-transport-layer.md`, `gitnexus.md`, `agentmemory.md`, `graphify.md`)

### Task 3.4: Updated SCHEMA.md template
- Added `status: active|draft|archived` to frontmatter template
- Added `date: (optional, semantic document date)` to frontmatter template
- Added conventions note: "Every page must have `title`, `tags`, `created`, `updated`, and `status`"
- Updated `updated` to 2026-08-24 (template contract changed)

### Task 3.5: Committed and integrated
- Committed on branch `review-hermes-cron-wiki-fixes` at `f926254`
- Cherry-picked into wiki `main` via fast-forward merge
- No conflicts

## Post-integration deterministic audit

| Metric | Result |
|---|---|
| Files scanned | 24 |
| Total relative links | 37 |
| Valid links | 37 |
| Broken links | 0 |
| Errors | 0 |

## What remains blocked

- Task 3.6 (`wiki/scripts/wiki-lint.py` deterministic validator): BLOCKED on ownership acceptance
- Task 3.7 (lint acceptance test): BLOCKED on task 3.6

## Updated dates

Content pages: `updated` dates preserved as-is (no substantive content change, only frontmatter/link corrections). SCHEMA.md `updated` bumped to 2026-08-24 because the template contract changed.
