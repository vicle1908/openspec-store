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

Every declared CLI provides a **non-interactive** self-update verb, and invoking one while already current is a no-op (observed: `claude update` → `Claude Code is up to date (2.1.289)`, exit 0). Only `claude` currently has native background auto-update enabled; `codex`, `Claude-Fable`, `opencode`, `kilo`, `auggie`, and `pi` have none — which is why the pipeline backstop is required.

Homebrew's own source confirms the mechanism: a cask's `auto_updates` means the tool updates itself, and brew explicitly declines to consider such a cask outdated (`return false if !auto_updates`). A cask or formula *without* it is the case where brew owns version — and therefore the case where pairing it with a self-updating tool causes drift.

Official vendor documentation names **multiple** channels, so the choice cannot be made on preference alone: `codex` documents both `npm install -g @openai/codex` and `brew install --cask codex`; `claude` documents both `brew install --cask claude-code` and `npm install -g @anthropic-ai/claude-code`. The two channels disagree about who owns version, which is exactly what the missing rule must resolve.

## What Changes

- MODIFY `workstation-toolchain-inventory`'s "Preferred package-manager source is used where one exists" so a *documented* channel is preferred, multiple documented channels are recorded rather than arbitrarily chosen, and the choice between them is delegated to the version-authority rule.
- ADD "Exactly one version authority per tool" to `workstation-toolchain-inventory`: where a tool self-updates, its self-updater is the version authority and a package manager owns version only if its asset explicitly defers version control; a tool claimed by both is reported as a version-authority drift defect.
- ADD "Self-update is the preferred update path and the pipeline backstop" to `workstation-toolchain-inventory`: native background auto-update is left enabled, and the maintenance pipeline invokes each declared tool's self-update verb as an idempotent backstop so tools without native auto-update still advance. A package manager's upgrade path MUST NOT be substituted.
- MODIFY `agent-cli-inventory-coverage`'s "Each CLI's installation source is recorded" so the recorded update verb is the one belonging to the version authority.
- ADD "Every declared CLI has a declared update path" to `agent-cli-inventory-coverage`: coverage requires an update path per CLI, and the runner invokes it as a backstop each run.
- ADD "Coverage reporting distinguishes drift from coverage findings" so a version-authority conflict is reported distinctly from undeclared coverage and from update failures.
- Record the drift matrix, the official-documentation and self-update evidence, and the decision rules in `design.md`, with tasks to implement drift detection, measurement-failure separation, and the self-update backstop.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `workstation-toolchain-inventory`: the preferred-source requirement is refined to documented channels and delegating to a new version-authority requirement; two requirements are added — exactly-one-version-authority, and self-update-preferred-with-pipeline-backstop.
- `agent-cli-inventory-coverage`: the installation-source requirement is refined so update verbs target the version authority; two requirements are added — every-declared-CLI-has-an-update-path, and drift-reported-distinctly.

## Impact

- `platform/openspec-store/openspec/specs/workstation-toolchain-inventory/spec.md` — one requirement modified, one added
- `platform/openspec-store/openspec/specs/agent-cli-inventory-coverage/spec.md` — one requirement modified
- `~/Developer/scripts/workstation-daily-update.sh` — drift reporting for the declared agent-CLI set
- No tool is removed or downgraded; this governs which mechanism may set each tool's version
- No code and no installed tool is modified by this proposal
