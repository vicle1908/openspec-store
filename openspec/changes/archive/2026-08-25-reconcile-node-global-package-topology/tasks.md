# Tasks: reconcile-node-global-package-topology

## 1. Inventory and evidence

- [x] 1.1 Capture fresh interactive and non-interactive Node/npm identity: executable paths, versions, `process.execPath`, npm userconfig path, effective prefix, global root, nvm variables as booleans/paths, and PATH-aware Claude resolutions.
- [x] 1.2 Capture a redacted global package manifest and the exact npm config scope/key responsible for the current prefix; do not print credentials or unrelated config values.
- [x] 1.3 Verify the native Claude binary by absolute path and record its version before any npm mutation.
- [x] 1.4 Verify the stale `@anthropic-ai/claude-code` package exists in the exact tree that the selected runtime would mutate; do not infer ownership from a symlink alone.

## 2. Topology decision

- [x] 2.1 Select nvm-managed per-version globals, fixed-runtime `~/.npm-global`, or stop with a decision blocker; record the evidence and rationale.
- [x] 2.2 If nvm-managed topology is selected, remove/neutralize only the incompatible forced prefix setting in its owning config scope and verify the active runtime before continuing.
- [x] 2.3 If fixed-runtime topology is selected, set the prefix only in the approved npm config scope after verifying the global bin directory is on PATH.

## 3. Claude package cleanup

- [x] 3.1 Record the exact stale package version and owning global root for rollback.
- [x] 3.2 Remove only `@anthropic-ai/claude-code` from the proven owning tree; do not remove the native Claude installation or unrelated global packages.
- [x] 3.3 Verify native Claude by absolute path and `whence -a`/`type -a`; verify the stale npm package is absent from the intended tree.

## 4. Final evidence and rollback

- [x] 4.1 Compare the redacted package manifest before/after and prove only the intended package/config changed.
- [x] 4.2 Re-run interactive and non-interactive runtime/root checks and record the selected topology.
- [x] 4.3 Rehearse or document rollback using captured config scope/value and exact package version; do not use hard-coded `~/.local` or `~/.npm-global` assumptions.
