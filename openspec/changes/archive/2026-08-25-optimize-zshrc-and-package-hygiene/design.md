# Design: optimize-zshrc-and-package-hygiene

## Context and baseline

This is a single-user macOS shell cleanup. The existing file combines
oh-my-zsh, Starship, multiple completion installers, nvm, agent launchers,
provider integration, and inline credentials. The first proposal treated all
of these as one mutation surface; review showed that completion security and
Node/npm ownership need separate contracts.

Baseline captured on 2026-08-25:

| Metric | Observed state |
|---|---|
| Interactive startup | 4.53-5.23s over three `zsh -ic 'exit'` runs |
| Explicit `compinit` calls | 3, plus oh-my-zsh's internal initialization |
| Secret-bearing exports | 7 literal assignments in `~/.zshrc` |
| npm prefix | `~/.local` in the observed shell |
| Observed npm global tree | `~/.npm-global` |
| Claude resolutions | native `~/.local/bin/claude` plus stale npm-global copy |
| Homebrew hygiene | invalid `antigravity-cli` metadata; unlinked `block-goose-cli`; `antigravity` outdated |

The Node/npm rows are observations only. They are not sufficient to choose a
canonical runtime until `command -v`, `node -p process.execPath`, npm config
scope, global root, nvm variables, and PATH are captured in the same fresh
shell.

## Design decisions

### D1 - Completion ownership stays with oh-my-zsh

All custom completion directories that must be visible to oh-my-zsh are
added to `fpath` before `source "$ZSH/oh-my-zsh.sh"`. The plugin list is ordered
so `zsh-syntax-highlighting` is last, and autosuggestion settings are defined
before plugin initialization.

The change removes the three explicit `compinit` calls and does not replace
them with `compinit -C`. Oh-my-zsh performs the single completion
initialization and retains its security checks. A deterministic
`ZSH_COMPDUMP="$HOME/.zcompdump"` may be set before oh-my-zsh; the post-source
compile step must reference `$ZSH_COMPDUMP` and compare dump/zwc mtimes rather
than assuming a filename. The verification gate runs `compaudit` and records
only permission/path facts.

### D2 - No ad-hoc nvm lazy loading

The first draft's wrappers were rejected because `exec` could replace the
interactive shell, wrappers would not cover arbitrary Node executables or
`corepack`, and nvm's `.nvmrc`/default-alias/non-interactive semantics would be
unclear. This change leaves the current nvm loading behavior untouched.

Any nvm optimization must first choose an installation/storage model and test
it against the active runtime. That work belongs to
`reconcile-node-global-package-topology` and is not inferred from startup
measurements.

### D3 - Secrets are private but remain interactive-only

`~/.zshenv.secrets` is a custom file, not an automatically sourced zsh file.
It is sourced from `~/.zshrc` only, preserving the current behavior and
avoiding expansion of credential exposure to every zsh process. The source
block refuses to load a file that is not a regular, user-owned file with mode
`0600`.

Migration evidence is structural: variable-name presence, assignment count,
mode, owner, and boolean export checks. It never prints values. Local backups
remain outside the repository, mode `0600`, and are not copied to the change
directory.

The seven credentials may already have been exposed by shell backups or sync.
Rotation is a documented residual follow-up, not falsely claimed remediation.
The two OmniRoute/Copilot variables are known to share one credential identity;
this fact is recorded without the credential value.

### D4 - Node/npm/Claude ownership is a separate contract

The successor change uses this preflight before any npm mutation:

```text
command -v node
command -v npm
node -p process.execPath
npm config get userconfig
npm config get prefix
npm root -g
npm ls -g --depth=0
printenv NVM_DIR NPM_CONFIG_PREFIX PREFIX
zsh -ic 'command -v node; command -v npm; node -p process.execPath; npm config get prefix; npm root -g'
```

The output must be redacted to names, paths, versions, and booleans before
entering evidence. If the active runtime is nvm-managed or the prefix is
externally forced, the successor must not blindly set `~/.npm-global`; it must
select a supported topology or stop for a decision. Claude removal is pinned
to the proven package root and verifies the native absolute binary first.
Rollback restores the captured npm config scope/value and exact package
version, not an assumed `~/.local` path.

### D5 - Homebrew repairs are targeted

The Homebrew portion captures `brew config`, targeted `brew info`, installed
versions, cask metadata, keg link state, and PATH resolution before mutation.
A diagnostic timeout or nonzero result blocks repairs. Only the two observed
warnings are addressed. The outdated `antigravity` cask is recorded but not
upgraded because cask rollback is not reliably version-pinned by the current
plan.

### D6 - Performance claims are measured, not promised

The change reports before/after startup measurements and uses component
profiling (`zprof` or an equivalent isolated profile) to distinguish completion
cost from CCE, Starship, nvm, SSH, and plugin costs. The `<2s` target is removed
as a hard acceptance criterion; an improvement is reported with its measured
cold/warm samples and remaining contributors.

## Verification matrix

| Surface | Gate | Evidence boundary |
|---|---|---|
| Syntax | `zsh -n ~/.zshrc`; bounded double source | exit status, duration, no secret values |
| Completion | `compaudit`; completion lookup for Docker/Grok/Bun/plugins | paths, owners, modes, command names |
| Plugin order | semantic check that syntax highlighting is last | plugin names only |
| Secrets | mode/owner check; old names absent from `.zshrc`; interactive export check | names/counts/booleans only |
| Provider shell functions | `type shopapikey giaoduc cockpit cce` | function/executable presence only |
| Node/npm handoff | runtime, prefix, root, package manifest, Claude resolutions | versions/paths/package names only |
| Homebrew | targeted pre/post info and link checks | formula/cask names, versions, links |
| Performance | three fresh-shell samples plus component profile | timings and labels only |

## Residual risks

- CCE still evaluates external output with `eval`; it remains a separate
  security follow-up.
- Credentials are moved, not rotated; archival must preserve the follow-up.
- The successor may find that nvm and the existing global package tree cannot
  be reconciled without a user-selected clean-break migration.
