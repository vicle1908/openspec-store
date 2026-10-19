# workstation-toolchain-inventory Specification Delta

## MODIFIED Requirements

### Requirement: Sanctioned install locations

Workstation tooling SHALL be installed into one of the sanctioned locations only: the declared
npm global prefix, the relocated toolbelt `~/.local/share/home-toolchain`, the system
package-manager prefix, or a language-specific tool manager under `~/.local/share`. A tool
SHALL NOT be installed into an unscoped ad-hoc directory under `$HOME`, including `~/node_modules`
or `~/.local/lib/node_modules`.

#### Scenario: Tool installed into an unsanctioned location

- **WHEN** a node package is installed into a directory that is not a sanctioned location, such
  as `~/.local/lib/node_modules` or `~/node_modules`
- **THEN** the inventory SHALL report it as an unsanctioned installation
- **AND** the report SHALL identify the sanctioned location that would own it instead

#### Scenario: All installations are sanctioned

- **WHEN** every installed copy of every inventoried tool resolves into one of the sanctioned
  locations and no `~/node_modules` or `~/.local/lib/node_modules` exists
- **THEN** the inventory SHALL report no unsanctioned installations

### Requirement: The declared npm global prefix is authoritative and singular

The workstation SHALL declare exactly one npm global prefix, the prefix npm reports for
`npm config get prefix` SHALL equal the prefix the maintenance pipeline installs globals into,
and `$HOME` SHALL NOT contain a `package.json`, lockfile (`package-lock.json`, `pnpm-lock.yaml`,
`pnpm-workspace.yaml`, `bun.lock`, `bun.lockb`, `yarn.lock`), or `node_modules` directory that
hijacks `npm prefix` resolution from `~/Developer`. Where these disagree or `$HOME` hijacks
local prefix resolution, the inventory SHALL report the defect rather than treating the state
as reconciled.

#### Scenario: npm's effective prefix disagrees with the intended prefix

- **WHEN** npm's reported global prefix differs from the prefix the maintenance pipeline passes
  to `npm install -g`, as when `node` is installed by the system package manager and sets npm's
  default prefix while the pipeline targets a user prefix
- **THEN** the inventory SHALL report both prefixes, identify which one `npm install -g` without
  `--prefix` would use, and identify which one the pipeline uses
- **AND** it SHALL classify the split as a defect to be reconciled by declaration

#### Scenario: Home directory artifacts hijack local npm prefix resolution

- **WHEN** `$HOME` contains `node_modules`, `package.json`, `package-lock.json`, `pnpm-lock.yaml`,
  `pnpm-workspace.yaml`, or `bun.lock`, causing `npm prefix` executed in `~/Developer` to resolve
  to `$HOME`
- **THEN** `inventory-workstation-toolchain.py` SHALL report `home_prefix_hijacked: true` and
  list the offending `$HOME` artifacts in `prefix_reconciliation`
- **AND** it SHALL classify the prefix reconciliation status as `split_detected`

#### Scenario: Prefixes agree

- **WHEN** npm's reported global prefix equals the prefix the maintenance pipeline installs into
  and equals the declared prefix, no package-manager artifacts or `node_modules` exist directly
  in `$HOME`, and `npm prefix` in `~/Developer` resolves to `~/Developer`
- **THEN** the inventory SHALL report the prefix as reconciled (`home_prefix_hijacked: false`)
- **AND** no prefix defect SHALL be raised
