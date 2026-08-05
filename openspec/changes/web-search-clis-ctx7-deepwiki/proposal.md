# Proposal: Add ctx7 and deepwiki to web-search-clis Skill

## Why

The web-search-clis skill currently covers 4 web search/extraction CLIs (bx, tvly, exa, brightdata) for general web content. Two additional CLIs are installed but undocumented:

- **ctx7** (v0.5.7) — Context7 CLI for fetching library/framework documentation. Resolves library names to IDs, then queries documentation with natural language. Returns code snippets with source URLs and benchmark scores.
- **deepwiki** (v0.1.0) — DeepWiki CLI for querying any public GitHub repo's auto-generated wiki. Provides table of contents, full wiki content, and natural-language Q&A across one or more repos.

These tools fill a gap in the research toolkit: **source code and library documentation search**, which is distinct from general web search. Current tools return web pages; ctx7 returns structured library docs; deepwiki returns repo-level architectural knowledge.

## What Changes

1. **SKILL.md** — Add ctx7 and deepwiki sections with:
   - Prerequisites (binary locations, auth status)
   - Decision matrix row additions
   - Command reference for all subcommands
   - Cost tracking (both free, no auth required)
   - Common pitfalls
   - MCP fallback notes (if available)
   - Updated verification checklist

2. **Decision Matrix** — Add two new rows:
   - Library/framework docs → `ctx7 library` + `ctx7 docs`
   - GitHub repo wiki/Q&A → `deepwiki ask` + `deepwiki wiki`

3. **AGENTS.md** — Add to Research & Search Tools table

## Non-Goals

- Adding ctx7 MCP server integration (separate concern)
- Adding deepwiki as a Hermes plugin
- Modifying other research skills (arxiv, grounded-citations, etc.)
- Creating OpenSpec delta specs (skip_specs: true — this is a skill file change)

## Affected Ownership

- Skill file: `~/.hermes/skills/research/web-search-clis/SKILL.md`
- Workspace docs: `~/Developer/AGENTS.md` (Research & Search Tools section)
