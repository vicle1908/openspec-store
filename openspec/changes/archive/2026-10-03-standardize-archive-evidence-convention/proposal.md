# Proposal

## Why

A prior commit (`6f274f8d`) added an `evidence.md` file to an already-archived change. That conflicts with four existing specifications that require archived change files to remain immutable and corrective evidence to be written to a new active change. The corrective change must both record that discrepancy and close the underlying gap: archive evidence is an unenforced, unsanctioned convention — only 78 of 619 archived changes (12.6%) carry evidence in either form, its usage peaked at 57% in 2026-09 and regressed to 25% in 2026-10, and two incompatible forms coexist.

## What Changes

- **Revert the immutability violation.** Remove the `evidence.md` that was added to `openspec/changes/archive/2026-10-03-add-phanmemvip-codex-x-provider/`, restoring that archived directory to its pre-edit state, and preserve the recovered evidence inside this active corrective change instead.
- **Name the evidence artifact in archive guidance.** Extend `operations.archive` guidance in `openspec/config.yaml` to name the evidence artifact and require it for changes that perform verification.
- **Standardize on a single evidence form.** New changes SHALL use a single `evidence.md` file; the legacy `evidence/` directory form is retained for existing archives and not migrated.
- **State an explicit non-goal for backfill.** Existing archives are NOT backfilled; the 543 archives without evidence remain as-is.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `cleanup-archive-verification`: add requirements that corrective evidence is written to the active change only, that an attempt to modify an archived file is rejected and leaves the corrective change incomplete, and that archive evidence uses one standardized form named in archive guidance.
- `archive-integrity-reconciliation`: add a requirement that a discovered immutability violation is recorded and remediated by a subsequent active change that restores the archive to its pre-edit state without further modifying archived bytes.

## Impact

- `openspec/config.yaml` — `operations.archive.guidance` gains an evidence requirement.
- `openspec/changes/archive/2026-10-03-add-phanmemvip-codex-x-provider/` — the added `evidence.md` is removed; the archive returns to its pre-edit content.
- `openspec/changes/standardize-archive-evidence-convention/` — receives the recovered evidence and this change's own evidence.
- **Non-goals**: no backfill of existing archives; no schema fork; no migration between the two evidence forms; no edits to any other archived change.

## Scope note

The immutability requirement already exists in `cleanup-archive-verification`, `archive-integrity-reconciliation`, `archive-closure-audit`, and `ai-review-deployment-state`. This change does not restate those principles; it adds the specific obligations for detecting and recording a violation, and for naming the standardized evidence artifact in guidance.
