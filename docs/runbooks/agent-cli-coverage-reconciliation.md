# Runbook: Agent CLI Coverage Reconciliation & Management

## Overview
The workstation maintenance pipeline enforces explicit coverage declarations for all installed AI coding agent CLIs. Tools are never silently updated or uninstalled; every installed CLI is either declared as covered with an automated update verb, or explicitly declared as uncovered.

## 1. Active Roster and Classification
- **Covered (6)**: `claude`, `codex`, `opencode`, `auggie`, `qoder`, `pi` (updated via scriptable verbs under timeout fences).
- **Uncovered Declared (10)**:
  - Package manager / Cask / npm managed: `droid`, `goose`, `cursor-agent`, `buzz`, `kilo`, `prime-agent`.
  - Upstream release channel / Git / Standalone: `grok`, `hermes-agent`, `happy`, `cce`.

### Classification Categories
1. **`covered`**: Installed agent CLI declared in `AGENT_CLI_COVERED` with a verified automated update path (native self-updater or compatible delegator).
2. **`uncovered_declared`**: Installed agent CLI declared in `AGENT_CLI_KNOWN_UNCOVERED` with an explicit governing channel, package manager ownership, or manual status. Uncovered CLIs are intentionally bypassed during Stage 5 agent CLI updates.
3. **`undeclared`**: Installed agent CLI discovered on `$PATH` but absent from both covered and uncovered lists. This represents an unmanaged tool and triggers a domain finding.

### Active Provenance and Wrapper Resolution
Discovery resolves active binaries through symlinks and shell wrapper scripts rather than relying solely on surface paths:
- **Qoder CLI**: The binary identity is `qoder`. The active binary at `~/.qoder/entry/qoder` is an entry wrapper that routes to `qodercli` (`@qoder-ai/qodercli` bundle under the npm ecosystem). Source classification inspects the underlying package target.
- **Hermes Agent**: Resolves wrapper scripts executing the canonical Git checkout and Python virtual environment (`~/.hermes/hermes-agent/...`).
- **Update Path Evaluation**: Every declared CLI is checked against a conservative supported-updater registry for its active installation source. Unsupported commands or manager mismatches (such as `brew upgrade` for an npm package or arbitrary non-empty commands) fail-closed.
- **Kilo CLI Status**: The obsolete `kilo update` command is eliminated; Kilo is declared as `uncovered_declared` (ecosystem manager `npm`) because its native updater is currently unmanaged/failing locally.
## 2. Reconciliation Command & Options
To audit coverage and verify zero undeclared tools:
```bash
python3 scripts/reconcile-agent-cli-coverage.py
```

For machine-readable JSON:
```bash
python3 scripts/reconcile-agent-cli-coverage.py --json
```

To simulate the initial state where newly detected tools are undeclared:
```bash
python3 scripts/reconcile-agent-cli-coverage.py --simulate-initial
```

### JSON Output Structure
The `--json` mode produces a top-level dictionary containing:
- `declared_covered`: Dictionary mapping covered CLI names to update verbs.
- `declared_uncovered`: List of declared uncovered CLI names.
- `total_installed`: Total count of detected agent CLIs on the workstation.
- `undeclared_count`: Integer count of undeclared CLIs (0 for clean state).
- `lacking_update_path`: List of declared CLIs lacking supported update paths.
- `background_settings`: Non-destructively audited environment variables and configuration files.
- `records`: List of per-tool inventory records including `name`, `binary_path`, `status`, `source_type`, `source_detail`, `update_verb`, `real_path`, `has_update_path`, and `update_path_detail`.

## 3. Exit Code Contract & Measurement Distinction

### Exit Code Specification
- **`0`**: Complete, clean reconciliation audit (`undeclared_count == 0`). All installed agent CLIs are accounted for in either the covered or uncovered lists.
- **`1`**: Complete, valid measurement with domain findings (`undeclared_count > 0`). One or more installed agent CLIs are undeclared. The script emits the contract line:
  ```
    Undeclared Count:       N
  ```
  where `N` is an integer greater than 0.
- **`2`**: Argument parsing error (invalid flags or parameters passed to the CLI).
- **Other Nonzero / Abnormal Termination**: Unhandled Python traceback, process crash, or execution timeout. The contract line `Undeclared Count:` will be absent.

### Domain Findings vs. Measurement Failures
Calling scripts and pipeline runners (such as `workstation-daily-update.sh`) must distinguish valid domain findings from measurement failures:
- **Domain Finding (exit 1 with contract line)**: When `reconcile-agent-cli-coverage.py` exits with code 1 and prints `Undeclared Count:       N`, the measurement succeeded. The finding reflects real workstation state (undeclared tools detected). The runner parses `N` into `AGENT_UNDECLARED_COUNT=N` and leaves `AGENT_COVERAGE_MEASURE_FAILED=0`.
- **Measurement Failure (crash, timeout, or missing contract line)**: If the script exits nonzero without printing `Undeclared Count:`, or exits with code 2, or times out under a process fence, the measurement failed. The runner sets `AGENT_COVERAGE_MEASURE_FAILED=1` to record a DEGRADED measurement state without falsely claiming zero findings.

## 4. Background Auto-Update Inspection
The reconciliation script performs a non-destructive, audit-as-is check of native background auto-update settings without modifying user configuration files:
- **Environment Variables**:
  - `DISABLE_AUTOUPDATER`: Disables background auto-updating in tools like Claude Code while keeping manual CLI update commands functional.
  - `DISABLE_UPDATES`: Disables all update mutations under user policy.
  - `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE`: Indicates package-manager managed update delegation.
- **Configuration Files**:
  - `~/.claude/settings.json` and `~/.claude.json`: Audits `autoUpdatesChannel`, `autoUpdates`, and `autoUpdatesProtectedForNative`.
  - `~/.grok/config.toml`: Audits `auto_update` and `installer` settings (verifying non-interactive `auto_update = false` to prevent background updater hangs).

## 5. Procedure for Adding an Agent CLI
1. Detect binary on `$PATH` via `which <agent>`.
2. Determine installation source and underlying target:
   - If Homebrew formula or cask: manage via Homebrew (Stage 1), declare in `AGENT_CLI_KNOWN_UNCOVERED`.
   - If standalone CLI with scriptable, non-interactive updater: declare in `AGENT_CLI_COVERED` with update command.
   - If manual or wrapped CLI: declare in `AGENT_CLI_KNOWN_UNCOVERED`.
3. Verify clean reconciliation: `python3 scripts/reconcile-agent-cli-coverage.py` must report `Undeclared Count:       0` with exit code 0.

## 6. Pipeline Mutation Gating & Roster Normalization

The daily maintenance pipeline (`workstation-daily-update.sh`) enforces strict preflight mutation gating derived from inventory and coverage audits:
1. **Split Homebrew Rosters**: Preflight authority evaluation generates independent `DENY_ROSTER_BREW_FORMULAE` and `DENY_ROSTER_BREW_CASKS`. A drift or misalignment finding on a Homebrew cask does not suppress unrelated formula upgrades, and a formula finding does not suppress unrelated casks.
2. **Normalized Package Filtering**: Outdated package output from `npm outdated -g --parseable` has version suffixes stripped (e.g. `sub(/@[^@]*$/, "", pkg)`) before applying anchored deny filters. This preserves scoped package prefixes (e.g. `@openai/codex`) while ensuring denied packages are reliably excluded from `npm install -g`.
3. **Currency Decoupling**: Successful updater runs where before and after versions match are reported as `(idempotent, currency unverified)`. The status `currency verified` is strictly reserved for tools whose currency was corroborated against an authoritative upstream release channel API.
