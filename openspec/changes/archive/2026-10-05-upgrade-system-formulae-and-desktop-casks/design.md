# Design: Upgrade System Formulae and Desktop Application Casks

## Context
See `proposal.md`. A comprehensive inspection of system-wide packages identified outdated Homebrew formulae (`node`, `simdjson`), outdated desktop application casks (`google-drive`, `lark`, `teamviewer`), and an unmerged upstream commit history in `~/.hermes/hermes-agent`.

## Goals / Non-Goals

**Goals:**
- Upgrade `node` to `26.10.0_2` via `brew upgrade --formula node`.
- Upgrade `simdjson` to `5.0.0` via `brew upgrade --formula simdjson`.
- Upgrade desktop application casks: `google-drive@132.0.0`, `lark@8.1.22`, `teamviewer@15.82.6` via `brew upgrade --cask`.
- Fast-forward merge `~/.hermes/hermes-agent` to `origin/main` (commit `8b66a51036`).
- Verify CLI execution and background service stability.

**Non-Goals:**
- Modifying custom local configuration files (`~/.hermes/`).
- Force-updating uninstalled casks.

## Decisions

### Decision 1: Upgrade formulae before casks
- `node` is the core execution runtime for several developer tools and build pipelines. Upgrading formulae first ensures shared libraries (`simdjson`, `node`) are properly linked in `/opt/homebrew` before desktop application bundles are updated.

### Decision 2: Fast-forward git merge for hermes-agent
- `~/.hermes/hermes-agent` is on branch `main` with a clean working tree and ancestry verified (`git merge-base --is-ancestor HEAD origin/main`). Running `git merge origin/main --ff-only` applies upstream changes cleanly without merge commits or conflicts.
