## Naming Convention

All agent-ecosystem specs follow a strict prefix convention:

| Repo | Prefix | Example |
|------|--------|---------|
| agent-core | `agent-core-` | `agent-core-components` |
| agent-docs-sync | `agent-docs-sync-` | `agent-docs-sync-memory` |
| agent-harness | `agent-harness-` | `agent-harness-workflow` |

Standalone harness-skill specs (not our repos) live under `_standalone/` in the
store and retain their original `harness-*` names.

## Ownership Model

Each repo has a `SPEC_INDEX.md` that serves as the canonical mapping:
- Spec → Module(s) it governs
- Spec → Doc(s) it covers
- Docs without dedicated spec coverage (and why)

This index is the single source of truth for which specs are normative for which
codebase.

## Store Workspace Context

The store's `openspec/config.yaml` context section now includes the agent
ecosystem with:
- Repo descriptions and dependency relationships
- Naming convention documentation
- Reference to SPEC_INDEX.md files

## Validation Strategy

All 27 agent-ecosystem specs plus 8 standalone specs pass strict validation.
The full store (349 specs) is green. No requirement text was modified — only
structural metadata (titles, purpose text, directory organization).
