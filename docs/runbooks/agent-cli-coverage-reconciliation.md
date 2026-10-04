# Runbook: Agent CLI Coverage Reconciliation & Management

## Overview
The workstation maintenance pipeline enforces explicit coverage declarations for all installed AI coding agent CLIs. Tools are never silently updated or uninstalled; every installed CLI is either declared as covered with an automated update verb, or explicitly declared as uncovered.

## 1. Active Roster and Classification
- **Covered (7)**: `claude`, `codex`, `opencode`, `kilo`, `auggie`, `qoder`, `pi` (updated via scriptable verbs under timeout fences).
- **Uncovered Declared (9)**:
  - Package manager / Cask managed: `droid`, `goose`, `cursor-agent`, `buzz`.
  - Upstream release channel / Standalone: `grok`, `prime-agent`, `hermes-agent`, `happy`, `cce`.

## 2. Reconciliation Command
To audit coverage and verify zero undeclared tools:
```bash
python3 scripts/reconcile-agent-cli-coverage.py
```
For machine-readable JSON:
```bash
python3 scripts/reconcile-agent-cli-coverage.py --json
```

## 3. Procedure for Adding an Agent CLI
1. Detect binary on `$PATH` via `which <agent>`.
2. Determine installation source:
   - If Homebrew formula or cask: manage via Homebrew (Stage 1), declare in `AGENT_CLI_KNOWN_UNCOVERED`.
   - If standalone CLI with scriptable, non-interactive updater: declare in `AGENT_CLI_COVERED` with update command.
   - If manual or wrapped CLI: declare in `AGENT_CLI_KNOWN_UNCOVERED`.
3. Verify clean reconciliation: `python3 scripts/reconcile-agent-cli-coverage.py` must report `undeclared_count: 0`.
