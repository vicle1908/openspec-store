# Design: Add ctx7 and deepwiki to web-search-clis Skill

## Architecture

The enhancement is additive — two new tool sections appended to the existing SKILL.md following the established pattern (prerequisites, command reference, decision matrix, pitfalls, verification).

### ctx7 (Context7 CLI v0.5.7)

**Binary:** `/opt/homebrew/bin/ctx7`
**Purpose:** Library/framework documentation search. Two-step workflow:
1. `ctx7 library <name> <query>` — resolve library name to Context7 library ID
2. `ctx7 docs <libraryId> <query>` — fetch documentation snippets for a specific topic

**Output format:** Structured text with source URLs, code snippets, benchmark scores, and source reputation ratings.

**Key characteristics:**
- No authentication required for library/docs queries
- Returns up to 3 library matches with IDs, descriptions, snippet counts
- Docs query returns code examples with source attribution
- `--json` flag for machine-readable output
- Library IDs follow `/owner/repo` or `/websites/site_name` pattern

### deepwiki (DeepWiki CLI v0.1.0)

**Binary:** `/Users/androidteam/.npm-global/bin/deepwiki`
**Purpose:** GitHub repo documentation/wiki search. Three commands:
1. `deepwiki toc <repo>` — table of contents for repo wiki
2. `deepwiki wiki <repo>` — full wiki content
3. `deepwiki ask <repos...> <question>` — NL Q&A across one or more repos

**Output format:** Markdown content with structured wiki pages, or NL answers for `ask`.

**Key characteristics:**
- No authentication required
- Works with any public GitHub repo (owner/repo format)
- `ask` supports multi-repo questions (cross-repo knowledge)
- `--json` flag for raw server output
- `--quiet` flag to suppress non-essential output

### Decision Matrix Updates

| Task | Tool | Notes |
|------|------|-------|
| Library/framework docs | `ctx7 library` + `ctx7 docs` | Structured docs with code snippets |
| GitHub repo wiki/overview | `deepwiki wiki` | Auto-generated comprehensive wiki |
| Cross-repo Q&A | `deepwiki ask` | Multi-repo natural language questions |

### Trade-offs

- **ctx7** has higher quality for library docs (benchmark-scored, reputation-rated) but requires two steps (resolve → query)
- **deepwiki** is faster for repo overview (single command) but covers only public GitHub repos
- Neither has MCP fallback equivalents yet — documented as "no MCP fallback"
- Both are free with no auth — low friction to adopt

## Integration Points

- Decision matrix gets 2 new rows
- Command reference gets 2 new subsections
- Cost tracking table gets 2 new entries (both free)
- Pitfalls section gets relevant entries for each tool
- Verification checklist gets 2 new items
- AGENTS.md Research & Search Tools table gets updated
