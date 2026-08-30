## Context

See `proposal.md` for motivation. The validated startup chain is `.zshenv` → `.zprofile` → `.zshrc` for login interactive shells. `.zshenv` owns the Qoder bootstrap and shared secrets. `.zprofile` runs Homebrew `brew shellenv`, adds a malformed JetBrains Toolbox entry (the double-quoted `Application\ Support` backslash is literal, so the PATH entry names a nonexistent directory — the real `Application Support` directory exists and contains `idea`/`studio`), adds `~/.local/bin`, sources OrbStack init, and repeats the Qoder block. `.zshrc` loads NVM and adds user, package-manager, Android, Bun, and provider-tool paths. All supported CLIs currently resolve, so first-match command precedence is an explicit compatibility constraint. `npm_config_prefix` is set by no dotfile — it appears only when inherited from a parent process environment (e.g., shells spawned by GUI apps), which is why the NVM warning is context-dependent rather than deterministic.

## Goals / Non-Goals

**Goals:**

- Make every PATH entry added by the dotfiles resolve to an existing directory.
- Make user-managed PATH additions idempotent and conditional on directory existence.
- Preserve first-match precedence and prepend-vs-append position semantics for currently working CLIs.
- Keep `.zshenv` fast and limited to universal environment setup.
- Make NVM initialization deterministic regardless of inherited environment.
- Provide repeatable shell and executable-discovery checks.

**Non-Goals:**

- Do not rotate, print, relocate, or otherwise modify credentials.
- Do not upgrade Node, npm, pnpm, Homebrew, or any CLI package.
- Do not change provider launcher semantics or application repositories.
- Do not rewrite launcher-managed blocks wholesale — only the minimal inline quoting fix to the Toolbox entry.
- Do not prune system- or launcher-inherited PATH entries that the dotfiles do not own.

## Decisions

1. **Use one idempotent PATH helper in the interactive configuration, following the existing pnpm `case`-guard pattern in `.zshrc:112-119`.**
   - Rationale: the pnpm guard already proves the pattern works in this codebase; generalizing it avoids re-adding directories on repeated sourcing while preserving first occurrence.
   - Alternative rejected: blindly replacing PATH with a hard-coded list, because it could remove IDE, system, or launcher-provided tools.

2. **Keep `.zshenv` limited to universal bootstrap behavior.**
   - Rationale: `.zshenv` is read by every zsh process, including scripts; expensive or interactive setup there would leak into noninteractive tools.
   - Alternative rejected: moving all CLI paths into `.zshenv`, because it increases process overhead and changes behavior for scripts.

3. **Consolidate user-owned additions in `.zprofile`/`.zshrc` according to shell role.**
   - Rationale: login-only PATH additions belong in `.zprofile`; NVM and interactive integrations belong in `.zshrc`. Each directory should have one owner and one insertion point.
   - Alternative rejected: adding more unconditional exports to `.zshrc`, which would preserve the current duplication problem.

4. **Guard optional paths with filesystem checks.**
   - Rationale: the TeX Live directory is verified absent while Android, JetBrains, Qoder, and the main CLI directories exist. Conditional additions avoid stale PATH components without assuming future installations.
   - Alternative rejected: deleting every currently absent inherited path, because some are managed by launchers and may be intentionally available in another context.

5. **Fix the JetBrains Toolbox quoting in place inside its launcher-managed block.**
   - Rationale: the entry is inside double quotes where the backslash is literal, so it never resolved. Correcting the quoting (single quotes or unquoted escaped space) is a one-line fix that keeps the `# Added by Toolbox App` block intact.
   - Alternative rejected: deduplicating or rewriting the Toolbox line into the helper, because Toolbox may re-append its own line on update and a rewritten block would just get clobbered.

6. **Defensively unset `npm_config_prefix` at the NVM initialization boundary.**
   - Rationale: verified that no dotfile sets this variable; it reaches shells only through inherited parent-process environments, so the warning is nondeterministic. Unsetting it just before sourcing `nvm.sh` makes startup deterministic without touching npm's npmrc-managed prefix, which correctly points at the NVM-managed node directory.
   - Alternative rejected: configuring npm's prefix globally, because that can conflict with NVM and package-manager ownership, and the npmrc prefix is not the problem.

7. **Validate both shell modes and command provenance.**
   - Rationale: an interactive login shell exercises `.zprofile` and `.zshrc`, while a clean noninteractive shell exercises `.zshenv` behavior. Validation must check dotfile-added path existence, uniqueness, executable locations, versions, and startup stderr.

## Risks / Trade-offs

- [Risk] PATH order changes can select a different executable → record current `command -v` results before editing and compare after editing.
- [Risk] Removing an optional path could affect a future tool installation → use existence guards and retain documented ownership rather than deleting unrelated inherited entries.
- [Risk] Clearing npm prefix could affect a non-NVM workflow → the unset is scoped to the NVM initialization boundary; npm's npmrc-managed prefix is untouched, and `npm config get prefix` is verified unchanged.
- [Risk] A Toolbox update may re-append a malformed line → keep the fix minimal inside the existing block; a re-added dead entry is detectable by the PATH-existence check and harmless to CLI resolution.
- [Risk] Dotfiles contain sensitive environment exports → never include their values in artifacts, logs, diffs, or test output.

## Migration Plan

1. Snapshot relevant dotfile hashes and command provenance without displaying secrets.
2. Fix the Toolbox quoting in `.zprofile`; edit `.zprofile`/`.zshrc` PATH additions per the decisions above; only adjust `.zshenv` if required by validation.
3. Start a fresh login shell and a clean noninteractive shell.
4. Verify PATH uniqueness, dotfile-added path existence, CLI discovery, Node/npm/pnpm versions, and absence of NVM prefix warnings.
5. Roll back by restoring the pre-change dotfiles if any command precedence or launcher behavior changes unexpectedly.

## Open Questions

- Whether the stale TeX Live installation should be restored later is outside this change; the implementation uses a conditional path so that a future installation becomes available automatically.
