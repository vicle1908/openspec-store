# Proposal: Upgrade Outdated Homebrew Casks and Remote Agent Releases

## Why
A comprehensive audit against remote upstream channels revealed several developer tools, Homebrew casks, and Git-tracked agent repositories on the workstation that have newer releases available:
- Homebrew casks: `copilot-cli` (1.0.88 -> 1.0.91), `droid` (0.227.0 -> 0.233.0), `zed` (1.21.0 -> 1.22.0), `gcloud-cli` (586.0.0 -> 587.0.0), `postman-cli` (1.65.0 -> 1.69.0), `google-drive` (131.0.2 -> 132.0.0), `lark` (8.0.3 -> 8.1.22), and `teamviewer` (15.81.6 -> 15.82.6).
- Git repository: `platform/prime-agent` on `main` is behind `origin/main` by 1 upstream commit (`c24ac227f keep the daemon running when a client closes (#3345)`).

Upgrading these components to their latest upstream releases ensures developer environment security, eliminates client-detach bugs, and keeps desktop agent binaries in lockstep with vendor releases.

## What Changes
- **Homebrew Cask Modernization**:
  - Upgrade outdated CLI and editor casks via `brew upgrade --cask`: `copilot-cli`, `droid`, `zed`, `gcloud-cli`, `postman-cli`.
  - Upgrade remaining background productivity casks: `google-drive`, `lark`, `teamviewer`.
- **Prime Agent Git Repository Upstream Fast-Forward**:
  - Fast-forward `main` in `platform/prime-agent` to include commit `c24ac227f` from `origin/main`.
  - Verify working tree cleanliness and test launcher environment pins.
- **Verification**:
  - Verify upgraded binaries on `$PATH`: `copilot --version`, `droid --version`, `zed --version`, `gcloud --version`, `postman --version`.
  - Verify `prime-agent` commit log.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `ecosystem-tooling-and-skills-upgrade`: Extend the cask modernization scenario to verify that upgraded casks (`copilot-cli@1.0.91`, `droid@0.233.0`, `zed@1.22.0`, `gcloud-cli@587.0.0`, `postman-cli@1.69.0`) and repository checkouts match current upstream remote heads.

## Non-Goals
- Downgrading any package.
- Modifying unmanaged third-party binary paths outside Homebrew.

## Affected Ownership Boundaries
- Homebrew Cask Management: `/opt/homebrew/Caskroom/`
- Platform Repositories: `platform/prime-agent`
