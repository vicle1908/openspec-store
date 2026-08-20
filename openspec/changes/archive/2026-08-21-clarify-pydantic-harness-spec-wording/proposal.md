## Why

The archived pydantic-ai harness correction left two purpose-level statements stale and did not enumerate `compaction_enabled` at the supported public boundary, while the vendor contract must continue to describe intentional SDK forwarding alongside internal adapter isolation. This documentation-only correction makes those boundaries precise without changing product code, historical archives, or unrelated active changes.

## What Changes

- Clarify `agent-compaction` purpose and historical context: `AgentConfig.runtime_options()` is a typed projection helper used by public construction, while `AgentRuntime` does not automatically read configuration fields; the supported explicit disablement is `compaction_enabled=false`.
- Replace the `agent-core-capabilities` Purpose placeholder and enumerate `compaction_enabled` among supported public runtime options while keeping private legacy aliases and configuration-only keys separate.
- Keep `vendor-isolation` purpose and requirements aligned with intentional public SDK runtime-type forwarding and internal adapter isolation, without restoring the obsolete blanket import prohibition.
- Preserve every existing scenario label, all dated archives, unrelated active changes, and untracked reports.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-compaction`: Clarify the projection boundary, historical note, and explicit public disablement.
- `agent-core-capabilities`: Replace the Purpose placeholder and include `compaction_enabled` in the public options boundary.
- `vendor-isolation`: Retain wording consistent with intentional public forwarding and internal adapter isolation.

## Impact

Only the CLI-managed change artifacts, its dated archive, and the three corresponding main capability specifications are in scope, plus the requested SDD report. No product source, dependency lock, provider, credential, live service, historical archive, unrelated active change, or `reports/` path is changed.
