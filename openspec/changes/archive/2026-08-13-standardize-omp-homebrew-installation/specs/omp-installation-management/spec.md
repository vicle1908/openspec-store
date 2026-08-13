## ADDED Requirements

### Requirement: Canonical omp binary resolution

A fresh login shell SHALL resolve exactly one omp binary path.
The canonical path SHALL be `/opt/homebrew/bin/omp`.
No Bun-managed omp path SHALL appear in `which -a omp` output.

#### Scenario: single omp binary in fresh shell

Given the Bun-managed omp packages have been removed
When a fresh login shell runs `command -v omp`
Then the output SHALL be `/opt/homebrew/bin/omp`.

#### Scenario: no Bun-managed omp in PATH

Given the Bun-managed omp packages have been removed
When a fresh login shell runs `which -a omp`
Then the output SHALL contain exactly one path.

### Requirement: Homebrew omp functional acceptance

Homebrew omp SHALL pass the live default-role smoke test.

#### Scenario: default role resolves through Homebrew omp

When a fresh login shell runs `omp --no-session -p "reply only: pong"`
Then the response SHALL contain `pong` and exit code SHALL be 0.

### Requirement: Unrelated Bun packages preserved

Removing the three `@oh-my-pi/*` packages SHALL NOT remove or
break any unrelated Bun-installed package.

#### Scenario: gitnexus remains installed

Given the three `@oh-my-pi/*` packages have been removed
When `bun pm ls -g` is inspected
Then `gitnexus` SHALL still appear.

#### Scenario: pyright remains installed

Given the three `@oh-my-pi/*` packages have been removed
When the pyright binary is located
Then it SHALL exist.

### Requirement: omp configuration untouched

The removal SHALL NOT modify `~/.omp/agent/models.yml` or
`~/.omp/agent/config.yml`.

#### Scenario: live hashes unchanged

Given the removal has completed
When `models.yml` hash is checked
Then it SHALL equal the pre-removal baseline.

#### Scenario: live role map unchanged

Given the removal has completed
When `config.yml` is inspected programmatically
Then `modelRoles` SHALL be identical to pre-removal state.
