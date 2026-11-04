# workstation-toolchain-inventory Delta Specification

## ADDED Requirements

### Requirement: Automated maintenance SHALL upgrade all outdated software packages without passive deferral

Workstation automated maintenance pipelines (`shb_schedule.workflows.workstation_update` and `workstation-daily-update.sh`) SHALL actively upgrade every outdated software package across Homebrew formulae, Homebrew casks, Mac App Store applications, Bun globals, uv tools, npm globals, and coding agent CLIs without deferring or skipping running applications or large software bundles.

#### Scenario: Active graceful teardown and background relaunch for Homebrew casks
- **WHEN** an outdated Homebrew cask has active processes running on the host
- **THEN** the pipeline SHALL gracefully terminate the processes using POSIX signals (`pkill -TERM -x <proc>` with a bounded polling loop, escalating to `pkill -KILL -x` if unresponsive)
- **AND** it SHALL NOT execute AppleEvents (`osascript -e 'quit app ...'`) to prevent `kTCCServiceAppleEvents` privacy prompts
- **AND** it SHALL execute the cask upgrade non-interactively with standard input closed (`stdin=subprocess.DEVNULL`)
- **AND** it SHALL automatically relaunch persistent daemons and background utilities registered in `CASK_RELAUNCH_APPS` in the background (`open -a "<App>" --background`) post-upgrade

#### Scenario: Active graceful teardown and comprehensive upgrade for Mac App Store applications
- **WHEN** one or more Mac App Store applications are reported as outdated by `mas outdated`
- **THEN** the pipeline SHALL NOT passively skip running applications or large application bundles
- **AND** for any running target application, the pipeline SHALL gracefully terminate its process via POSIX signals prior to upgrading
- **AND** the pipeline SHALL invoke `mas upgrade <app_id>` with a generous execution timeout (up to 1800 seconds) to accommodate large bundles such as Xcode
- **AND** the pipeline SHALL automatically relaunch active applications in the background post-upgrade

#### Scenario: Full parity between scheduled DBOS workflows and sequential fallback runner
- **WHEN** maintenance is triggered via the sequential shell runner `workstation-daily-update.sh`
- **THEN** it SHALL execute maintenance across all package managers including Mac App Store applications (`mas outdated` / `mas upgrade`)
- **AND** it SHALL enforce POSIX signal process termination, standard input decoupling (`< /dev/null`), and background relaunching
