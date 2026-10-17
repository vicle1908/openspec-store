# agent-cli-inventory-coverage Specification Delta

## ADDED Requirements

### Requirement: Primary DBOS runner and fallback Bash runner share an identical covered-agent roster

`shb-schedule` (`workstation_update.py`), `workstation-daily-update.sh`, `toolchain_updater_registry.py`, and `reconcile-agent-cli-coverage.py` SHALL enforce the exact same covered and declared-uncovered agent CLI rosters so scheduled `apply` runs and `--check` audits never diverge on which agent CLIs are updated in the agent-CLI stage.

#### Scenario: Unsupported Kilo native updater is excluded from DBOS agent stage
- **WHEN** `step_agent_cli_update` in `workstation_update.py` executes
- **THEN** it SHALL NOT invoke `kilo update` because `kilo` is classified as `uncovered_declared` in `toolchain_updater_registry.py`
- **AND** `kimi` (`kimi update`), `claude`, `codex`, `opencode`, `auggie`, `qoder`, and `pi` SHALL be aligned across both `workstation_update.py` and `workstation-daily-update.sh`

#### Scenario: Qwen Code is registered in the declared uncovered Homebrew-governed set
- **WHEN** `reconcile-agent-cli-coverage.py --json` inspects installed coding agent CLIs
- **THEN** `qwen` (`/opt/homebrew/bin/qwen`, formula `qwen-code`) SHALL be listed in the declared uncovered set (governed by Stage 1 Homebrew formula updates) with zero undeclared CLI findings
