# Runbook: Workstation Toolchain Inventory, Prefix Reconciliation, and Duplication Governance

## Overview
Workstation development tooling is installed across system package managers (Homebrew), user npm prefixes (`~/.npm-global`), language tool managers, and the isolated home toolbelt (`~/.local/share/home-toolchain`).

## 1. Sanctioned Install Locations
Declared in `config/workstation-sanctioned-locations.tsv`:
- `~/.npm-global`: The declared npm global prefix for workstation CLIs.
- `~/.local/share/home-toolchain`: The isolated package manifest for toolchain CLIs (`bru`, `newman`, etc.).
- `/opt/homebrew`: The system package manager prefix.
- `~/.local/share`: Language and runtime tool managers (`uv`, `mise`, etc.).

Any installation in an unscoped directory (such as `~/.local/lib/node_modules`) is classified as unsanctioned.

## 2. Declared npm Global Prefix & Reconciliation
Because `node` is installed via Homebrew, npm's built-in default prefix is `/opt/homebrew`. If `~/.npmrc` does not explicitly set `prefix`, `npm install -g` places packages into `/opt/homebrew/lib/node_modules`, while maintenance scripts installing with `--prefix ~/.npm-global` place them into `~/.npm-global`.

- **Reconciliation Command**:
  ```bash
  python3 scripts/inventory-workstation-toolchain.py
  ```
- **Declarative Fix**: Add `prefix = /Users/androidteam/.npm-global` to `~/.npmrc`.
- **Rollback**: Remove the `prefix` line from `~/.npmrc`.

## 3. Preferred Sources and Name Collisions
Where Homebrew provides a formula or cask, that channel is preferred over unsigned downloads or ad-hoc wrappers:
- `codex` -> cask `codex` (also documented via npm `@openai/codex`)
- `claude` -> native standalone installer or cask `claude-code` (cask `claude` installs the desktop GUI app `/Applications/Claude.app`, not the CLI)
- `cursor-agent` -> cask `cursor-cli`
- `hermes-agent` -> formula `hermes-agent` (or git checkout under `~/.hermes/hermes-agent`)
- `buzz` -> cask `buzz`
- `grok` -> cask `grok-build` (Homebrew formula `grok` is an unrelated deprecated regex tool; must NOT be used)
- `opencode` -> formula `opencode` (from third-party tap; shadows `homebrew/core/opencode`)
- `prime-agent` -> none (official R2 Mach-O binary channel)

## 4. Duplication & Reclamation Safety
Duplication is reported with measured sizes. Reclamation is **strictly gated** on explicit authorization and must be verified by post-reclamation execution checks (`gitnexus --version`, `bru --version`). Direct deletion by duplication detection alone is prohibited.

## 5. Version Authority Model and Actual Writers

Each installed development tool has **exactly one elected version authority**: the single mechanism permitted to advance or pin the installed version. The version authority model enforces the distinction between an updater dispatch entrypoint (how a user or script invokes an update) and the actual version writer (the process or package manager that physically mutates the installation).

1. **Tool-Native Authority**:
   Tools that manage their own versioning via native self-updaters (e.g. `claude update`, `auggie update --skip-confirmation`, `hermes update`) elect `native` authority. The tool itself (or internal updater script) acts as the version writer.
2. **Package Manager Authority**:
   Tools installed and managed by system or ecosystem package managers without self-updating commands (e.g. `goose`, `newman` under Homebrew formulae; `droid`, `cursor-agent`, `buzz` under Homebrew casks; `happy` under npm-global; `bru` under home-toolchain) elect their package manager (`brew-formula`, `brew-cask`, `npm-global`, `home-toolchain`) as the version authority.
3. **Compatible Manager Delegation**:
   When a tool provides a native update command that inspects its runtime environment and delegates execution to its installing package manager (e.g. `opencode upgrade` delegating to `brew upgrade opencode`, or `grok` with `installer = "brew"` delegating to Homebrew cask `grok-build`), the package manager remains the single actual version writer. Compatible delegation is treated as an authorized entrypoint to that manager and produces **no authority conflict**.
4. **Bundle `auto_updates` Semantics**:
   Homebrew cask receipts declaring `auto_updates: true` indicate internal bundle self-updating capability. This flag disables automatic bundle version comparison during routine updates, but is not an exclusive version-control waiver (greedy upgrade flags permit managing them). Asset identity must not be conflated: cask `claude` installs the desktop GUI app (`/Applications/Claude.app`), whereas the CLI is managed independently via native download (`~/.local/share/claude/versions/...`) or cask `claude-code`.
5. **Unknown Authority Gating**:
   When available evidence is insufficient to verify active provenance, updater dispatch, or owning asset (e.g. `cce` as an ad-hoc standalone binary in `~/.local/bin/cce` without package manager receipt or updater subcommand), authority is recorded as `unknown` with explicit evidence gaps. Automated update mutations for that tool are strictly gated until resolved.

## 6. Updater Dispatch Classification

Updaters are classified into four distinct dispatch types:
- **`native`**: The tool directly mutates its own installation (e.g. `claude`, `auggie`, `hermes-agent`, `qoder`).
- **`delegating`**: The tool provides an update verb but verifies its installation context and invokes its owning package manager (e.g. `opencode` -> `brew`, `grok` -> `brew`).
- **`none`**: The tool provides no scriptable self-update subcommand and relies solely on package manager upgrade cycles or manual vendor updates (e.g. `droid`, `goose`, `cursor-agent`, `buzz`, `happy`, `kilo`, `newman`, `bru`).
- **`unknown`**: Provenance or update capability is ambiguous or undocumented (e.g. `cce`).

## 7. Prefix Target Alignment & Misalignment Risk

A tool's effective write target (evaluated across environment variables, package receipts, and updater configuration) must align with the active installation root resolved on `$PATH`.

- **Target-Misalignment Risk**:
  Occurs when an update action targets a directory or prefix different from the active installation root.
  - *Example*: The active `codex` executable resolves to `/opt/homebrew/lib/node_modules/@openai/codex/bin/codex.js` (installed under `/opt/homebrew`), while the workstation's declared npm global prefix is `~/.npm-global`. Invoking `codex update` or `npm install -g @openai/codex` without prefix alignment targets `~/.npm-global/lib/node_modules/@openai/codex`, leaving the active binary on `$PATH` stale and unupdated.
  - *Mitigation*: Run `npm install -g --prefix /opt/homebrew @openai/codex`, or migrate the active installation root to align with `~/.npm-global`.
- **Orthogonal Location Findings**:
  Installations in unsanctioned or unscoped directories (such as `gitnexus` in `~/.local/lib/node_modules` or `qoder` in `~/.qoder/entry/qoder`) are reported as orthogonal findings without masking version authority.

## 8. Documented Installation Channels & Selection Precedence

Official documentation may define multiple supported installation channels for a given tool:
- `codex`: npm (`@openai/codex`) and Homebrew cask (`codex`).
- `claude`: native standalone installer (`curl -fsSL https://code.claude.com/install.sh`), Homebrew cask (`claude-code`), and npm (`@anthropic-ai/claude-code`).
- `opencode`: Homebrew formula (`opencode` from anomalyco tap) and npm (`opencode`).

Channel selection is resolved by **active installation provenance** rather than blanket preference. The inventory records all documented channels, identifies the active channel matching the realpath on `$PATH`, and only reports an installation as bypassing a preferred source if it resides in an unsanctioned wrapper or unsigned download when an official package manager channel is available.

## 9. Version Authority & Drift Reconciliation Audit

Run the read-only workstation toolchain inventory:
```bash
python3 platform/openspec-store/scripts/inventory-workstation-toolchain.py
```

Machine-readable JSON output:
```bash
python3 platform/openspec-store/scripts/inventory-workstation-toolchain.py --json
```

- **Reconciled Status**: Reports `Status:                      RECONCILED` when all tools have aligned single writers and no conflicting uncoordinated update paths.
- **Drift Detected Status**: Reports `Status:                      DRIFT_DETECTED` when uncoordinated independent writers, incompatible write targets, or target prefix misalignments are detected.
