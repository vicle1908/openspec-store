## Context

Research from official sources (PyPI, GitHub, pydantic.dev) reveals gaps in agent-core research docs. The docs are mostly accurate but miss key features and have outdated capability statuses.

## Goals / Non-Goals

**Goals:**
- Add durable execution documentation (4 solutions)
- Add streaming v3 documentation
- Update harness capability matrix with accurate statuses
- Fix version references

**Non-Goals:**
- Rewriting entire docs (only targeted updates)
- Changing code
- Adding new research topics

## Decisions

### Decision 1: Update in-place, not rewrite

Update specific sections of existing docs rather than rewriting. Preserves existing accurate content.

### Decision 2: Source from official docs

All updates based on official pydantic.dev docs, GitHub releases, and PyPI — not third-party articles.

### Decision 3: Focus on agent-core gaps

Updates prioritize features relevant to agent-core's use of these frameworks.
