# Proposal: reconcile-node-global-package-topology

## Why

The current macOS shell has three competing Node/npm surfaces:

- `~/.zshrc` loads Homebrew nvm and the active shell resolves an nvm-managed
  Node version.
- `npm config get prefix` reports `~/.local` in the observed environment.
- The global agent package tree observed during the audit is
  `~/.npm-global`, which is also on PATH.

There are also two Claude installations: a newer native
`~/.local/bin/claude` and a stale npm-global `@anthropic-ai/claude-code` copy.
The original cleanup proposal tried to set a global prefix and uninstall the
stale package without proving which Node/npm runtime owned that tree. nvm's
prefix constraints make that unsafe.

## What Changes

- Capture the active Node/npm runtime and all relevant config scopes in fresh
  interactive and non-interactive shells.
- Select one supported topology based on evidence:
  - nvm-managed Node with per-version global package trees and no incompatible
    forced npm prefix; or
  - a fixed Homebrew/Hermes Node with an explicitly managed `~/.npm-global`
    tree, while leaving nvm behavior separate and documented.
- Preserve a redacted global package manifest and exact npm config scope/value
  for rollback.
- Verify the native Claude binary by absolute path and PATH-aware resolution.
- Remove only the stale Claude package from the proven owning tree, or stop if
  ownership cannot be proven.
- Verify `npm ls -g`, `npm root -g`, package ownership, and Claude resolution
  after the selected topology is applied.

## Scope / Non-goals

- No blind `npm config set prefix ~/.npm-global` or `~/.local`.
- No package uninstall based only on a symlink or `which -a` result.
- No secret values in evidence or command output.
- No nvm installation migration unless the preflight selects it and a separate
  explicit migration plan is approved.
- No Homebrew upgrades.

## Execution gates

Stop before mutation when the active runtime, npm config scope, global root,
PATH, and package manifest do not agree on one owner. A successful `npm ls -g`
under a different runtime is not evidence for the shell's active runtime.

## Rollback

Restore the captured npm config scope/value, original runtime selection, and
exact package version from the preflight manifest. Do not use a hard-coded
rollback path.
