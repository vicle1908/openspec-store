# gitnexus-embeddings-wiki-completion — Design

## Architecture

```
Ofable-5 (localhost:11434)
  ├── nomic-embed-text (768-dim) → GitNexus embedding pipeline
  └── fable-52.5:0.5b (chat) → GitNexus wiki generation

GitNexus 1.6.9
  ├── 18 repos indexed (all workspace repos)
  ├── .gitnexusrc per repo (embedding config, default branch)
  ├── Local ONNX embeddings disabled (using Ofable-5 remote)
  └── Wiki output: .gitnexus/wiki/ per repo

mcp-router (localhost:3282)
  ├── gitnexus MCP (9 tools) → semantic search, impact, context
  ├── agentmemory MCP (7 tools) → episodic memory
  └── wiki MCP (6 tools) → curated knowledge base

Graphify 0.9.34
  ├── Per-repo graphify-out/graph.json (18 repos)
  └── Global graph: ~/.graphify/global-graph.json (48K nodes)
```

## Embedding Pipeline

### Dimension Migration

Previous indexes used ONNX default (384-dim). Ofable-5 nomic-embed-text produces 768-dim.
Required fix: `GITNEXUS_EMBEDDING_DIMS=768` env var + `--drop-embeddings` flag.

Without this, GitNexus throws: "Embedding dimension mismatch: endpoint returned 768d
vector, but expected 384d."

### .gitnexusrc Format

Flat JSON at repo root. Key fields:
- `defaultBranch`: "main" (all repos)
- `embeddings`: true (enable embedding pipeline)
- `dropEmbeddings`: true (clear old 384-dim vectors before rebuild)
- `embeddingBaseUrl`: "http://localhost:11434/v1" (Ofable-5 OpenAI-compatible endpoint)
- `embeddingModel`: "nomic-embed-text"
- `embeddingThreads`: 4 (CPU threads for batch processing)
- `embeddingBatchSize`: 16 (nodes per batch)
- `workers`: 4 (parallel parse workers)

### Embedding Coverage

| Repo | Embeddings | Status |
|------|-----------|--------|
| agent-core | 3,319 | ✅ |
| agent-harness | 1,889 | ✅ |
| ai-review | 1,099 | ✅ |
| browser-cli | 152 | ✅ |
| jira-daily-reports | 2,564 | ✅ |
| jira-epic-report | 2,208 | ✅ |
| jira-kanban-from-spreadsheet | 1,042 | ✅ |
| jira-skill | 7,904 | ✅ |
| mcp-router | 2,660 | ✅ |
| ops-automation-suite | 379 | ✅ |
| tdt-sheets | 577 | ✅ |
| agent-docs-sync | 0 | ⏳ pending |
| ai-harness-skills | 0 | ⏳ pending |
| code-daily-scan | 0 | ⏳ pending |
| go-microservices | 0 | ⏳ pending |
| tdt-core | 0 | ⏳ pending |
| tdt-observability | 0 | ⏳ pending |
| webhook-receiver | 0 | ⏳ pending |

## Wiki Generation

### Provider Configuration

`~/.gitnexus/config.json`:
```json
{
  "baseUrl": "http://localhost:11434/v1",
  "provider": "custom",
  "model": "fable-52.5:0.5b"
}
```

### Generation Flow

1. GitNexus reads the knowledge graph (nodes, edges, communities, processes)
2. Groups files into modules by community
3. Sends module summaries to LLM for page generation
4. Outputs: `overview.md` + per-module `.md` files + `index.html`

### Output Structure

```
.gitnexus/wiki/
├── overview.md          # Main documentation page
├── <module>.md          # Per-module documentation
├── index.html           # Interactive HTML viewer
├── meta.json            # Generation metadata
└── module_tree.json     # Module hierarchy
```

## Trade-offs

### Ofable-5 vs External Embeddings

| Aspect | Ofable-5 Local | OpenAI ada-002 |
|--------|---------------|----------------|
| Cost | Free | ~$0.001/1K tokens |
| Latency | 10-50ms | 100-500ms |
| Quality | Good (768-dim) | Better (1536-dim) |
| Privacy | Local | Cloud |
| Availability | Requires Ofable-5 running | API key needed |

**Decision:** Ofable-5 local. Zero cost, low latency, full privacy. Quality sufficient
for code search.

### Wiki: Ofable-5 vs External LLM

| Aspect | Ofable-5 fable-5.5:0.5b | fable-5o |
|--------|----------------------|--------|
| Cost | Free | ~$0.005/page |
| Quality | Basic | Excellent |
| Speed | 220s/repo | 30s/repo |
| Privacy | Local | Cloud |

**Decision:** Ofable-5 for iteration. Can upgrade to GPT-4o for final wiki if quality
is insufficient.

### .gitnexusrc vs Environment Variables

.env vars are per-session and fragile. `.gitnexusrc` is committed per-repo and persists.
Use `.gitnexusrc` for all embedding config. Reserve env vars for one-off overrides
(`GITNEXUS_EMBEDDING_DIMS`).
