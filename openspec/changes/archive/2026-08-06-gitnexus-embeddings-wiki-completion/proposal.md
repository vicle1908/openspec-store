# gitnexus-embeddings-wiki-completion

## Why

The archived `workspace-knowledge-integration` change established the foundation:
graphify graphs for all repos, global cross-repo graph, LLM Wiki skeleton, wiki MCP
server. But three critical gaps remained:

1. **GitNexus only indexed 10/18 repos** — 8 Python repos (agent-docs-sync, agent-harness,
   ai-review, browser-cli, jira-epic-report, jira-skill, ops-automation-suite, tdt-sheets)
   had no semantic code intelligence. Agents couldn't run `impact`, `context`, or
   `detect_changes` on these repos.

2. **No local embeddings** — GitNexus relied on struct matching only. Semantic search
   (`query`) returned process-flow results but couldn't match by meaning. With Ofable-5
   available (nomic-embed-text, 768-dim), local embeddings enable vector-based semantic
   search across all indexed code.

3. **No wiki generation** — GitNexus wiki feature (auto-generated code documentation from
   the knowledge graph) was never exercised. Tested successfully with Ofable-5 qwen2.5:0.5b
   on browser-cli.

4. **Graphify global graph was stale** — The archived change built it, but repos had
   evolved. Rebuilt to 48,124 nodes / 98,654 links across all 18 repos.

## What Changes

### Phase 1: Complete GitNexus indexing (8 missing repos)

Index all 8 missing Python repos with `gitnexus analyze --skip-agents-md --skip-skills
--index-only`. Fix jira-skill WAL corruption with clean+rebuild.

**Result:** 18/18 repos indexed. Total: ~85,000+ symbols across the workspace.

### Phase 2: Update stale indexes (10 repos)

Re-index 10 repos that had fallen behind HEAD (1-36 commits). All brought to current
commit.

### Phase 3: Ofable-5 local embeddings

- Pull `nomic-embed-text` (768-dim, 274MB) and `fable-5.5:0.5b` (397MB) via Ofable-5
- Create `.gitnexusrc` for all 18 repos with embedding config:
  ```json
  {
    "defaultBranch": "main",
    "embeddings": true,
    "dropEmbeddings": true,
    "embeddingBaseUrl": "http://localhost:11434/v1",
    "embeddingModel": "nomic-embed-text",
    "embeddingThreads": 4,
    "embeddingBatchSize": 16,
    "workers": 4
  }
  ```
- Re-index repos with `--embeddings --drop-embeddings` and `GITNEXUS_EMBEDDING_DIMS=768`
- 11 repos confirmed with embeddings (22,773 total embeddings)
- 7 repos still need embedding re-indexing (background job incomplete)

### Phase 4: Wiki generation

- Configure `~/.gitnexus/config.json` with Ofable-5 custom provider
- Test wiki generation on browser-cli: `gitnexus wiki --provider custom --model fable-52.5:0.5b
  --base-url http://localhost:11434/v1`
- Output: `.gitnexus/wiki/` with `overview.md`, module pages, `index.html`
- Generation time: ~220s for small repo (22 files)

### Phase 5: Graphify global graph rebuild

- Re-run `graphify global add` for all 18 repos
- Updated `~/.graphify/global-graph.json`: 48,124 nodes, 98,654 links (66MB)
