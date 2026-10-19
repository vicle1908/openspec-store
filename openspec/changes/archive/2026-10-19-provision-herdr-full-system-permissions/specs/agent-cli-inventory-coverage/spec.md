# agent-cli-inventory-coverage Spec Delta

## ADDED Requirements

### Requirement: Herdr registration in declared uncovered Homebrew-governed agent CLI roster

The agent CLI coverage reconciler, updater registry, and daily maintenance runner SHALL register `herdr` in the declared uncovered Homebrew-governed set so Stage 1 Homebrew formula updates govern `herdr` without undeclared-CLI errors.

#### Scenario: Herdr is reported as declared uncovered under Homebrew formula authority
- **WHEN** `python3 scripts/reconcile-agent-cli-coverage.py --json` executes on the workstation
- **THEN** `herdr` (`/opt/homebrew/bin/herdr`, formula `herdr`) SHALL appear in the declared uncovered set (`uncovered_declared`, delegating to `brew`) with zero undeclared CLI findings

#### Scenario: Daily maintenance script and updater registry share identical uncovered roster including Herdr
- **WHEN** `scripts/toolchain_updater_registry.py` and `AGENT_CLI_KNOWN_UNCOVERED` in `scripts/workstation-daily-update.sh` (and its `platform/openspec-store/scripts/workstation-daily-update.sh` mirror) are inspected
- **THEN** `("herdr", "brew-formula")` SHALL be declared in `SUPPORTED_UPDATER_REGISTRY` with `status="uncovered_declared"` and `delegating_to="brew"`
- **AND** `AGENT_CLI_KNOWN_UNCOVERED` SHALL include `herdr` while maintaining byte-for-byte SHA-256 parity across both script paths
