# Spec Delta: ecosystem-tooling-and-skills-upgrade

## MODIFIED Requirements

### Requirement: Desktop application and Homebrew cask modernization

The system SHALL upgrade identified outdated Homebrew casks without disruption to background services, and verify that container runtimes and network daemons remain operational post-upgrade.

#### Scenario: Homebrew casks are upgraded and verified
- **WHEN** outdated casks (`copilot-cli`, `droid`, `zed`, `gcloud-cli`, `postman-cli`, `google-drive`, `lark`, `teamviewer`) are upgraded via `brew upgrade --cask`
- **THEN** the system SHALL invoke targeted cask upgrade commands
- **AND** `copilot-cli` SHALL report version 1.0.91 or higher
- **AND** `droid` SHALL report version 0.233.0 or higher
- **AND** `zed` SHALL report version 1.22.0 or higher
- **AND** `gcloud-cli` SHALL report version 587.0.0 or higher
- **AND** `postman-cli` SHALL report version 1.69.0 or higher
- **AND** `docker ps` SHALL respond and existing services remain operational.

## ADDED Requirements

### Requirement: Upstream Git Agent Repository Fast-Forward Alignment
Tracked core agent repositories in `platform/` (`platform/prime-agent`) SHALL track their canonical remote `origin/main` branch without unmerged divergence, fast-forwarding upstream release and bugfix commits while maintaining working tree cleanliness.

#### Scenario: Prime agent repository tracks origin/main
- **WHEN** `git -C platform/prime-agent fetch origin` reports upstream commits on `origin/main`
- **THEN** the branch SHALL be fast-forwarded to `origin/main`
- **AND** `git status` SHALL report working tree clean and up to date with `origin/main`
