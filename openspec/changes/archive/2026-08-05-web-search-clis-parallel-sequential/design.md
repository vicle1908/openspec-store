# Design: Parallel vs Sequential Search Strategy

## Architecture

New section `## Search Strategy` inserted after Decision Matrix, before Command Reference. This positions it as a cross-cutting concern that applies to all tools.

### Parallel Patterns

**When to parallelize:** Queries are independent — no output from one feeds into another.

| Pattern | Example | Tools |
|---------|---------|-------|
| **Multi-tool triangulation** | Same query across bx + tvly + exa | 3 independent calls |
| **Multi-topic discovery** | Different aspects of a topic simultaneously | 3+ independent calls |
| **Multi-repo Q&A** | `deepwiki ask` on multiple repos | Parallel subagents |
| **Multi-library resolve** | `ctx7 library` for different libraries | Parallel CLI calls |
| **Search + docs + wiki** | Web search + ctx7 docs + deepwiki wiki for same topic | 3 independent calls |

**Rate limit constraints for parallel:**
- bx: 1 req/s — stagger with 2s sleep if running multiple bx calls
- exa: ~$0.005/query — cost awareness for batch runs
- brightdata: limited credits — prefer `discover` (free) over `search` (paid) in parallel
- tvly: generous limits — safe for parallel
- ctx7/deepwiki: no limits — safe for parallel

### Sequential Patterns

**When to go sequential:** Output from step N feeds into step N+1.

| Pattern | Example | Why sequential |
|---------|---------|----------------|
| **ctx7 two-step** | `library` → `docs` | Need library ID before querying docs |
| **Search → extract** | `web_search` → `tvly extract` on top result | Need URL from search |
| **Search → scrape** | `brightdata search` → `brightdata scrape` on result | Need URL from search |
| **Deep research → verify** | `tvly research run` → `exa answer` to cross-check | Verification depends on findings |
| **wiki TOC → targeted ask** | `deepwiki toc` → `deepwiki ask` on specific page | TOC reveals what to ask |
| **Refine loop** | Initial search → analyze gaps → refined search | Quality depends on iteration |

### Hybrid Patterns

**Parallel discovery → sequential deep dive:**

```
Phase 1 (parallel):          Phase 2 (sequential):
├── bx web "topic"           ├── extract top result from Phase 1
├── tvly search "topic"      ├── ctx7 docs on best library
├── exa search "topic"       └── deepwiki ask on related repo
└── deepwiki ask "topic"
```

**Parallel extraction → sequential synthesis:**
```
Phase 1 (parallel):          Phase 2 (sequential):
├── tvly extract URL-A       └── synthesize all extracted content
├── tvly extract URL-B           into unified answer
└── tvly extract URL-C
```

### execute_code for Batching

When running 3+ independent CLI calls, `execute_code` batches them in one tool call:

```python
from hermes_tools import terminal
results = []
for tool, cmd in [
    ("bx", 'bx web "topic" --count 3'),
    ("tvly", 'tvly search "topic" --max-results 3'),
    ("exa", 'exa search "topic" --num-results 3 --plain'),
]:
    r = terminal(cmd)
    results.append({"tool": tool, "output": r["output"]})
```

### delegate_task for Multi-Subagent Research

For complex research requiring multiple independent deep dives:

```python
delegate_task(tasks=[
    {"goal": "Research X using web search and extract key findings"},
    {"goal": "Research Y using arxiv and semantic scholar"},
    {"goal": "Research Z using deepwiki and ctx7 for code docs"},
])
```

Each subagent gets its own terminal session and can run tools independently. Results consolidate automatically.

### Anti-Patterns

1. **Sequential when parallel is safe** — Running 3 independent web searches one after another wastes 3 round-trips. Batch them.
2. **Parallel when sequential is required** — Running `ctx7 docs` before `ctx7 library` resolves the ID. The docs call will fail or return wrong results.
3. **Ignoring rate limits in parallel** — Firing 5 bx calls simultaneously triggers 429s. Stagger or switch to tvly/exa.
4. **Over-parallelizing extraction** — `tvly extract` on 20 URLs simultaneously may hit rate limits. Batch in groups of 5.
5. **Using delegate_task for single-tool calls** — Subagent overhead is wasteful for one `web_search` call. Use direct tool calls for simple lookups.
