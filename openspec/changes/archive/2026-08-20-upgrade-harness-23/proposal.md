# Proposal: Upgrade pydantic-ai-harness 0.11.0 → 0.23.0

## Summary

Upgrade pydantic-ai-harness from 0.11.0 to 0.23.0 across agent-core, agent-harness, and agent-docs-sync. Integrate new harness capabilities (TieredCompaction, SpendLimits, Advisor, SystemReminders, ConversationSearch) into AgentRuntime. Update all documentation, specs, and dev toolings to reflect the current state.

## Motivation

- pydantic-ai-harness 0.23.0 ships 20+ capabilities with 13 releases in 27 days
- New capabilities (TieredCompaction, SpendLimits, Advisor) provide production-ready features that were previously custom code
- aligns with pydantic-ai v2.32.0 (our pinned range: >=2.31.0,<2.33)
- Removes stale version references across the workspace

## Scope

### Repos affected
- **agent-core** — dependency bump, capability integration, docs, tests
- **agent-harness** — dependency bump, type fixes, docs, tests
- **agent-docs-sync** — dependency bump, docs
- **openspec-store** — spec updates, archival of stale specs
- **wiki** — entity page updates

### What changed
1. Dependency pins updated to `pydantic-ai-harness[dynamic-workflow]>=0.23.0,<0.24`
2. AgentRuntime now composes: TieredCompaction, SpendLimits, Planning, Advisor, SystemReminders
3. ConsumerRuntimeProfile.max_iterations default changed from 15 to None
4. 7 OpenSpec specs marked as historical (describe removed harness_config interface)
5. 5 OpenSpec specs updated with current version references
6. All documentation updated with current capabilities and versions
7. Dev toolings updated (ruff >=0.16.3, pre-commit-hooks v6.0.0 added to all repos)
8. Cross-repo SDK boundary fixed (AssuranceLevel exported, lifecycle imports via SDK)

## Alternatives considered

- **Pin to 0.11.0** — rejected: misses 13 releases of improvements and new capabilities
- **Incremental upgrade (0.11→0.15→0.20→0.23)** — rejected: 0.x versioning means each minor may break; single jump with full verification is cleaner
