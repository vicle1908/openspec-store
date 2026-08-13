## MODIFIED Requirements

### Requirement: Canonical omp binary resolution

A fresh login shell SHALL resolve exactly one omp binary path.
The canonical path SHALL be `/opt/homebrew/bin/omp`.
No Bun-managed omp path SHALL appear in `which -a omp` output.
`omp --version` SHALL report the version matching the installed Homebrew formula.

#### Scenario: single omp binary in fresh shell

Given the Bun-managed omp packages have been removed
When a fresh login shell runs `command -v omp`
Then the output SHALL be `/opt/homebrew/bin/omp`.

#### Scenario: no Bun-managed omp in PATH

Given the Bun-managed omp packages have been removed
When a fresh login shell runs `which -a omp`
Then the output SHALL contain exactly one path.

#### Scenario: version matches Homebrew formula

When a fresh login shell runs `omp --version`
Then the reported version SHALL match the version installed by Homebrew.
