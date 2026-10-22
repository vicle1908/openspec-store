# omp-installation-management Specification Delta

## MODIFIED Requirements

### Requirement: Canonical omp binary resolution

A fresh login shell SHALL resolve exactly one `omp` binary path at `/opt/homebrew/bin/omp`, no Bun-managed or npm-managed `omp` file or dangling symlink SHALL exist at `~/.bun/bin/omp` or `~/.npm-global/bin/omp`, and `omp --version` SHALL report the version matching the installed Homebrew formula.

#### Scenario: single omp binary in fresh shell
- **WHEN** a fresh login shell runs `command -v omp` after Bun-managed `omp` packages have been removed
- **THEN** the output SHALL be `/opt/homebrew/bin/omp`

#### Scenario: no Bun-managed omp in PATH
- **WHEN** a fresh login shell runs `which -a omp` after Bun-managed `omp` packages have been removed
- **THEN** the output SHALL contain exactly one path (`/opt/homebrew/bin/omp`)

#### Scenario: no dangling or active omp symlink in Bun or npm global bin directories
- **WHEN** `~/.bun/bin/omp` and `~/.npm-global/bin/omp` are inspected with symlink-aware checks (`test ! -L ~/.bun/bin/omp && test ! -e ~/.bun/bin/omp`)
- **THEN** neither an executable nor a dangling symlink SHALL exist at either shadow path

#### Scenario: version matches Homebrew formula
- **WHEN** a fresh login shell runs `omp --version`
- **THEN** the reported version SHALL match the version installed by Homebrew (`can1357/tap/omp`)

### Requirement: Unrelated Bun packages preserved

Removing `@oh-my-pi/*` artifacts and dangling `~/.bun/bin/omp` symlinks SHALL NOT break Bun global package inspection (`bun pm ls -g`) or remove unrelated tools in sanctioned prefixes (`gitnexus` in `~/.npm-global` and `pyright` in `~/.local/share/home-toolchain`).

#### Scenario: gitnexus remains installed
- **WHEN** `which gitnexus` is inspected after the `@oh-my-pi/*` packages and `~/.bun/bin/omp` have been removed
- **THEN** `gitnexus` (`~/.npm-global/bin/gitnexus`) SHALL still exist and execute cleanly

#### Scenario: pyright remains installed
- **WHEN** the `pyright` binary (`/opt/homebrew/bin/pyright` and `~/.local/share/home-toolchain/node_modules/.bin/pyright`) is located after the `@oh-my-pi/*` packages and `~/.bun/bin/omp` have been removed
- **THEN** it SHALL exist

#### Scenario: bun global package listing exits cleanly with initialized lockfile
- **WHEN** `bun pm ls -g` is executed against `~/.bun/install/global`
- **THEN** `~/.bun/install/global/bun.lock` SHALL be present and `bun pm ls -g` SHALL exit with status `0` without `missing lockfile` errors
