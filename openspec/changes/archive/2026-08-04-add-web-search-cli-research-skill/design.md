# Design: Web Search CLI Research Skill

## Architecture

Single SKILL.md at `~/.hermes/skills/research/web-search-clis/SKILL.md`
following the peer-matched structure from existing research skills
(arxiv, grounded-citations, blogwatcher).

### Skill Structure

```
~/.hermes/skills/research/web-search-clis/
└── SKILL.md
```

No scripts or references needed — the skill is a command reference, not
a pipeline. All tools are standalone CLIs invoked via `terminal`.

## Tool Profiles

### bx (Brave Search CLI)

- **Binary:** `/Users/androidteam/.local/bin/bx`
- **Version:** Brave Search CLI (Rust binary)
- **Auth:** `export BRAVE_SEARCH_API_KEY="..."` (from `~/.zshrc`)
- **Default shorthand:** `bx "query"` = `bx context "query"`
- **Free tier:** `web`, `news`, `images`, `videos` (4 of 11 commands)
- **Paid tier adds:** `context` (RAG grounding), `answers` (AI answers), `suggest`, `spellcheck`, `places`
- **Rate limit:** 1 req/s on free plan (429 on burst)
- **Output:** JSON (default), pipe-friendly
- **Strengths:** Fast, broad coverage, news freshness, image/video search

### tvly (Tavily CLI)

- **Binary:** `~/.local/bin/tvly` → uv-managed Python tool
- **Version:** tavily-cli 0.1.6
- **Auth:** `tvly login --api-key tvly-...` (saved to `~/.tavily/config.json`)
- **Commands:** `search`, `extract`, `crawl`, `map`, `research`
- **Free tier:** All commands available (generous rate limits)
- **Output:** Formatted text (default), `--json` flag for JSON
- **Strengths:** Content extraction, deep research (auto-synthesizes 15-source reports), crawl with depth control, site mapping

### exa (Exa CLI)

- **Binary:** `~/.local/bin/exa` (npm: exa-cli v0.1.5)
- **Auth:** `export EXA_API_KEY="..."` (from Zed config)
- **Commands:** `search`, `answer`, `contents`, `find-similar`
- **Free tier:** All commands (costs tracked per request)
- **Search types:** `auto` (~1s), `fast` (~450ms), `neural` (~1s), `deep` (4-15s), `deep-lite` (4s), `deep-reasoning` (12-40s)
- **Output:** JSON (default), `--plain` for text
- **Strengths:** Neural/semantic search, grounded answers with citations, entity extraction (companies, people), find-similar, highlights, summaries, structured output schemas

## Decision Matrix

| Task | Primary Tool | Fallback |
|------|-------------|----------|
| Quick web search | `bx web` | `tvly search` |
| News articles | `bx news` | `tvly search` |
| Image search | `bx images` | — |
| Video search | `bx videos` | — |
| Extract page content | `tvly extract` | `exa contents` |
| Deep research report | `tvly research run` | `exa search --type deep` |
| Grounded answer | `exa answer` | `tvly research run` |
| Semantic/neural search | `exa search` | `bx web` |
| Find similar pages | `exa find-similar` | — |
| Crawl entire site | `tvly crawl` | — |
| Map site URLs | `tvly map` | — |
| Company/people search | `exa search --category company` | — |
| Structured extraction | `exa search --summary-schema` | — |

## MCP Equivalents

When CLIs are unavailable, use MCP tools through mcp-router:

| CLI | MCP Equivalent |
|-----|---------------|
| `bx web` | `mcp__mcp_router__brave_web_search` |
| `tvly search` | `mcp__mcp_router__tavily_search` |
| `tvly extract` | `mcp__mcp_router__tavily_extract` |
| `tvly crawl` | `mcp__mcp_router__tavily_crawl` |
| `tvly map` | `mcp__mcp_router__tavily_map` |
| `tvly research` | `mcp__mcp_router__tavily_research` |
| `exa search` | `mcp__mcp_router__web_search_exa` |
| `exa contents` | `mcp__mcp_router__web_fetch_exa` |
| — | `mcp__mcp_router__brave_news_search` |
| — | `mcp__mcp_router__brave_image_search` |
| — | `mcp__mcp_router__brave_video_search` |

## Auth Key Locations

| Tool | Env Variable | Config Source |
|------|-------------|---------------|
| bx | `BRAVE_SEARCH_API_KEY` | `~/.zshrc` |
| tvly | `TAVILY_API_KEY` | `~/.tavily/config.json` |
| exa | `EXA_API_KEY` | `~/.config/zed/settings_backup.json` |
