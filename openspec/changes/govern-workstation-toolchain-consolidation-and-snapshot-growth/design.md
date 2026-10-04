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

Tool-installation split, measured:

| Location | Role | Contents |
|---|---|---|
| `/opt/homebrew/lib/node_modules` | npm's **effective default** — `npm config get prefix` → `/opt/homebrew`, because `node` is a Homebrew formula | `@openai/codex`, `@qoder-ai`, `prime-agent`, `npm` |
| `~/.npm-global/lib/node_modules` | the prefix `workstation-daily-update.sh` installs into (30 packages), but which `~/.npmrc` **never sets** | 30 packages |
| `~/.local/lib/node_modules` | ad-hoc third location | `gitnexus` |

Because the effective prefix and the intended prefix disagree, `npm install -g` and
`npm outdated -g --prefix "$HOME/.npm-global"` operate on **different trees** — the pipeline
reports one set of globals as current while a second tree is the one actually on the path.

Duplicated copies, measured:

| Tool | Copies | Sizes |
|---|---|---|
| `gitnexus` | 3 | 1.0 G (`~/.npm-global`), 1.0 G (`~/.local/lib`), 226 M (`home-toolchain`) |
| `@openai/codex` | 2 | 318 M (`~/.npm-global`), 327 M (`/opt/homebrew/lib`) |
| `@qoder-ai` | 2 | 90 M (`~/.npm-global`), 90 M (`/opt/homebrew/lib`) |

Six `/opt/homebrew/bin` entries are **npm installs symlinked into the package manager's bin
directory**, not package-manager-managed installs:

```console
codex       -> ../lib/node_modules/@openai/codex/bin/codex.js
qoder       -> ../lib/node_modules/@qoder-ai/qodercli/bundle/qoder-npm-dispatcher.cjs
qodercli    -> ../lib/node_modules/@qoder-ai/qodercli/bundle/qodercli.js
prime-agent -> ../lib/node_modules/prime-agent/dist/bundle/cli.js
npm, npx    -> ../lib/node_modules/npm/bin/…
```

Homebrew ownership research (which CLI Homebrew actually ships):

| CLI | Homebrew asset | Current installation |
|---|---|---|
| `cursor-agent` | cask `cursor-cli` | package-manager-managed |
| `droid` | cask `droid` | package-manager-managed |
| `opencode` | formula `opencode` (third-party tap; shadows `homebrew/core`) | package-manager-managed |
| `claude` | cask `claude` | vendor download (`~/.local/bin/claude`) |
| `codex` | cask `codex` | npm-global, symlinked into `/opt/homebrew/bin` |
| `hermes-agent` | formula `hermes-agent` exists | vendor install under `~/.hermes/hermes-agent` |
| `buzz` | cask `buzz` | vendor download |
| `Claude-Fable`, `kilo`, `auggie`, `cce`, `pi`, `prime-agent`, `happy` | none | npm-global / vendor |
| `Anthropic` | formula `Anthropic` is a **different tool** (a regex library, deprecated 2027-01-11) | vendor download (`~/.grok/downloads/…`) |

Two collisions are recorded rather than assumed away: Homebrew's `opencode` formula comes from a
third-party tap and *shadows* `homebrew/core/opencode`; and Homebrew's `Anthropic` formula is
unrelated to the installed installer, whose asset is named `grok-build`.

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
- Reconcile the npm global prefix so the effective prefix and the pipeline's intended prefix agree.
- Make duplication, Homebrew availability, and name collisions *visible* through existing audited surfaces.
- Attach each finding to an owning tool command rather than a deletion action.
- Make agent-CLI coverage reconciliation a reported invariant, keeping every installed CLI available.
- Keep every reclamation reversible or separately authorized.

**Non-Goals (design-level):**
- Removing any agent CLI; the coverage requirement declares and reports, it does not decommission. All installed CLIs remain available.
- Forcing all tools onto Homebrew; several have no Homebrew asset at all, so the requirement is preferred-source-where-available.
- Choosing which duplicate copies to remove; the specs require reporting + authorization, not a prescribed deletion set.
- Reducing snapshot history depth; the specs treat depth reduction as separately authorized.
- Selecting a new package manager or relocating `~/.npm-global` to a different user prefix.

## Decisions

### Decision 1: Declare the npm global prefix so the split cannot recur at its root

- **Rationale**: The measured duplication is a *symptom*. The cause is that `~/.npmrc` never sets
  `prefix`, so npm's effective default (`/opt/homebrew`, following `node`) disagrees with the
  prefix the pipeline installs into (`~/.npm-global`). Reconciling by declaring the prefix fixes
  every downstream duplicate at once, whereas removing copies treats symptoms and regrows them on
  the next `npm install -g`.
- **Alternative considered**: deleting the `/opt/homebrew/lib/node_modules` copies. Rejected —
  those are the copies currently live on the path, so removal would break the tools while the
  prefix disagreement remains.

### Decision 2: Prefer the package manager only where it actually ships the tool

- **Rationale**: "Move everything to Homebrew" is not available: Homebrew ships `codex`,
  `claude`, `droid`, `cursor-agent`, `buzz`, `hermes-agent`, and `opencode`, but ships **no**
  asset for `Claude-Fable`, `kilo`, `auggie`, `cce`, `pi`, `prime-agent`, or `happy`. The spec
  therefore requires the preferred source *where one exists* and records the owning ecosystem
  manager otherwise, rather than mandating an unavailable migration.
- **Alternative considered**: a blanket "prefer Homebrew" rule. Rejected — it would mark
  available-only-via-npm tools as permanently non-compliant, and would push the naive migration
  of `Anthropic` onto an unrelated regex-library formula.

### Decision 3: Record name collisions explicitly

- **Rationale**: Two measured collisions would cause damage if assumed benign. Moving `Anthropic`
  to Homebrew's `Anthropic` formula would install a deprecated regex library in place of the
  installer. Homebrew's `opencode` formula comes from a third-party tap that shadows
  `homebrew/core/opencode`, so the tap of record must be stated. Both are recorded as facts the
  inventory reports, not decisions the migration makes silently.
- **Alternative considered**: relying on exact name matching. Rejected — name matching is
  precisely what produced both collisions.

### Decision 4: A package manager's bin directory does not imply package-manager ownership

- **Rationale**: Six tools *appear* package-manager-managed because they are symlinked into
  `/opt/homebrew/bin`, while resolving into an ecosystem manager's module directory. Any
  ownership rule that trusts the bin directory would misattribute them and then "upgrade" them
  through the wrong manager.
- **Alternative considered**: treating `bin` location as ownership evidence. Rejected on the
  measured counterexample.

### Decision 5: Extend `workstation-storage-hygiene` rather than create a second cleanup capability

- **Rationale**: A parallel cleanup workflow would duplicate the four-class safety model and the
  owning-tool-command rule, and would give operators two places to look. Adding two scenarios to
  the existing classification requirement keeps one governed entry point.
- **Alternative considered**: a standalone `toolchain-cleanup` capability. Rejected — it would
  fork the safety model and conflict with the retention policy's exclusion-list semantics.

### Decision 6: Report duplication; never delete by duplication alone

- **Rationale**: A duplicate is only safe to reclaim once the authoritative copy is proven to
  serve the tool. `gitnexus` demonstrates the hazard: its `~/.npm-global` copy is not the one on
  the path, so deleting it would remove the sanctioned install while leaving resolution pointed
  elsewhere.
- **Alternative considered**: authorizing removal of any copy not on the path. Rejected — path
  resolution can change with shell profile order, so on-path status alone is not durable
  evidence.

### Decision 7: Snapshot growth is bounded by repack, not by deletion

- **Rationale**: Loose objects exist because Git has not repacked yet; the same history already
  occupies 17.41 MiB packed. Repacking is Git's own supported operation, preserves every object
  and the full 862-commit history, and is exactly the "owning-tool command" the existing
  capability requires. Deleting object files would corrupt the store.
- **Alternative considered**: truncating history (depth reduction). Rejected as the default —
  it destroys recoverable state, so the specs require separate authorization instead.

### Decision 8: Growth bounds are enforced on a schedule, not corrected once

- **Rationale**: The defect is recurrence, not a single oversized store. A one-off `gc` would
  regrow at ~18 commits/day (~10 GiB per ~7 weeks, extrapolated from the measured 9.67 GiB over
  48 days). Enforcement therefore belongs in the existing daily maintenance pipeline alongside
  the stages already there.
- **Alternative considered**: a dedicated snapshot-store agent. Rejected — the daily pipeline
  already owns workstation maintenance and reporting.

### Decision 9: Coverage is a declaration reconciled against discovery, and retains every CLI

- **Rationale**: The runner's covered set is the authority, so the correct contract is
  "declared versus discovered", reusing the pattern already in the script. Undeclared CLIs are
  reported, never updated and never removed, so an unrecognized tool cannot be changed without an
  explicit declaration while remaining fully available.
- **Alternative considered**: auto-updating or pruning every discovered CLI. Rejected — it would
  run unknown update verbs against undeclared tools, or remove tools the operator still uses.

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

1. Declare the npm global prefix in `~/.npmrc` so `npm config get prefix` matches the prefix the pipeline installs into; verify `npm prefix` and the pipeline's `--prefix` agree before touching any tree.
2. Add the reconciliation and reporting to the existing runner as read-only stages; observe one
   full run before any reclamation.
3. Declare the currently undeclared agent CLIs (covered or uncovered) with their installation
   sources and matching update verbs, so the report reaches a clean baseline.
4. Repack each declared snapshot store via its owner command, recording before/after
   measurements; verify the owning tool still reads the store.
5. Report tool-install duplication, Homebrew availability, and name collisions with measured
   sizes; reclaim only after per-tool authorization and the post-reclamation execution check.
6. Rollback: no step is destructive by itself; the prefix declaration is a single `~/.npmrc`
   line, repack preserves history, and duplicate reclamation is reversible by reinstalling from
   the owning manager.

## Open Questions

- Whether `~/.local/lib` should remain a sanctioned location at all, once the prefix is declared
  — deferrable; the specs require reporting and authorization regardless of the answer.
- Whether the vendor-downloaded CLIs that *do* have a Homebrew asset (`claude`, `buzz`,
  `hermes-agent`) should later migrate to it — deferrable; the spec requires reporting the
  available asset, not performing the migration.
- Whether the six npm symlinks inside `/opt/homebrew/bin` should be removed once the prefix is
  declared — deferrable; removal is gated on the post-reclamation execution check either way.
- The exact default ceiling for the snapshot store — deferrable; any declared value satisfies the
  contract and can be tuned from measurement.
