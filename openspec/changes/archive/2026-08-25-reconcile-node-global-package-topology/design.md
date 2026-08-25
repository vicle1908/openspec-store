# Design: reconcile-node-global-package-topology

## Preflight contract

Run each probe in a fresh shell and capture only paths, versions, package
names, and booleans. Never print environment values that may be credentials.

```text
command -v node
command -v npm
node -p process.execPath
node --version
npm --version
npm config get userconfig
npm config get prefix
npm root -g
npm ls -g --depth=0
printenv NVM_DIR NPM_CONFIG_PREFIX PREFIX
zsh -ic 'command -v node; command -v npm; node -p process.execPath; node --version; npm --version; npm config get userconfig; npm config get prefix; npm root -g; whence -a claude'
```

Also record whether the effective npm config file contains a prefix setting,
without printing unrelated config values.

## Topology decision

### Topology A - nvm-managed

Choose this only if the active `node` path is under the nvm version tree and
nvm is intentionally the shell's Node owner. Remove or neutralize only the
incompatible custom prefix setting after recording its exact scope and value.
Global packages remain per nvm version. Do not assume the existing
`~/.npm-global` package tree belongs to this runtime; migrate packages only as a
separate, explicitly approved step.

### Topology B - fixed runtime with explicit global tree

Choose this only if the active shell is intentionally using a fixed Homebrew
or Hermes Node and `~/.npm-global` is the approved global package root. Set the
prefix only in the correct npm config scope after verifying the root is on
PATH, then manage packages through that one runtime.

If neither topology is supported by the evidence, stop and report a decision
blocker instead of changing prefix or deleting packages.

## Claude removal sequence

1. Verify `~/.local/bin/claude --version` by absolute path.
2. Capture `whence -a claude`, `type -a claude`, and the package root owning the
   npm-global Claude copy.
3. Record the exact installed package version and package root.
4. Remove only `@anthropic-ai/claude-code` from that exact tree using a
   prefix/runtime-pinned operation.
5. Verify native Claude remains the selected command and the npm package is
   absent from the intended tree while unrelated packages are unchanged.

## Evidence and rollback

Evidence contains a redacted package manifest, runtime paths, npm config scope,
root paths, and exact versions. It does not contain token-bearing config
output. Rollback restores the captured original config scope/value and
reinstalls the recorded package version into the recorded owning tree only if
needed.

## Verification matrix

| Surface | Required result |
|---|---|
| Runtime identity | interactive and non-interactive Node/npm paths are recorded |
| Prefix/root | prefix and `npm root -g` agree with the chosen topology |
| Package ownership | the target Claude package belongs to the tree being changed |
| Native Claude | absolute binary runs before and after cleanup |
| Unrelated packages | manifest diff contains only the intended package change |
| Rollback | captured config scope/value and exact package version are restorable |
