## Why

The shell startup configuration currently exposes the required developer CLIs, but PATH construction is not consistently idempotent across `.zshenv`, `.zprofile`, and `.zshrc`: repeated entries are present, one TeX Live entry points at a nonexistent directory, the JetBrains Toolbox entry in `.zprofile` is malformed (a literal backslash inside double quotes makes it resolve to a nonexistent directory), and NVM can inherit an incompatible `npm_config_prefix` from parent process environments. This change will make shell startup predictable without changing the precedence of working tools.

## What Changes

- Normalize PATH additions across the shell startup files while preserving existing command precedence and position semantics (prepend vs append-at-end).
- Add only existing optional tool directories and avoid duplicate entries, following the existing pnpm `case`-guard idempotent pattern.
- Fix the malformed JetBrains Toolbox PATH entry in `.zprofile` so it resolves to the real `Application Support` directory.
- Remove or conditionally skip the stale TeX Live path.
- Keep `.zshenv` lightweight and retain the valid Qoder bootstrap.
- Defensively unset `npm_config_prefix` at the NVM initialization boundary so startup is deterministic even when a parent process exports it.
- Add validation for interactive and non-interactive shells and the supported CLI inventory.
- **Non-goals:** no credential rotation or relocation, no provider behavior changes, no package upgrades, no changes to application repositories, and no rewrites of launcher-managed blocks beyond the minimal inline quoting fix.

## Capabilities

### New Capabilities

None. This is a shell configuration and validation change with no new product capability.

### Modified Capabilities

None. No existing product-level requirements change.

## Impact

Affected ownership boundaries are the user's personal shell configuration — `~/.zshenv` (Qoder bootstrap, shared secrets), `~/.zprofile` (Homebrew `brew shellenv`, JetBrains Toolbox entry, `~/.local/bin`, OrbStack init, Qoder block), and `~/.zshrc` (NVM, pnpm, user CLI directories, Android SDK, Bun, provider-tool paths) — plus the locally installed CLI toolchains under `~/.local/bin`, `~/.npm-global/bin`, Homebrew, and NVM. Validation will cover PATH ordering, executable discovery, Node/npm/pnpm compatibility, and startup diagnostics. The OpenSpec store records the plan; implementation remains outside the store in the user's dotfiles.

This change is configuration/tooling-only and opts out of delta specs via `skip_specs: true`.
