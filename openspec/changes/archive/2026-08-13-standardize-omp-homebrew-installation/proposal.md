# Proposal: standardize-omp-homebrew-installation

## Why

Two omp installations coexist on this machine: a Bun/Node wrapper at
`~/.bun/bin/omp` (12 MB, symlinked to `~/node_modules/@oh-my-pi/...`) and a
Homebrew native binary at `/opt/homebrew/bin/omp` (122 MB). Both report
v17.2.15 but have different hashes, different codebases, and different
startup characteristics. Fresh shells currently resolve to the Bun
installation due to PATH order.

This duplication creates ambiguity about which binary is canonical, risks
version drift when only one installation is updated, and adds unnecessary
complexity to troubleshooting. Homebrew is the preferred canonical
installation: it is a standalone native binary, managed by Homebrew's
upgrade lifecycle, and has already passed default-role and explicit-provider
smoke tests.

## What Changes

1. Remove the three `@oh-my-pi/*` packages from `~/package.json` through Bun's
   package manager.
2. Confirm `~/.bun/bin/omp` no longer exists and that fresh shells resolve to
   `/opt/homebrew/bin/omp`.
3. Verify the live omp configuration (providers, roles, hashes) is unchanged.

## Non-Goals

- No omp configuration changes (providers, roles, models.yml, config.yml).
- No credential migration (OmniRoute inline key is a separate change).
- No Homebrew upgrade or pin — the current 17.2.15 is retained.
- No removal of unrelated Bun global packages (gitnexus, pyright, etc.).
