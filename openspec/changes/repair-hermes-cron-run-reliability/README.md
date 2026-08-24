# repair-hermes-cron-run-reliability

**Status:** Planning (Multi-provider review completed with partial coverage. Codex returned BLOCK and AGY returned PASS_WITH_CHANGES. Planning corrections are incorporated, but implementation remains gated on cross-repository ownership and final semantic reconciliation.)
**Created:** 2026-08-24
**Schema:** spec-driven

## Scope

Three-track cron job reliability repair:
1. **Deterministic watchdog** — no-agent wrapper for mcp-router-health.sh
2. **Read-only freshness reporter** — consumes knowledge-status.sh --json, no mutations
3. **Wiki lint corrections** — frontmatter, links, schema sync

## Decision Gates

- **Script ownership** (BLOCKS tasks 1.1, 2.1, 3.6): Proposed: ops-automation-suite/scripts/hermes-cron/ + wiki/scripts/wiki-lint.py. Requires explicit user approval before implementation. See design.md Ownership section.
- **knowledge-refresh ownership** (BLOCKS Track 2 `operation_status` extension): `~/Developer/scripts/knowledge-refresh/` is untracked. Requires resolution before Track 2 can extend status fields.
- **Graphify version pin**: Out of scope (0.9.42→0.9.46/0.9.48 needs separate compatibility review)

## Files

- `proposal.md` — Why + What Changes
- `design.md` — Architecture decisions, trade-offs, ownership
- `tasks.md` — Implementation tasks with acceptance criteria
- `review-scope.yaml` — Review edges and provider assignments
- `evidence.md` — Baseline diagnostic evidence
- `specs/` — Delta specs (2 ADDED, 1 MODIFIED)
