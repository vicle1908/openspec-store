## Why

The second review pass still leaves three archived capability contracts broader or less precise than the implemented pydantic-ai harness boundary, and the evidence record does not yet identify the resolved dependency versions, implementation identities, or forwarding test. This correction makes the public SDK/internal adapter boundary, public runtime options versus private legacy aliases, explicit compaction disablement, and evidence limitations auditable without changing product code or historical archives.

## What Changes

- Align the `vendor-isolation` purpose and requirements with intentional public SDK runtime-type forwarding and the internal adapter boundary; retain focused lint enforcement without the obsolete blanket claim.
- Make `agent-core-capabilities` enumerate supported public runtime options and distinguish them from private legacy/config aliases that are not a public construction API.
- Name `compaction_enabled=false` as the supported explicit compaction disablement and state that deterministic evidence does not establish live behavior or provider acceptance.
- Add the resolved `pydantic-ai` 2.32.0 and `pydantic-ai-harness` 0.23.0 versions, implementation SHAs, the harness-forwarding test command, and both correction archive paths to the task/evidence record.
- Retain all existing scenario labels and preserve the existing `2026-08-21-reconcile-pydantic-ai-harness-capability-contract` archive.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vendor-isolation`: Correct the stated purpose and public SDK/internal adapter boundary.
- `agent-core-capabilities`: Separate supported public runtime options from private legacy aliases.
- `agent-compaction`: Name explicit `compaction_enabled=false` disablement and narrow evidence claims.

## Impact

Only the new CLI-managed change, its archive, and the three corresponding main capability specs are in scope, plus the requested SDD evidence report. No product source, dependency lock, existing dated archive, unrelated active change, credential, provider, or live service is changed.
