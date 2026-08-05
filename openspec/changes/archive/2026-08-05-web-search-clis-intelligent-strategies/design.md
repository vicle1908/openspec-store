# Design: Intelligent Strategies

## Architecture

New section `## Intelligent Strategies` inserted after `## Search Strategy`, before `## Command Reference`. The 22 existing pitfalls remain but the most actionable ones get cross-referenced into the new section.

### 1. Tool Selection Decision Tree

A flowchart-style decision guide:

```
Task: Research a topic
├── Need official library docs? → ctx7 (two-step)
├── Need GitHub repo overview? → deepwiki (toc → wiki → ask)
├── Need general web results? → bx web (fast, free) or tvly search
├── Need semantic/deep understanding? → exa (neural/deep)
├── Need to bypass bot detection? → brightdata scrape
├── Need structured data (Amazon, LinkedIn)? → brightdata pipelines
├── Need images/videos? → bx images/bx videos (only source)
├── Need deep research report? → tvly research run
└── Need to extract page content? → tvly extract (free) > brightdata scrape (richer, paid)
```

### 2. Error Recovery Playbook

Tool-specific error → recovery action:

| Error | Tool | Recovery |
|-------|------|----------|
| `OPTION_NOT_IN_PLAN` (400) | bx | `bx "query"` defaults to paid `context`. Always use `bx web "query"` |
| `RATE_LIMITED` (429) | bx | Sleep 2s, or switch to tvly/exa for same query |
| `EXA_API_KEY is required` | exa | `export EXA_API_KEY=...` in shell, or use MCP fallback |
| `Repository not found` | deepwiki | Repo not indexed. Try `web_extract` on GitHub README instead |
| Empty `ctx7 docs` output | ctx7 | Library ID wrong. Re-run `ctx7 library` with more specific query |
| `tvly extract` returns minimal content | tvly | Page is JS-rendered. Switch to `brightdata scrape` or `brightdata browser` |
| `brightdata scrape` empty/broken | brightdata | Site has strong bot protection. Use `brightdata browser` for interactive rendering |
| `brightdata discover` slow | brightdata | Normal — it polls. Set timeout 60s+. Use tvly/exa for speed-sensitive paths |

### 3. Cost/Quality/Speed Matrix

| Priority | Recommended Stack | Trade-off |
|----------|------------------|-----------|
| **Speed** | bx web → tvly extract | Fast results, good quality, free |
| **Quality** | exa neural + tvly research run | Higher cost, deeper understanding |
| **Cost** | bx web + tvly extract + deepwiki | All free, covers most needs |
| **Completeness** | bx + tvly + exa + ctx7 + deepwiki parallel | Maximum coverage, moderate cost |
| **Bot bypass** | brightdata scrape/browser | Higher cost, handles protected sites |
| **Source code** | ctx7 + deepwiki + exa --category publication | Library docs + repo knowledge + papers |

### 4. Result Quality Assessment

After getting initial results, assess quality before diving deeper:

- ** bx results**: Check if results match query intent (bx returns exact-match heavy results)
- ** tvly results**: relevance scores (0.0-1.0) indicate match quality
- ** exa results**: benchmark scores and source reputation ratings
- ** ctx7 results**: benchmark score (0-100), source reputation (High/Medium/Low), snippet count
- ** deepwiki results**: check if repo is indexed (TOC returned = indexed; error = not indexed)

Quality thresholds:
- exa: skip results with no relevance score
- ctx7: prefer libraries with benchmark > 70 and "High" reputation
- tvly: prefer results with score > 0.7

### 5. Adaptive Research Flow

Start broad, narrow based on evidence:

```
Phase 1: Quick triage (parallel)
├── bx web "topic" --count 3 (fast, free)
└── tvly search "topic" --max-results 3 (relevance scores)

Phase 2: Assess Phase 1
├── If results are sufficient → extract best URLs → synthesize answer
├── If results are shallow → exa neural/deep for deeper understanding
├── If topic is a library → ctx7 library → ctx7 docs
├── If topic is a repo → deepwiki toc → deepwiki wiki
└── If topic is niche → tvly research run (15-source synthesis)

Phase 3: Verification (optional, for high-stakes)
├── Cross-check with exa answer (citations)
├── Verify specific claims with brightdata scrape
└── Check academic sources with arxiv search
```
