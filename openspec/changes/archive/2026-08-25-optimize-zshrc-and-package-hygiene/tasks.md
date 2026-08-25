# Tasks: optimize-zshrc-and-package-hygiene

## 1. Baseline and local backups

- [x] 1.1 Capture redacted baseline evidence: `.zshrc` sha256, three fresh-shell startup samples, `command -v`/`type -a` results for node/npm/claude, `npm config get prefix`, `npm root -g`, package names/versions, targeted Homebrew status, and current file modes. Never print credential values.
- [x] 1.2 Create `~/.zshrc.bak-<timestamp>` and verify it is byte-identical with `cmp`; keep the backup outside the repository.
- [x] 1.3 Create `~/.zshenv.secrets.bak-<timestamp>` and the new `~/.zshenv.secrets`; require regular-file, current-user ownership, and mode `0600` for both. Keep both outside the repository and never copy their contents into evidence.
- [x] 1.4 Record the seven migrated variable names, the shared OmniRoute/Copilot credential identity, and the required rotation follow-up without recording values.

## 2. Safe `.zshrc` cleanup

- [x] 2.1 Re-read semantic anchors immediately before editing; remove the duplicate pnpm PATH block and trailing Docker Desktop completion block without relying on stale line numbers.
- [x] 2.2 Move Docker and Grok completion `fpath` additions before oh-my-zsh; set deterministic `ZSH_COMPDUMP` before sourcing oh-my-zsh; remove all explicit `compinit` calls and do not add `compinit -C`.
- [x] 2.3 Move `kimi-cli` before `zsh-syntax-highlighting`, keep syntax highlighting last, and set `ZSH_AUTOSUGGEST_STRATEGY` before oh-my-zsh initialization.
- [x] 2.4 Compile only the actual configured completion dump after initialization, using the dump/zwc mtime guard; remove assumptions about a plain `~/.zcompdump` path.
- [x] 2.5 Replace literal secret exports with a guarded source of `~/.zshenv.secrets`; the guard must refuse unsafe owner/mode/file types and preserve interactive-only sourcing.
- [x] 2.6 Leave nvm loading, CCE behavior, provider launchers, and unrelated PATH entries unchanged; explicitly record those boundaries in evidence.

## 3. Shell and completion verification

- [x] 3.1 Run `zsh -n ~/.zshrc` and a bounded fresh-shell test that sources `.zshrc` twice; verify no hang, syntax failure, or duplicate initialization failure.
- [x] 3.2 Run `compaudit` and inspect every returned path's owner/mode; verify Docker, Grok, Bun, and plugin completions resolve without suppressing security warnings.
- [x] 3.3 Verify `type shopapikey giaoduc cockpit cce` and the documented provider launcher functions remain available; do not invoke providers or expose credentials.
- [x] 3.4 Run three post-change startup samples and one component profile; report measured cold/warm values and contributors. Do not require an unsupported `<2s` target.

## 4. Node/npm/Claude handoff

- [x] 4.1 Capture the current Node/npm runtime, nvm variables, npm config scope, effective prefix, global root, package manifest, and Claude resolutions in redacted evidence.
- [x] 4.2 Link the evidence to `reconcile-node-global-package-topology`; do not mutate npm prefix, uninstall Claude, or claim package cleanup in this change.

## 5. Targeted Homebrew repair

- [x] 5.1 Run targeted preflight (`brew config`, targeted `brew info`, metadata/link/version capture) once; a timeout or nonzero result blocks repair tasks.
- [x] 5.2 If preflight confirms invalid `antigravity-cli` metadata, run `brew reinstall --cask --force antigravity-cli`; verify targeted metadata afterward.
- [x] 5.3 If preflight confirms the reported unlinked `block-goose-cli` keg, run `brew link block-goose-cli`; verify link state and command resolution afterward.
- [x] 5.4 Leave the outdated `antigravity` cask unchanged and record it as separately approved maintenance; do not run `brew upgrade` here.

## 6. Evidence and closure

- [x] 6.1 Record post-change hashes, modes, timings, completion results, Homebrew targeted results, and Node/npm handoff facts in a redacted evidence file under this change; never store secret values.
- [x] 6.2 Record residual CCE `eval` risk and credential-rotation follow-up; verify the successor change owns the Node/npm/Claude mutation scope.
