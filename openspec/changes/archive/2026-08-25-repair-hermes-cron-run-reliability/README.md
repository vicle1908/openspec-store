# repair-hermes-cron-run-reliability

**Status:** Implementation approved and in progress.
**Created:** 2026-08-24
**Schema:** spec-driven

## Scope

Three-track cron job reliability repair:
1. **Deterministic watchdog** — no-agent wrapper for mcp-router-health.sh
2. **Read-only freshness reporter** — consumes knowledge-status.sh --json, no mutations
3. **Wiki lint corrections** — frontmatter, links, schema sync

## Ownership

Approved 2026-08-25:
- Watchdog and freshness wrappers: `ops-automation-suite/scripts/hermes-cron/`
- Wiki validator: `wiki/scripts/wiki-lint.py`
- Knowledge-refresh automation: migrate to `ops-automation-suite/scripts/knowledge-refresh/`
- Runtime copies under `~/.hermes/scripts/` and `~/Developer/scripts/knowledge-refresh/` are projections, not canonical sources.

## Decision Gates

- ~~**Script ownership**~~ — Approved 2026-08-25.
- **Graphify version pin**: Out of scope (0.9.42→0.9.46/0.9.48 needs separate compatibility review)

## Files

- `proposal.md` — Why + What Changes
- `design.md` — Architecture decisions, trade-offs, ownership
- `tasks.md` — Implementation tasks with acceptance criteria
- `review-scope.yaml` — Review edges and provider assignments
- `evidence.md` — Baseline diagnostic evidence
- `specs/` — Delta specs (2 ADDED, 1 MODIFIED)
- `reviews/` — Multi-provider review evidence
