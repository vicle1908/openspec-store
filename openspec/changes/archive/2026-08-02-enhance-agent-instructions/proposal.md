# Proposal: Enhance Agent Instructions

## Why

The repository has 7 AGENTS.md files totaling ~14.7KB, but they lack several
elements that 2025–2026 modern practices consider standard. Research against
the agents.md spec (23.3k stars, Linux Foundation), Apache Airflow's AGENTS.md
(34.6KB), Claude Code's memory docs, and GitHub Copilot's custom instructions
docs identified the following gaps:

1. **No project overview** — agents cannot determine repo purpose without reading README
2. **No prerequisites** — agents don't know which tools/versions to install
3. **No explicit pitfalls/gotchas** — agents repeat known mistakes (Redis CONFIG, integration test tags, Docker compose multi-file builds)
4. **Stale commit text** — "outer repository has no commit history yet" is false (6 PRs merged)
5. **Orphaned mcp-router guide** — lives at `tools/agentguide/` but the actual repo has no AGENTS.md
6. **CLAUDE.md diverged** — only contains graphify info, not portable across agents
7. **No navigation table** — agents don't know which subdirectory guides exist

## What Changes

- Enhance root `AGENTS.md` with project overview, prerequisites, pitfalls, commit format, and navigation table (within 550-word limit)
- Remove stale "no commit history" text from root AGENTS.md
- Reconcile root `CLAUDE.md` to import AGENTS.md content for cross-agent portability
- Deploy mcp-router guide to its actual repo or remove orphan
- No spec-level behavior changes (skip_specs: true)

## Affected Boundaries

- Root `AGENTS.md` (outer repository guidelines)
- Root `CLAUDE.md` (Claude Code / cross-agent instructions)
- `tools/agentguide/mcp-router.AGENTS.md` (orphaned guide)

## Non-Goals

- No changes to subdirectory AGENTS.md files (platform, services, deploy, openspec, scripts) — they are already well-structured
- No new spec deltas — purely agent instruction improvements
- No changes to service code, deployment manifests, or CI workflows

## Compatibility

Backward compatible. All changes are additive to instruction files. Existing
agents that already load these files will see improved context. No behavioral
changes to services.

## Rollback

Revert the commits modifying AGENTS.md and CLAUDE.md files. No stateful
systems are affected.
