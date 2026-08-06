# Design: Knowledge Tools Integration in OpenSpec Workflow

## Architecture

The integration adds a **Knowledge Context Layer** to each phase of the OpenSpec lifecycle. Each phase gets optional knowledge-tool steps that enrich the existing workflow without replacing it.

```
Phase 1: Create          Phase 2: Design & Review       Phase 3: Apply
┌─────────────────┐      ┌──────────────────────┐       ┌─────────────────┐
│ 1a. Grep search │      │ 2a. 5-provider review │       │ (existing impl) │
│ 1b. graphify    │ NEW  │ 2b. Knowledge evidence│ NEW   │ 3b. graphify    │ NEW
│ 1c. gitnexus    │ NEW  │     added to context  │       │     update per  │
│ 1d. wiki search │ NEW  │                       │       │     commit      │
│ 1e. memory      │ NEW  │                       │       │                 │
│     recall      │      │                       │       │                 │
└─────────────────┘      └──────────────────────┘       └─────────────────┘

Phase 4: Validate        Phase 5: Archive
┌─────────────────┐      ┌──────────────────────┐
│ 4a. openspec    │      │ 5a. archive (existing)│
│     validate    │      │ 5b. wiki update       │ NEW
│ 4b. knowledge   │ NEW  │ 5c. gitnexus re-index │ NEW
│     freshness   │      │ 5d. graphify update   │ NEW
│     check       │      │                       │
└─────────────────┘      └──────────────────────┘
```

## Design Decisions

### Decision 1: Knowledge gathering is OPTIONAL per phase, not mandatory

**Rationale:** Not every change benefits from all four tools. A config-only change (`skip_specs: true`) doesn't need graphify analysis. A documentation-only change doesn't need gitnexus impact analysis.

**Implementation:** Each knowledge step has a "when to use" gate:
- graphify steps → when the change touches code (not `skip_specs: true`)
- gitnexus steps → when the change affects symbols with callers
- wiki steps → when the change affects documented services/concepts
- agentmemory steps → always available (past context is always useful)

### Decision 2: Knowledge outputs are EVIDENCE, not gatekeepers

**Rationale:** Knowledge tools provide context and evidence for human/agent judgment. They should not block the workflow (unlike validation failures).

**Implementation:** Knowledge outputs are collected into the context bundle for reviewers. They appear in review reports as additional evidence lanes. They do NOT cause automatic FAIL statuses — they inform PASS/PARTIAL/UNKNOWN decisions.

### Decision 3: Post-archive updates are BEST EFFORT, not blocking

**Rationale:** Wiki updates and graph rebuilds are maintenance tasks. Forcing them before archive completion would slow down the workflow for changes that don't affect documented knowledge.

**Implementation:** Post-archive knowledge updates are recommended in the workflow but not enforced. The weekly crons (graphify Mon 8AM, wiki Mon 9AM) provide a safety net for missed updates.

### Decision 4: Tool routing follows the existing workspace-knowledge-tools patterns

**Rationale:** The `workspace-knowledge-tools` skill already defines the cross-tool query patterns. OpenSpec should use these same patterns, not invent new ones.

**Implementation:** Reference the existing patterns:
- Structural questions → `graphify query` (free, fast)
- Semantic/deeper questions → `gitnexus context`/`impact` (indexed, MCP)
- Past session context → `agentmemory memory_smart_search` (episodic)
- Curated knowledge → `wiki_search` (compiled)

## Integration Points

### Phase 1: Create — Knowledge Context Gathering

After the existing "Broader cross-repo search" step, add:

```
1f. Knowledge context gathering:
    For each repo in scope, collect:
    - graphify query "<change-topic>" — structural nodes + communities
    - gitnexus impact "<affected-symbol>" — blast radius + risk level
    - wiki_search "<service-name>" — existing documentation
    - memory_smart_search "<change-description>" — past session patterns
    
    Save results to: openspec/changes/<name>/knowledge-context.md
```

### Phase 2: Design & Review — Knowledge Evidence

Extend the 5-provider review context bundle with:
- graphify structural analysis (god-nodes, community membership)
- gitnexus impact analysis (risk level, affected count)
- wiki pages for affected services
- agentmemory patterns (prior similar changes, lessons learned)

Add a 9th edge to the alignment matrix:
- **Knowledge ↔ Code** — Does the existing knowledge (wiki, graph, memory) match the proposed changes?

### Phase 3: Apply — Per-Commit Graph Updates

After each vertical slice commit in a multi-commit change:
- `graphify update .` on affected repos (keeps graphs current incrementally)

### Phase 4: Validate — Knowledge Freshness

Before final validation:
- `graphify check-update .` — verify no pending re-extraction
- `wiki_stale` — verify wiki pages aren't outdated
- MCP `list_repos` with staleness check — verify gitnexus indexes are current

### Phase 5: Archive — Knowledge Capture

After archiving:
1. For each affected repo:
   - `graphify update .` (if code changed)
   - Re-index with `gitnexus analyze` (if symbols changed)
2. For each affected service/entity in wiki:
   - `wiki_search` to find related pages
   - `wiki_ingest` to update if stale
3. Significant architecture decisions → create/update wiki concept pages

## Edge Definition Update

Add to the 8-edge alignment matrix:

| Edge | What to Check |
|------|---------------|
| **Knowledge ↔ Code** | Do existing knowledge tools (wiki, graph, memory) accurately reflect the current codebase state? Are wiki pages stale? Is the graph current? |

This brings the matrix to **9 edges**.

## Trade-offs

| Trade-off | Chosen | Alternative | Why |
|-----------|--------|-------------|-----|
| Optional vs mandatory knowledge steps | Optional per phase | Mandatory for all | Config-only changes don't need graphify |
| Evidence vs gatekeeper | Evidence only | Block on failures | Knowledge tools can be stale; shouldn't block valid changes |
| Per-commit vs post-apply graph update | Per-commit (during apply) | Single post-apply update | Incremental updates are faster and catch issues earlier |
| Best-effort vs enforced post-archive | Best-effort with cron safety net | Enforced before archive | Slows workflow; crons catch misses |
