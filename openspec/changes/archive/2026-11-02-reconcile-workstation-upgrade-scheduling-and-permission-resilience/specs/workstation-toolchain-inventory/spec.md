# workstation-toolchain-inventory Delta Specification

## ADDED Requirements

### Requirement: Automated cask upgrade inspection SHALL support greedy evaluation with process safety gating

The automated workstation maintenance pipeline and toolchain inventory SHALL evaluate auto-updating Homebrew casks via `--greedy` inspection, while safeguarding running applications through process presence verification before invoking cask upgrade routines.

#### Scenario: Greedy cask discovery with running application deferral
- **WHEN** `shb-schedule` or `workstation-daily-update.sh` executes the Homebrew maintenance step
- **THEN** it SHALL query `brew outdated --greedy --json=v2` to identify outdated casks marked with `auto_updates: true`
- **AND** for each outdated cask, it SHALL check active processes defined in `CASK_PROCESS_NAMES`
- **AND** if any matching process is active, the cask SHALL be skipped and recorded in `casks_skipped_running`
- **AND** if no matching process is active, the cask SHALL be upgraded non-interactively via `brew upgrade --cask -- <cask>`

#### Scenario: Docker Desktop coordinated lifecycle upgrade
- **WHEN** `docker-desktop` is identified as outdated and no unmanaged processes block upgrading
- **THEN** registered compose stacks SHALL be drained before cask replacement
- **AND** following successful cask upgrade, `docker-service.sh start` and `docker-service.sh up` SHALL be executed to restore stacks and privileged helpers

### Requirement: Coding agent CLI self-updaters SHALL execute non-interactively

Coding agent CLI tools managed outside Homebrew or npm SHALL execute deterministic, non-interactive self-update routines that apply binary updates directly to user-local execution roots without hanging on interactive prompts or no-op checks.

#### Scenario: Notion CLI non-interactive upgrade
- **WHEN** the scheduled pipeline executes the agent CLI update step for `ntn`
- **THEN** it SHALL execute the official installer script via non-interactive pipe targeting `~/.local/bin/ntn`
- **AND** the command SHALL execute within a time-bounded window without interactive input prompts
