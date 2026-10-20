# Spec Delta

## ADDED Requirements

### Requirement: OMP registration in declared uncovered Homebrew-governed agent CLI roster

The agent CLI coverage reconciler, updater registry, and daily maintenance runner SHALL register `omp` in the declared uncovered Homebrew-governed set and verify its `SUPPORTED_UPDATER_REGISTRY` declaration so Stage 1 Homebrew formula updates govern `/opt/homebrew/bin/omp` without undeclared-CLI errors.

#### Scenario: OMP is reported as declared uncovered under Homebrew formula authority
- **WHEN** `python3 scripts/reconcile-agent-cli-coverage.py --json` executes on the workstation
- **THEN** `omp` (`/opt/homebrew/bin/omp`, formula `can1357/tap/omp`) SHALL appear in the declared uncovered set (`uncovered_declared`) with `evaluate_update_path()` verifying `decl.status == "uncovered_declared"` and reporting `delegating_to=brew` with zero undeclared CLI findings

#### Scenario: Daily maintenance script and updater registry share identical uncovered roster including OMP
- **WHEN** `scripts/toolchain_updater_registry.py` and `AGENT_CLI_KNOWN_UNCOVERED` in `scripts/workstation-daily-update.sh` (and its `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` mirror) are inspected
- **THEN** `("omp", "brew-formula")` SHALL be declared in `SUPPORTED_UPDATER_REGISTRY` with `status="uncovered_declared"` and `delegating_to="brew"`
- **AND** `AGENT_CLI_KNOWN_UNCOVERED` SHALL include `omp` while maintaining byte-for-byte SHA-256 parity across both script paths
