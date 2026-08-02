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
The full store (350 specs) is green. No requirement text was modified — only
structural metadata (titles, purpose text, directory organization).

## Learnings

1. **Two harness systems**: The store contained specs for both our
   `agent-harness` (LangGraph-based, depends on agent-core) and a standalone
   `harness-skill` system (no agent-core dependency). The standalone specs
   (`harness-*`) were interleaved with ours, creating confusion. Moving them to
   `_standalone/` resolved this.

2. **Naming inconsistency root cause**: The `docs-sync-*` specs were created
   before the `agent-docs-sync-*` naming convention was established. The
   `harness-workflow-architecture` spec similarly predates the `agent-harness-*`
   convention.

3. **Purpose text gaps**: Many specs had auto-generated boilerplate ("This
   specification defines requirements for X") instead of meaningful purpose
   text. The repair was mechanical — read requirements, derive purpose from
   content.

4. **SPEC_INDEX.md value**: The ownership catalogs immediately revealed which
   docs lack spec coverage (e.g., agent-core has 25 docs but only 13 specs).
   This gap is by design — architecture references, migration guides, and
   configuration docs don't need normative specs.
