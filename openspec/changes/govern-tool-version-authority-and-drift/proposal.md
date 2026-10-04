# Proposal

## Why

The archived change `govern-workstation-toolchain-consolidation-and-snapshot-growth` established the sanctioned install locations, the single npm global prefix, and preferred-source reporting, but it left one requirement uncovered: **which mechanism is allowed to determine a tool's version**. Measured on 2026-10-04, several installed agent CLIs can update themselves while their package-manager asset also pins a version — so a package-manager upgrade silently reverts what the tool installed for itself, and the spec has no rule to detect or prevent it.

### Measured version-authority conflicts (2026-10-04)

| Tool | Self-updates | Package asset | Asset defers version? | Outcome |
|---|---|---|---|---|
| `claude` | yes (`update`) | cask `claude` | **yes** (`auto_updates`) | no drift |
| `droid` | no update verb | cask `droid` | **yes** (`auto_updates`) | no drift |
| `codex` | yes (`update`) | cask `codex` | **no** | **drift** — cask pins while the CLI self-updates |
| `Claude-Fable` | yes (`update`) | cask `Claude-Fable` | **no** | **drift** |
| `opencode` | yes (`upgrade`) | formula `opencode` | n/a — formulas always pin | **drift** |

Homebrew's own source confirms the mechanism: a cask's `auto_updates` means the tool updates itself, and brew explicitly declines to consider such a cask outdated (`return false if !auto_updates`). A cask or formula *without* it is the case where brew owns version — and therefore the case where pairing it with a self-updating tool causes drift.

Official vendor documentation names **multiple** channels, so the choice cannot be made on preference alone: `codex` documents both `npm install -g @openai/codex` and `brew install --cask codex`; `claude` documents both `brew install --cask claude-code` and `npm install -g @anthropic-ai/claude-code`. The two channels disagree about who owns version, which is exactly what the missing rule must resolve.

## What Changes

- MODIFY `workstation-toolchain-inventory`'s "Preferred package-manager source is used where one exists" so a *documented* channel is preferred, multiple documented channels are recorded rather than arbitrarily chosen, and the choice between them is delegated to the version-authority rule.
- ADD "Exactly one version authority per tool" to `workstation-toolchain-inventory`: where a tool self-updates, its self-updater is the version authority and a package manager owns version only if its asset explicitly defers version control; a tool claimed by both is reported as a version-authority drift defect.
- MODIFY `agent-cli-inventory-coverage`'s "Each CLI's installation source is recorded" so the recorded update verb is the one belonging to the version authority, and a manager that does not own version MUST NOT be used to update the tool.
- Record the drift matrix, the official-documentation evidence, and the decision rule in `design.md`, with tasks to implement drift detection.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `workstation-toolchain-inventory`: the preferred-source requirement is refined to documented channels and delegating to a new version-authority requirement, which is added.
- `agent-cli-inventory-coverage`: the installation-source requirement is refined so update verbs target the version authority.

## Impact

- `platform/openspec-store/openspec/specs/workstation-toolchain-inventory/spec.md` — one requirement modified, one added
- `platform/openspec-store/openspec/specs/agent-cli-inventory-coverage/spec.md` — one requirement modified
- `~/Developer/scripts/workstation-daily-update.sh` — drift reporting for the declared agent-CLI set
- No tool is removed or downgraded; this governs which mechanism may set each tool's version
- No code and no installed tool is modified by this proposal
