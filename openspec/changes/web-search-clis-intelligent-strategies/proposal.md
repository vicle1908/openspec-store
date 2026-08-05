# Proposal: Add Intelligent Strategies to web-search-clis

## Why

The skill has tools, commands, parallel/sequential patterns, and pitfalls — but lacks **decision intelligence**: when to prefer one tool over another, how to recover from errors, how to optimize for cost/quality/speed, and how to adapt strategy based on initial results. The pitfalls section has grown to 22 items but is a flat list without actionable decision logic.

Real-world testing revealed concrete evidence:
- `bx "query"` defaults to paid `bx context` — confirmed `OPTION_NOT_IN_PLAN` error
- `tvly extract` returns ~2KB vs `brightdata scrape` ~40KB for same URL — quality trade-off is real
- `ctx7` vague queries return wrong libraries (Spring instead of FastAPI)
- `deepwiki ask` fails on repos not yet indexed on deepwiki.com
- `exa` EXA_API_KEY must be exported in shell (not always inherited)
- `brightdata discover` is free but slow (5+ polling attempts)

## What Changes

1. **SKILL.md** — Add `## Intelligent Strategies` section with:
   - Tool Selection Decision Tree (what to pick first based on task type)
   - Error Recovery Playbook (what to do when each tool fails)
   - Cost/Quality/Speed Optimization matrix
   - Result Quality Assessment (how to evaluate if results are good enough)
   - Adaptive Research Flow (adjust strategy based on initial results)

2. **Consolidate pitfalls** — Merge the 22-item flat list into the intelligent strategies section where appropriate, keeping the pitfalls section focused on tool-specific gotchas only.

## Non-Goals

- Modifying tool internals
- Adding new tools
- Changing other skills

## Affected Ownership

- Skill file: `~/.hermes/skills/research/web-search-clis/SKILL.md`
