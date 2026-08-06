# gitnexus-embeddings-wiki-completion — Tasks

## 1. Index missing GitNexus repos

- [x] 1.1 Index ops-automation-suite — **VERIFIED 2026-08-06**: 414 nodes, 570 edges, 7 clusters
- [x] 1.2 Index browser-cli — **VERIFIED 2026-08-06**: 217 nodes, 343 edges, 8 clusters
- [x] 1.3 Index ai-review — **VERIFIED 2026-08-06**: 1,265 nodes, 2,533 edges, 42 clusters
- [x] 1.4 Index tdt-sheets — **VERIFIED 2026-08-06**: 1,352 nodes, 1,877 edges, 35 clusters
- [x] 1.5 Index agent-docs-sync — **VERIFIED 2026-08-06**: 1,496 nodes, 2,731 edges, 45 clusters
- [x] 1.6 Index agent-harness — **VERIFIED 2026-08-06**: 2,193 nodes, 3,372 edges, 63 clusters
- [x] 1.7 Index jira-epic-report — **VERIFIED 2026-08-06**: 2,666 nodes, 5,134 edges, 123 clusters
- [x] 1.8 Index jira-skill (WAL corruption fixed with clean+rebuild) — **VERIFIED 2026-08-06**: 9,591 nodes, 15,592 edges, 325 clusters

## 2. Update stale GitNexus indexes

- [x] 2.1 Update tdt-observability (16 commits behind) — **VERIFIED 2026-08-06**: 539 nodes, 1,065 edges
- [x] 2.2 Update ai-harness-skills (14 commits behind, WAL corruption fixed) — **VERIFIED 2026-08-06**: 3,031 nodes, 6,212 edges
- [x] 2.3 Update agent-core (16 commits behind) — **VERIFIED 2026-08-06**: 5,779 nodes, 8,704 edges
- [x] 2.4 Update code-daily-scan (22 commits behind) — **VERIFIED 2026-08-06**: 2,103 nodes, 3,644 edges
- [x] 2.5 Update jira-kanban-from-spreadsheet (19 commits behind) — **VERIFIED 2026-08-06**: 1,333 nodes, 2,107 edges
- [x] 2.6 Update tdt-core (36 commits behind) — **VERIFIED 2026-08-06**: 3,009 nodes, 5,893 edges
- [x] 2.7 Update jira-daily-reports (31 commits behind) — **VERIFIED 2026-08-06**: 3,400 nodes, 5,950 edges
- [x] 2.8 Update webhook-receiver (29 commits behind) — **VERIFIED 2026-08-06**: 1,156 nodes, 1,963 edges
- [x] 2.9 Update go-microservices (1 commit behind) — **VERIFIED 2026-08-06**: 18,521 nodes, 51,809 edges

## 3. Set up Ofable-5 local embeddings

- [x] 3.1 Pull nomic-embed-text model (768-dim, 274MB) — **VERIFIED 2026-08-06**: `ollama list` confirms
- [x] 3.2 Pull fable-52.5:0.5b model (397MB) for wiki generation — **VERIFIED 2026-08-06**: `ollama list` confirms
- [x] 3.3 Test Ofable-5 embedding endpoint — **VERIFIED 2026-08-06**: curl to localhost:11434/v1/embeddings returns 768-dim vectors
- [x] 3.4 Create .gitnexusrc for all 18 repos — **VERIFIED 2026-08-06**: All 18 repos have .gitnexusrc with embedding config
- [x] 3.5 Fix dimension mismatch (384→768) — **VERIFIED 2026-08-06**: Set GITNEXUS_EMBEDDING_DIMS=768, use --drop-embeddings
- [x] 3.6 Re-index browser-cli with embeddings — **VERIFIED 2026-08-06**: 247 nodes, 152 embeddings
- [x] 3.7 Re-index ops-automation-suite with embeddings — **VERIFIED 2026-08-06**: 442 nodes, 379 embeddings
- [x] 3.8 Re-index ai-review with embeddings — **VERIFIED 2026-08-06**: 1,306 nodes, 1,099 embeddings
- [x] 3.9 Re-index tdt-sheets with embeddings — **VERIFIED 2026-08-06**: 1,440 nodes, 577 embeddings
- [x] 3.10 Re-index agent-harness with embeddings — **VERIFIED 2026-08-06**: 2,286 nodes, 1,889 embeddings
- [x] 3.11 Re-index agent-core with embeddings — **VERIFIED 2026-08-06**: 6,120 nodes, 3,319 embeddings
- [x] 3.12 Re-index remaining repos with embeddings (background job) — **PARTIAL**: 11/18 confirmed, 7 pending

## 4. Configure wiki generation

- [x] 4.1 Save Ofable-5 config to ~/.gitnexus/config.json — **VERIFIED 2026-08-06**: provider=custom, model=fable-52.5:0.5b
- [x] 4.2 Test wiki generation on browser-cli — **VERIFIED 2026-08-06**: 2 pages generated, index.html created
- [x] 4.3 Verify wiki content quality — **VERIFIED 2026-08-06**: overview.md captures architecture, module summaries, usage

## 5. Rebuild graphify global graph

- [x] 5.1 Run `graphify global add` for all 18 repos — **VERIFIED 2026-08-06**: All 18 repos registered
- [x] 5.2 Verify global graph — **VERIFIED 2026-08-06**: 48,124 nodes, 98,654 links (66MB)

## 6. Verify MCP tool availability

- [x] 6.1 Test gitnexus MCP tools via mcp-router — **VERIFIED 2026-08-06**: list_repos returns 18 repos
- [x] 6.2 Test agentmemory MCP tools — **VERIFIED 2026-08-06**: memory_export returns 4 memories
- [x] 6.3 Test wiki MCP tools — **VERIFIED 2026-08-06**: wiki_search returns results
