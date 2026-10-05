# Spec Delta: ecosystem-tooling-and-skills-upgrade

## MODIFIED Requirements

### Requirement: Desktop application and Homebrew cask modernization

The system SHALL upgrade identified outdated Homebrew casks without disruption to background services, and verify that container runtimes, node engines, and network daemons remain operational post-upgrade.

#### Scenario: Homebrew casks are upgraded and verified
- **WHEN** outdated casks (`copilot-cli`, `droid`, `zed`, `gcloud-cli`, `postman-cli`, `google-drive`, `lark`, `teamviewer`) and formulae (`node`, `simdjson`) are upgraded via `brew upgrade`
- **THEN** the system SHALL invoke targeted upgrade commands
- **AND** `node` SHALL report version 26.10.0 (revision 2)
- **AND** `simdjson` SHALL be linked at version 5.0.0
- **AND** `copilot-cli` SHALL report version 1.0.91 or higher
- **AND** `droid` SHALL report version 0.233.0 or higher
- **AND** `zed` SHALL report version 1.22.0 or higher
- **AND** `gcloud-cli` SHALL report version 587.0.0 or higher
- **AND** `postman-cli` SHALL report version 1.69.0 or higher
- **AND** `google-drive` SHALL report version 132.0.0 or higher
- **AND** `lark` SHALL report version 8.1.22 or higher
- **AND** `teamviewer` SHALL report version 15.82.6 or higher
- **AND** `docker ps` SHALL respond and existing container services remain operational.

## ADDED Requirements

### Requirement: Upstream Hermes Agent Fast-Forward Alignment
The local installation of Hermes Agent (`~/.hermes/hermes-agent`) SHALL track its canonical remote `origin/main` branch without unmerged divergence, fast-forwarding upstream release and bugfix commits while maintaining working tree cleanliness.

#### Scenario: Hermes agent repository tracks origin/main
- **WHEN** `git -C ~/.hermes/hermes-agent fetch origin` reports upstream commits on `origin/main`
- **THEN** the branch SHALL be fast-forwarded to `origin/main`
- **AND** `git status` SHALL report working tree clean and up to date with `origin/main`
- **AND** `hermes --version` SHALL execute successfully with exit code 0.
