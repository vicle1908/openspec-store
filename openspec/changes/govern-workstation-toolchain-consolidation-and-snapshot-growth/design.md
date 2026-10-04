# Design: Govern Workstation Toolchain Consolidation and Snapshot Growth

## Context

See `proposal.md` — Why. Three measured defects motivate this change, and this design records how
each is detected and bounded without destructive action.

### Measured current state (2026-10-04)

Snapshot store, `~/.agentmemory/snapshots` (a Git repository):

```console
$ git count-objects -vH
count: 1359
size: 9.67 GiB        <- loose objects
in-pack: 1227
packs: 1
size-pack: 17.41 MiB  <- packed history
garbage: 10 (164.42 MiB)

commits: 862   oldest 2026-08-17   newest 2026-10-04
reflog: 562 entries   branches: 1   remotes: 0
```

Loose objects are **~570×** the packed representation of the same history. Growth is ~18
commits/day with no repack and no rotation; `state.json` alone is 143 MB.

Tool-install duplication, measured:

| Tool | Copies | Sizes |
|---|---|---|
| `gitnexus` | 3 | 1.0 G (`~/.npm-global`), 1.0 G (`~/.local/lib`), 226 M (`home-toolchain`) |
| `@openai/codex` | 2 | 318 M (`~/.npm-global`), 327 M (`/opt/homebrew/lib`) |
| `@qoder-ai` | 2 | 90 M (`~/.npm-global`), 90 M (`/opt/homebrew/lib`) |

Path resolution is already ambiguous: `gitnexus` resolves to `~/.local/bin/gitnexus`, while
`codex` resolves to `/opt/homebrew/bin/codex` — neither is `~/.npm-global`, despite
`~/.npm-global` being the sanctioned prefix used by the daily update script.

Agent-CLI coverage gap in `~/Developer/scripts/workstation-daily-update.sh`:

```console
covered set:  claude codex opencode kilo auggie qoder pi prime-agent grok
known uncovered: droid
installed but undeclared: happy cursor-agent hermes-agent buzz cce
```

### Existing patterns to reuse

- `workstation-storage-hygiene` already defines the read-only audit, the four safety
  classifications, the owning-tool-command rule, and the prohibition on broad recursive
  deletion. This change **extends that classification** rather than creating a parallel cleanup
  mechanism.
- `workspace-artifact-retention-policy` already defines retention classes and the
  `PROTECTED`/`REVIEW_REQUIRED`/`RECLAIMABLE`/`RECLAIMED` states. Snapshot history maps onto its
  `retained rollback or snapshot` class, and tool installs onto `active index state` or
  `runtime state`.
- `workspace-topology-and-hygiene` already forbids loose artifacts at the workspace root and
  requires cache artifacts to live inside their owning repository.
- The daily update runner already implements the invariant-and-report style this change needs
  (`AGENT_CLI_COVERED` / `AGENT_CLI_KNOWN_UNCOVERED`, per-stage reporting, failure prefixes such
  as `FAILED`). The coverage requirement extends that existing mechanism.

## Goals / Non-Goals

**Goals:**
- Make duplication and snapshot growth *visible* through existing audited surfaces.
- Attach each finding to an owning tool command rather than a deletion action.
- Make agent-CLI coverage reconciliation a reported invariant of the existing runner.
- Keep every reclamation reversible or separately authorized.

**Non-Goals (design-level):**
- Choosing which duplicate copies to remove; the specs require reporting + authorization, not a
  prescribed deletion set.
- Reducing snapshot history depth; the specs treat depth reduction as separately authorized.
- Replacing any agent CLI; the coverage requirement declares and reports, it does not
  decommission.
- Selecting a new package manager or relocating `~/.npm-global`.

## Decisions

### Decision 1: Extend `workstation-storage-hygiene` rather than create a second cleanup capability

- **Rationale**: A parallel cleanup workflow would duplicate the four-class safety model and the
  owning-tool-command rule, and would give operators two places to look. Adding two scenarios to
  the existing classification requirement keeps one governed entry point.
- **Alternative considered**: a standalone `toolchain-cleanup` capability. Rejected — it would
  fork the safety model and conflict with the retention policy's exclusion-list semantics.

### Decision 2: Report duplication; never delete by duplication alone

- **Rationale**: A duplicate is only safe to reclaim once the authoritative copy is proven to
  serve the tool. `gitnexus` demonstrates the hazard: the `~/.npm-global` copy is not the one on
  the path, so deleting it would remove the sanctioned install while leaving resolution pointed
  elsewhere.
- **Alternative considered**: authorizing removal of any copy not on the path. Rejected — path
  resolution can change with shell profile order, so on-path status alone is not durable
  evidence.

### Decision 3: Snapshot growth is bounded by repack, not by deletion

- **Rationale**: Loose objects exist because Git has not repacked yet; the same history already
  occupies 17.41 MiB packed. Repacking is Git's own supported operation, preserves every object
  and the full 862-commit history, and is exactly the "owning-tool command" the existing
  capability requires. Deleting object files would corrupt the store.
- **Alternative considered**: truncating history (depth reduction). Rejected as the default —
  it destroys recoverable state, so the specs require separate authorization instead.

### Decision 4: Growth bounds are enforced on a schedule, not corrected once

- **Rationale**: The defect is recurrence, not a single oversized store. A one-off `gc` would
  regrow at ~18 commits/day (~10 GiB per ~7 weeks, extrapolated from the measured 9.67 GiB over
  48 days). Enforcement therefore belongs in the existing daily maintenance pipeline alongside
  the stages already there.
- **Alternative considered**: a dedicated snapshot-store agent. Rejected — the daily pipeline
  already owns workstation maintenance and reporting.

### Decision 5: Coverage is a declaration reconciled against discovery

- **Rationale**: The runner's covered set is the authority, so the correct contract is
  "declared versus discovered", reusing the pattern already in the script. Undeclared CLIs are
  reported, not updated, so an unrecognized tool cannot be changed without an explicit
  declaration.
- **Alternative considered**: auto-updating every discovered CLI. Rejected — it would run
  unknown update verbs against tools the operator never declared.

### Transaction boundaries

- Reporting stages are read-only; no boundary is crossed by the audit or the coverage check.
- Repack is bounded by the store's own consistency: it either completes or leaves existing
  objects intact; the workflow MUST NOT fall back to filesystem deletion.
- Duplicate reclamation is bounded by the post-reclamation execution check; failure restores the
  duplicate.
- History depth reduction is outside the automated boundary and requires separate authorization.

## Risks / Trade-offs

- **A duplicate appears unused but is required by a specific shell profile or tool** →
  Mitigation: reclamation is gated on the authoritative copy executing successfully afterwards,
  and restoration is required on failure.
- **Repack is interrupted** → Mitigation: Git repack is non-destructive; existing objects remain
  readable, and direct deletion of object files is prohibited.
- **A size ceiling set too low triggers constant repacking** → Mitigation: the ceiling is a
  declared, inspectable value compared against a measured loose-versus-packed split, so it can be
  tuned without changing the contract.
- **Coverage reconciliation reports CLIs that are intentionally installed manually** →
  Mitigation: the uncovered declaration exists precisely so a deliberate manual install is
  declared rather than repeatedly reported.
- **The daily pipeline gains runtime** → Mitigation: reconciliation is local and read-only; it
  requires no network access, unlike the update verbs already in the stage.

## Migration Plan

1. Add the reconciliation and reporting to the existing runner as read-only stages; observe one
   full run before any reclamation.
2. Declare the currently undeclared agent CLIs (covered or uncovered) so the report reaches a
   clean baseline.
3. Repack each declared snapshot store via its owner command, recording before/after
   measurements; verify the owning tool still reads the store.
4. Report tool-install duplication with measured sizes; reclaim only after per-tool
   authorization and the post-reclamation execution check.
5. Rollback: no step is destructive by itself; repack preserves history, and duplicate
   reclamation is reversible by reinstalling the package from the owning manager.

## Open Questions

- Which specific duplicate copies should ultimately be reclaimed, and whether `~/.local/lib`
  should remain a sanctioned location at all — deferrable; the specs require reporting and
  authorization regardless of the answer.
- The exact default ceiling for the snapshot store — deferrable; any declared value satisfies the
  contract and can be tuned from measurement.
