# Proposal

## Why

The workstation toolchain has three measured, ungoverned defects: npm's global prefix is split **three ways** — `/opt/homebrew` (npm's effective default, because `node` is a Homebrew formula), `~/.npm-global` (the prefix `workstation-daily-update.sh` installs into, but which `~/.npmrc` never actually sets), and `~/.local/lib/node_modules` (ad-hoc) — causing tools to be installed two and three times over; the `agentmemory` snapshot store has grown to 9.67 GiB of loose Git objects (9.9 GB `.git` against a 17 MiB pack, 862 unbounded commits since 2026-08-17, no repack or rotation); and the daily agent-CLI runner declares a covered set that omits five installed CLIs (`happy`, `cursor-agent`, `hermes-agent`, `buzz`, `cce`). Storage hygiene and retention are already governed by `workstation-storage-hygiene` and `workspace-artifact-retention-policy`, but install-location ownership, snapshot-store growth bounds, and agent-CLI inventory coverage are not, so these defects recur unobserved.

### Measured install-location state (2026-10-04)

| Location | Role | Contents |
|---|---|---|
| `/opt/homebrew/lib/node_modules` | npm's **effective default** (`npm config get prefix` → `/opt/homebrew`, because `node` is a Homebrew formula) | `@openai/codex`, `@qoder-ai`, `prime-agent`, `npm` |
| `~/.npm-global/lib/node_modules` | the prefix `workstation-daily-update.sh` **installs into**, yet `~/.npmrc` never sets it | 30 packages |
| `~/.local/lib/node_modules` | ad-hoc third location | `gitnexus` |

Because the installed prefix and the intended prefix disagree, `npm install -g` and `npm outdated -g --prefix ~/.npm-global` operate on **different trees**. Six tools are additionally symlinked from npm locations into `/opt/homebrew/bin` (`codex`, `qoder`, `qodercli`, `prime-agent`, plus `npm`/`npx`), which is why they *appear* Homebrew-managed while actually being npm installs.

### Homebrew availability research

Whether a CLI *should* move to Homebrew depends on whether Homebrew actually ships that tool:

| CLI | Homebrew asset | Currently installed as |
|---|---|---|
| `claude` | cask `claude` | external download (`~/.local/bin/claude`) |
| `codex` | cask `codex` | npm-global, symlinked into `/opt/homebrew/bin` |
| `cursor-agent` | cask `cursor-cli` | **brew-managed ✓** |
| `droid` | cask `droid` | **brew-managed ✓** |
| `opencode` | formula `opencode` (third-party tap; shadows `homebrew/core`) | **brew-managed ✓** |
| `hermes-agent` | formula `hermes-agent` (exists) | external install at `~/.hermes/hermes-agent` |
| `buzz` | cask `buzz` | external download |
| `Claude-Fable` | **none** | npm-global, symlinked into `/opt/homebrew/bin` |
| `kilo`, `auggie`, `cce`, `pi`, `prime-agent`, `happy` | **none** | npm-global / external |
| `Anthropic` | formula `Anthropic` is a **different tool** (a regex library, deprecated 2027-01-11) | external download (`~/.grok/downloads/…`) |

Two name collisions must be recorded rather than assumed away: Homebrew's `opencode` formula comes from a third-party tap and *shadows* `homebrew/core/opencode`, and Homebrew's `Anthropic` formula is unrelated to the installed installer, whose asset is actually named `grok-build`.

## What Changes

- Introduce a `workstation-toolchain-inventory` capability governing install locations: a single declared npm global prefix, the authoritative-location rule per tool, duplication detection, and the requirement that a preferred package-manager source be used where one exists.
- Introduce a `snapshot-store-growth-bounds` capability governing bounded growth of Git-backed snapshot stores: declared size ceilings, repack obligations, integrity/recoverability requirements, and scheduled enforcement by an owner command.
- Introduce an `agent-cli-inventory-coverage` capability governing the declared covered set: every installed CLI MUST be covered with a scriptable update verb or explicitly declared uncovered, and undeclared installations MUST be reported without being updated.
- MODIFY `workstation-storage-hygiene` to classify tool-installation duplication and Git snapshot-store object accumulation as candidate categories with owning-tool commands.
- No CLI is removed: all installed CLIs remain available. The change governs *where* they live and *how* they are declared — it does not decommission any tool.
- No BREAKING changes.

## Capabilities

### New Capabilities
- `workstation-toolchain-inventory`: defines the sanctioned install locations, the single declared npm global prefix, the preferred-package-manager rule (Homebrew where Homebrew ships the tool, including third-party taps and casks), the authoritative-location rule per tool, name-collision recording, and the requirement that duplication be reported with verification before it is reclaimable.
- `snapshot-store-growth-bounds`: defines size ceilings, repack obligations, integrity and recoverability requirements, and scheduled enforcement for Git-backed snapshot stores.
- `agent-cli-inventory-coverage`: defines the requirement that the agent-CLI covered set and the installed set be reconciled, with undeclared installations reported rather than silently updated or ignored.

### Modified Capabilities
- `workstation-storage-hygiene`: adds tool-installation duplication and Git loose-object accumulation to the cleanup-candidate classification, each with its owning-tool command and safety classification.

## Impact

- `~/.npmrc` — must declare the chosen npm global prefix so `npm prefix` stops disagreeing with the prefix the daily script installs into
- `~/Developer/scripts/workstation-daily-update.sh` (and its recorded mirror) — agent-CLI coverage reconciliation plus read-only snapshot-growth and duplication reporting stages
- `~/.agentmemory/snapshots/.git` — governed by the new growth bounds (not modified by this proposal)
- `~/.npm-global`, `~/.local/lib/node_modules`, `~/.local/share/home-toolchain`, `/opt/homebrew/lib` — install locations brought under one rule
- `/opt/homebrew/bin` — the six npm-origin symlinks recorded as npm installs, not Homebrew installs
- `platform/openspec-store` — three new capability specs, one modified spec, change artifacts
