# Proposal: optimize-zshrc-and-package-hygiene

## Why

The 2026-08-25 audit of `~/.zshrc` and installed packages found measurable
shell hygiene issues, but the first draft coupled them with unsafe Node/npm
migration assumptions. The execution boundary is narrowed here and the Node
package topology work is moved to the successor change
`reconcile-node-global-package-topology`.

Current evidence:

1. **Interactive startup is slow: 4.5-5.2s** for three `zsh -ic 'exit'` runs.
   This is a baseline, not proof that completion or nvm changes alone can
   reach a `<2s` target. Starship, oh-my-zsh plugins, CCE provider loading,
   SSH checks, iTerm integration, Kiro, fzf, Bun, and other startup work also
   contribute.
2. **There are three explicit `compinit` calls plus oh-my-zsh's internal
   completion initialization.** The current explicit calls are in the Docker
   completion block, Grok installer block, and trailing Docker Desktop block.
   The first draft's proposed `compinit -C` would bypass completion security
   checks and is rejected by this revision.
3. **Seven literal secret-bearing exports are present in `~/.zshrc`:**
   `NPMJS_TOKEN`, `POSTMAN_API_KEY`, `API_KEY_SECRET`,
   `OMNIROUTE_API_KEY`, `COPILOT_PROVIDER_API_KEY`,
   `BRAVE_SEARCH_API_KEY`, and `EXA_API_KEY`. The prior draft incorrectly
   described `NPMJS_TOKEN` as already redacted; the live file contains a
   literal assignment (display tooling may redact its value).
4. **Node/npm ownership is unresolved:** the active shell loads Homebrew nvm,
   `npm config get prefix` reports `~/.local`, while the observed global npm
   packages live under `~/.npm-global`. nvm's documented prefix constraints
   mean this cannot be repaired safely by a blind `npm config set`.
5. **Claude has two installations:** the native `~/.local/bin/claude` is
   newer and wins PATH resolution, while the npm-global copy is stale. Its
   removal is moved to the successor so the exact owning npm tree is proven
   first.
6. Homebrew reports broken metadata for `antigravity-cli` and an unlinked
   `block-goose-cli` keg. One outdated cask (`antigravity`) was observed, but
   upgrading it is not part of this bounded hygiene change.
7. The CCE integration evaluates external binary output with `eval`. This is
   a security-sensitive residual risk and is documented as an explicit
   follow-up, not silently changed here.

## What Changes

### R1 - Deduplicate and order completion inputs

- Remove the duplicate pnpm PATH block and retain one idempotent guard for
  both `$PNPM_HOME` and `$PNPM_HOME/bin`.
- Remove the trailing Docker Desktop completion block.
- Add Docker and Grok completion directories to `fpath` before oh-my-zsh is
  sourced so its audited completion initialization sees them.
- Move `kimi-cli` before `zsh-syntax-highlighting`; keep
  `zsh-syntax-highlighting` as the final oh-my-zsh plugin.
- Set `ZSH_AUTOSUGGEST_STRATEGY` before oh-my-zsh initializes its plugins.

### R2 - Use oh-my-zsh's audited completion initialization

- Remove all explicit post-plugin `compinit` calls; do not add `compinit -C`.
- Set a deterministic `ZSH_COMPDUMP` before sourcing oh-my-zsh, then compile
  the actual configured dump only when it is newer than its `.zwc` file.
- Verify completion security with `compaudit`; do not hide or bypass insecure
  directory warnings.

### R3 - Preserve nvm behavior in this change

Do not add hand-written lazy wrappers. The first draft's wrapper design was
unsafe (`exec node` can replace the interactive shell), incomplete for
`corepack`/global executables, and not transparent for `.nvmrc`, default-alias,
or non-interactive behavior. nvm/Node/npm topology and any performance
optimization are owned by `reconcile-node-global-package-topology`.

### R4 - Move shell secrets without expanding their scope

- Move the seven literal secret exports to `~/.zshenv.secrets`, mode `0600`,
  and source it from `~/.zshrc` with an owner/mode check.
- Preserve the current interactive-shell scope; do not source the file from
  `.zshenv` unless a separate consumer audit proves non-interactive need.
- Keep values out of evidence, command output, backups copied into the store,
  and OpenSpec artifacts. Record only variable names and boolean checks.
- Record rotation as a residual follow-up because moving already-exposed
  credentials is not equivalent to rotating them. The shared
  `OMNIROUTE_API_KEY`/`COPILOT_PROVIDER_API_KEY` identity must be called out
  without recording its value.

### R5 - Bounded Homebrew repair

After a targeted preflight and version/link capture:

- Reinstall `antigravity-cli` only if its metadata is actually invalid.
- Link `block-goose-cli` only if the preflight confirms it is the reported
  unlinked keg.
- Do not upgrade `antigravity` in this change; that is a separately approved
  maintenance action requiring its own rollback/current-version evidence.

### R6 - Successor handoff for Node/npm/Claude

Capture current Node/npm/package ownership as read-only evidence and leave
prefix repair and stale Claude removal to
`reconcile-node-global-package-topology`. No task in this change may assume
that `~/.npm-global` or `~/.local` is the canonical tree.

## Scope / Non-goals

- No source-code, repository, or OpenSpec spec delta (`skip_specs: true`).
- No hand-written lazy nvm wrappers and no nvm installation migration.
- No npm prefix mutation or package uninstall in this change.
- No Claude package removal in this change.
- No credential rotation in this change; the follow-up is explicit and must
  not be lost during archival.
- No CCE `eval` redesign in this change; record it as a security follow-up.
- No broad Homebrew cleanup or `brew upgrade` sweep.

## Execution gates

Execution must stop rather than guess when any of these fail:

1. `.zshrc` and secret-file backups are byte-identical, user-owned, and mode
   safe; no secret value is copied into the store.
2. `zsh -n ~/.zshrc` passes and a bounded fresh-shell test can source the file
   twice without a hang.
3. `compaudit` output is captured as redacted path/permission evidence and no
   insecure completion path is silently bypassed.
4. Node/npm topology is captured and handed to the successor; this change does
   not mutate the prefix when nvm ownership is unresolved.
5. Homebrew targeted diagnostics complete successfully before either repair.

## Rollout

1. Capture redacted baseline evidence and create local backups.
2. Move secrets and apply the semantic `.zshrc` cleanup (verify anchors, not
   stale line numbers).
3. Run syntax, double-source, completion, provider-function, and performance
   gates.
4. Capture the Node/npm/Claude ownership handoff for the successor change.
5. Run targeted Homebrew preflight, repair only the two confirmed warnings,
   and verify exact post-state.
6. Record residual CCE and credential-rotation follow-ups.

## Rollback

- Restore `~/.zshrc` from its timestamped byte-verified backup.
- Restore `~/.zshenv.secrets` only from its mode-0600 local backup; never put
  the backup in the repository or evidence bundle.
- For Homebrew, restore the prior link state with the package-manager command
  recorded by the preflight; do not claim rollback for an unperformed cask
  upgrade.
- Node/npm and Claude rollback instructions belong to the successor and must
  restore captured values/package versions rather than hard-coded paths.

## Post-change follow-up

- Rotate all credentials that were previously stored literally in `~/.zshrc`,
  prioritizing the shared OmniRoute/Copilot key pair, then npm, Postman,
  internal API, Brave, and Exa credentials through their owning providers.
- Review the CCE `eval` boundary and replace unrestricted evaluation with a
  validated environment-update protocol.
- Execute `reconcile-node-global-package-topology` only after its fresh
  runtime/package ownership gate passes.
