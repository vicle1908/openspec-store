## 1. Baseline and ownership

- [x] 1.1 Record non-secret hashes of `~/.zshenv`, `~/.zprofile`, and `~/.zshrc`, plus the current `command -v` result for each supported CLI; verify no credential values are emitted.
- [x] 1.2 Map each PATH directory to one owning startup file and document inherited launcher-managed entries (Toolbox, OrbStack, Qoder); verify the ownership map covers all user-managed additions and the current malformed Toolbox entry.

## 2. Shell configuration cleanup

- [x] 2.1 Add or reuse an idempotent PATH-directory helper that preserves first-match precedence and position semantics (prepend vs append-at-end), following the existing pnpm `case`-guard pattern; verify repeated shell sourcing does not increase PATH entry counts.
- [x] 2.2 Consolidate duplicate user-managed PATH additions between `.zprofile` and `.zshrc`; verify `.zshenv` remains limited to universal bootstrap behavior.
- [x] 2.3 Make the TeX Live PATH addition conditional on directory existence; verify no stale TeX path appears while the directory is absent.
- [x] 2.4 Fix the JetBrains Toolbox quoting in `.zprofile` so the PATH entry resolves to the real `Application Support/JetBrains/Toolbox/scripts` directory; verify `command -v idea` and `command -v studio` resolve in a fresh login shell (if those launchers are present) and that the Toolbox block's marker comments remain intact.
- [x] 2.5 Defensively unset `npm_config_prefix` at the NVM initialization boundary without changing npm's npmrc-managed prefix; verify login-shell startup emits no NVM prefix warning even when the variable is injected by a parent process, and that `npm config get prefix` is unchanged.

## 3. Verification and rollback readiness

- [x] 3.1 Start clean login interactive and noninteractive zsh processes; verify shell startup succeeds, dotfile-added PATH entries are unique, and every directory the dotfiles add exists on disk.
- [x] 3.2 Verify `bx`, `tvly`, `exa`, `brightdata`, `ctx7`, `deepwiki`, `graphify`, `openspec`, `uv`, `pnpm`, `node`, `npm`, `npx`, `docker`, and `claude` resolve to the expected executable families.
- [x] 3.3 Verify Node, npm, npx, and pnpm versions and NVM selection remain unchanged; verify no package installation or upgrade occurs.
- [x] 3.4 Compare post-change command provenance with the baseline and exercise the documented dotfile rollback; verify unrelated launcher paths and provider launcher functions (`shopapikey`, `cockpit`, `claude_reset`) remain operational.
