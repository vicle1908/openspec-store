## Why

Three-repository end-to-end verification exposed two fail-open diagnostics and one source-mapping gap: docs-sync can report a failed discovery as compliant, skill diagnostics can reject a profile that the loader successfully resolves from a fallback directory, and directory mappings do not apply to descendant files. These findings must be closed before the verified changes are committed and archived.

## What Changes

- Make docs-sync discovery failures explicit in audit reports and ensure strict audit exits non-zero when execution fails.
- Apply explicit documentation mappings to descendant files using deterministic most-specific prefix selection while preserving exact mappings.
- Align `skills doctor` with loader fallback semantics: malformed candidates remain visible as warnings, while an included-skill error is emitted only when no valid candidate loads.
- Add focused regressions and rerun the full supported-feature verification suites for `agent-core`, `agent-docs-sync`, and `agent-harness`.
- Preserve existing CLI output compatibility and introduce no new dependencies.

### Non-goals

- Redesigning docs-sync discovery, report schemas, or skill loading precedence.
- Changing harness checkpoint behavior or adding new harness features.
- Modifying unrelated active OpenSpec changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-docs-sync`: Require failed discovery to remain distinguishable from a successful empty scan and require directory mappings to cover descendant source files.
- `skill-scope-profiles`: Require profile diagnostics to evaluate included-skill loadability after all ordered fallback candidates are considered.

## Impact

- `agent-docs-sync`: `_discover` and `build_report` are rated **CRITICAL** by GitNexus because they feed all docs-sync CLI modes, multi-repository synchronization, and eight to nine execution flows. `public_surface_provenance` is currently unindexed because it is new, so its risk is unknown. The user explicitly approved proceeding with characterization tests and minimal fail-closed changes.
- `agent-core`: `diagnose_profile` is rated **LOW**, with one direct caller (`skills_doctor`) and one affected process group.
- `agent-harness`: no production behavior change is planned; its full suite remains part of the combined verification gate.
- APIs/dependencies: no breaking API change and no dependency addition.
