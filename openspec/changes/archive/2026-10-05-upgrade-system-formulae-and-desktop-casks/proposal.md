# Proposal: Upgrade System Formulae and Desktop Application Casks

## Why
While developer CLI casks and core agent tools were upgraded in preceding changes, workstation maintenance checks revealed remaining outdated system formulae (`node@26.10.0_1` -> `26.10.0_2`, `simdjson@4.6.11` -> `5.0.0`), desktop casks (`google-drive@131.0.2` -> `132.0.0`, `lark@8.0.3` -> `8.1.22`, `teamviewer@15.81.6` -> `15.82.6`), and an unmerged upstream commit history on `~/.hermes/hermes-agent` (1,217 commits behind `origin/main`).

Upgrading these components aligns the workstation with upstream security patches, ensures Node.js runtime stability, and keeps desktop application bundles in sync with vendor releases.

## What Changes
- **Homebrew Formulae Upgrades**:
  - Upgrade `node` to `26.10.0_2` (revision bump).
  - Upgrade `simdjson` to `5.0.0` (major version bump).
- **Homebrew Desktop Casks Upgrades**:
  - Upgrade `google-drive` to `132.0.0`.
  - Upgrade `lark` to `8.1.22,9dd05af0`.
  - Upgrade `teamviewer` to `15.82.6`.
- **Hermes Agent Git Fast-Forward**:
  - Fast-forward merge `~/.hermes/hermes-agent` to `origin/main` (commit `8b66a51036`).
  - Verify working tree cleanliness and test hermes CLI execution.
- **Verification**:
  - Verify `node --version`, `simdjson` headers/libs, `docker ps`, and `hermes --version`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `ecosystem-tooling-and-skills-upgrade`: Extend the formula and cask modernization requirements to encompass Node.js system runtime updates, simdjson major version upgrades, and desktop application cask tracking.

## Non-Goals
- Modifying custom local configuration files (`~/.hermes/`).
- Force-updating uninstalled casks.

## Affected Ownership Boundaries
- Homebrew Formulae: `/opt/homebrew/Cellar/node`, `/opt/homebrew/Cellar/simdjson`
- Homebrew Casks: `/opt/homebrew/Caskroom/`
- Hermes Runtime: `~/.hermes/hermes-agent`
