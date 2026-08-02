## Why

The agent ecosystem (agent-core, agent-docs-sync, agent-harness) has been
reorganized with consistent naming and ownership catalogs. A comprehensive
assessment validates the current state and identifies actionable gaps:
module test coverage disparities, cross-repo coupling depth, and spec coverage
boundaries. This change documents the validated findings and updates SPEC_INDEX
files with current metrics.

## What Changes

- Add validated test metrics to each SPEC_INDEX.md (test ratios per module)
- Add assessment notes documenting cross-repo coupling patterns
- Add test coverage gap findings for low-ratio modules (llm_gateway, foundation)
- Update agent-core SPEC_INDEX.md with agent-config and agent-step-persistence
  coverage rationale
- No spec text changes — this is a documentation and metrics update

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None.

## Impact

- **Docs:** 3 SPEC_INDEX.md files updated with metrics and findings
- **Specs:** No spec text changes
- **Validation:** 350/350 store validation remains green
