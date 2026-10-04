# Design: Govern Tool Version Authority and Drift

## Context

See `proposal.md` — Why. The archived change
`govern-workstation-toolchain-consolidation-and-snapshot-growth` established install locations,
the single npm prefix, and preferred-source reporting, and was implemented: `~/.npmrc` now
declares `prefix = ~/.npm-global`, so `npm config get prefix` and the maintenance pipeline agree.
That change is archived and therefore immutable, so this correction is carried as a new
delta against the live specs.

### Measured version-authority state (2026-10-04)

| Tool | Self-update verb | Package asset | Asset defers version | Outcome |
|---|---|---|---|---|
| `claude` | `update` | cask `claude` (`auto_updates`) | yes | no drift |
| `droid` | none found | cask `droid` (`auto_updates`) | yes | no drift |
| `codex` | `update` | cask `codex` | **no** | **drift** |
| `Claude-Fable` | `update` | cask `Claude-Fable` | **no** | **drift** |
| `opencode` | `upgrade` | formula `opencode` | n/a (formulas pin) | **drift** |

### The mechanism, from Homebrew's own source

A cask's `auto_updates` means the tool updates itself, and Homebrew explicitly declines to treat
such a cask as outdated:

```ruby
def auto_updates_bundle_outdated?
  return false if !auto_updates || version.latest?
  ...
```

So `auto_updates` is not a cosmetic flag: it is the declaration that makes the tool, not the
package manager, the version authority. A cask or formula *without* it is the case where the
package manager owns version — and therefore the case where pairing it with a self-updating tool
produces drift.

### Official vendor documentation names multiple channels

| Tool | Documented channels |
|---|---|
| `codex` | `npm install -g @openai/codex` **and** `brew install --cask codex` |
| `claude` | `brew install --cask claude-code` **and** `npm install -g @anthropic-ai/claude-code` |

The channels disagree about who owns version, so "prefer a package manager" is not sufficient on
its own: the choice must be resolved by the version-authority rule. This is the gap the archived
change left open.

### Existing patterns to reuse

- `workstation-toolchain-inventory` already defines authoritative-location per tool and
  preferred-source reporting; this change refines the latter and adds version authority to the
  same capability rather than creating a parallel one.
- `agent-cli-inventory-coverage` already requires each CLI's installation source to be recorded;
  this change makes the recorded update verb follow the version authority and adds a
  drift-versus-coverage reporting distinction.
- The maintenance runner already reports failure outcomes with a distinct prefix; drift findings
  follow the same reporting style.

## Goals / Non-Goals

**Goals:**
- Give every tool exactly one version authority.
- Report version-authority conflicts as a defect distinct from coverage or update failures.
- Prefer *documented* channels, and record multiple documented channels rather than choosing on
  preference.
- Prevent a package manager from silently reverting a tool's self-updated version.

**Non-Goals (design-level):**
- Removing or downgrading any installed tool; the rule governs which mechanism sets version.
- Forcing every tool onto one package manager; the documented channels differ per tool.
- Changing the already-implemented npm prefix declaration.
- Editing the archived change; its directory is immutable.

## Decisions

### Decision 1: The version authority is the mechanism, not the installer

- **Rationale**: A tool can be *installed* by one manager while its *version* is set by another.
  `codex` is the measured example: installed through a manager that pins, capable of updating
  itself. Treating the installer as the version owner is exactly what produces drift, so the two
  must be modelled separately.
- **Alternative considered**: assuming the installing manager always owns version. Rejected —
  it silently authorises a package-manager upgrade to revert the tool's own update.

### Decision 2: `auto_updates` is the deferral signal for package-manager assets

- **Rationale**: Homebrew's source shows `auto_updates` is precisely "this tool updates itself",
  and brew returns not-outdated when set. It is therefore the official, machine-readable
  deferral declaration, not a heuristic.
- **Alternative considered**: inferring deferral from a tool's own `--help` update verb alone.
  Rejected as the sole signal — the tool's capability and the asset's declaration must both be
  known, and either alone is ambiguous.

### Decision 3: A self-updating tool keeps version authority when its asset defers

- **Rationale**: Where both the tool self-updates and the asset declines version control, the
  package manager is a pure installation channel and there is no conflict. Recording it as drift
  would produce permanent false positives for well-formed installs such as `claude` and `droid`.
- **Alternative considered**: flagging any self-updating tool under any package manager.
  Rejected on the measured counterexample.

### Decision 4: Drift is a distinct finding class

- **Rationale**: Three conditions can co-occur and mean different things: a CLI may be
  undeclared, its update may fail, and its version authority may conflict. Collapsing them would
  make drift invisible behind a coverage or failure message, which is how it went unnoticed.
- **Alternative considered**: reporting drift as a coverage finding. Rejected — coverage is about
  declaration, drift is about version ownership.

### Decision 5: Prefer documented channels, and delegate the tie to version authority

- **Rationale**: Official documentation for `codex` and `claude` names both npm and Homebrew, so
  a preference rule cannot decide. The spec requires recording every documented channel and
  resolving the choice by version authority, which is the only rule that prevents drift.
- **Alternative considered**: hardcoding "Homebrew wins". Rejected — it would push a
  self-updating tool onto a pinning formula (`opencode`) and create drift where none need exist.

### Transaction boundaries

- All new behaviour is read-only reporting: it measures self-update capability and asset
  deferral, and reports conflicts. It does not change any tool's version.
- Where a correction is later applied, it is bounded by the post-change execution check already
  required by `workstation-toolchain-inventory`; a tool must still resolve and execute.

## Risks / Trade-offs

- **A tool's self-update capability is undocumented or hidden behind a flag** → Mitigation: the
  spec requires recording authority as `unknown` with the evidence gaps rather than guessing, so
  an undetermined tool is never falsely reported as reconciled.
- **An asset gains or loses `auto_updates` between releases** → Mitigation: the rule keys on the
  asset's declaration at measurement time, so a change is reported as a new finding rather than
  silently inherited.
- **A future tool both self-updates and ships a deferring formula** → Mitigation: the requirement
  keys on the asset's declaration, not on the asset's kind, so a deferring formula is handled the
  same as a deferring cask.
- **Recording multiple documented channels could read as indecision** → Mitigation: the spec
  states the tie is resolved by the version-authority rule, so the record is evidence, not an
  unresolved choice.

## Migration Plan

1. Record each declared agent CLI's self-update capability and its installing asset's
   version-deferral declaration; produce the measured matrix without changing any tool.
2. Report the current drift set (`codex`, `Claude-Fable`, `opencode`) as findings, distinct from
   coverage and failure findings.
3. Declare each covered CLI's update verb against its version authority, so the recorded verb
   matches the mechanism that owns version.
4. Where a drift is later corrected, do it by choosing a channel whose asset defers version, or
   by letting the tool own version — never by removing the tool. Verify resolution and execution
   afterwards.
5. Rollback: this change is reporting and declaration only; no tool version is modified, so no
   rollback step is required for the plan itself.

## Open Questions

- Whether `codex`, `Claude-Fable`, and `opencode` should ultimately be re-installed through a
  deferring channel, or left as reported drift — deferrable; the spec requires reporting the
  conflict, not resolving it a particular way.
- Whether a self-updating tool with a pinning asset should be *prevented* from being installed
  that way, or merely reported — deferrable; reporting is the required floor in either case.
