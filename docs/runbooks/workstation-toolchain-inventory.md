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
- `codex` -> cask `codex`
- `claude` -> cask `claude`
- `cursor-agent` -> cask `cursor-cli`
- `hermes-agent` -> formula `hermes-agent`
- `buzz` -> cask `buzz`
- `grok` -> cask `grok-build` (Homebrew formula `grok` is an unrelated deprecated regex tool; must NOT be used)
- `opencode` -> formula `opencode` (from third-party tap; shadows `homebrew/core/opencode`)
- `prime-agent` -> none (official R2 Mach-O binary channel)

## 4. Duplication & Reclamation Safety
Duplication is reported with measured sizes. Reclamation is **strictly gated** on explicit authorization and must be verified by post-reclamation execution checks (`gitnexus --version`, `bru --version`). Direct deletion by duplication detection alone is prohibited.
