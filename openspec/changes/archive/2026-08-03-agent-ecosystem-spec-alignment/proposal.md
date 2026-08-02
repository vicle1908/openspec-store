## Why

The agent ecosystem (agent-core, agent-docs-sync, agent-harness) has 27+ specs
in the OpenSpec store with inconsistent naming conventions, mixed ownership, and
no formal linkage between repos and their specs. Specifically:

- docs-sync-* specs use a different prefix than agent-docs-sync-* specs
- harness-workflow-architecture uses a different prefix than agent-harness-* specs
- Standalone harness-skill specs (harness-*) are interleaved with agent-harness
  specs, creating confusion about which system owns which spec
- The store's workspace context doesn't mention the agent repos at all
- No ownership catalog maps specs to repos, modules, or docs

This misalignment prevents automated tooling from discovering which specs govern
which code, and makes it impossible to validate that all specs for a repo are
consistent with its current implementation.

## What Changes

- Standardize all agent-ecosystem spec naming to use repo-prefixed conventions:
  `agent-core-*`, `agent-docs-sync-*`, `agent-harness-*`
- Move standalone harness-skill specs to `_standalone/` subdirectory to separate
  them from our agent-harness specs
- Add real Purpose text to 16 specs that had empty or generic boilerplate
- Update the store's workspace context to include the agent ecosystem
- Create SPEC_INDEX.md in each repo as the canonical ownership catalog
- All 27 agent-ecosystem specs pass strict validation after changes

## Capabilities

### New Capabilities

- None. This change reorganizes existing specs without adding new normative
  requirements.

### Modified Capabilities

- None. The rename and purpose-text updates are structural; no requirement text
  changes.

## Impact

- **Specs:** 7 renamed, 8 moved to `_standalone/`, 16 purpose text updates
- **Repos:** 3 SPEC_INDEX.md files added (agent-core, agent-docs-sync, agent-harness)
- **Store config:** workspace context updated to include agent ecosystem
- **Validation:** 349/349 specs pass `openspec validate --strict --all`
