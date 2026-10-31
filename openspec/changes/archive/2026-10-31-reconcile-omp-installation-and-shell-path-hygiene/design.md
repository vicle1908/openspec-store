# Design: Reconcile OMP Installation and Shell PATH Hygiene

## Context

The user workstation relies on `omp` (`omp.sh`, Stencil Labs coding agent) for agentic workflows alongside `pi`, `kimi-code`, `claude`, and `qoder`. Shell configuration files (`~/.zshenv`, `~/.zprofile`, `~/.zshrc`) manage environment variables and PATH ordering across interactive and non-interactive sessions.

## Architecture & Decisions

1. **Package Provisioning via Homebrew Tap**:
   - `can1357/tap/omp` v18.14.0 provides a single Mach-O arm64 binary at `/opt/homebrew/bin/omp` and completion definition at `/opt/homebrew/share/zsh/site-functions/_omp`.
   - Installing via Homebrew integrates cleanly into standard update routines (`brew update && brew upgrade`).

2. **Idempotent and Fast Shell Completion**:
   - `oh-my-zsh` compinit audits `$fpath` and compiles functions into `~/.zcompdump`.
   - Because `/opt/homebrew/share/zsh/site-functions` is in `$fpath`, `compinit` binds `_comps[omp]=_omp`.
   - Guarding the `eval "$(omp completions zsh)"` call with `[[ -z "${_comps[omp]}" ]]` avoids evaluating 772 lines of shell code on every interactive shell start, cutting ~100ms of lag while retaining fallback dynamic completion.

3. **PATH Helper Normalization**:
   - `_path_prepend` ensures directory existence and prevents duplicate entries if the shell is re-sourced.
   - `kimi-code` was converted from raw PATH prepend to `_path_prepend "$HOME/.kimi-code/bin"`.

4. **Agentmemory Engine Reconciliation**:
   - `agentmemory` v0.9.31 requires pinned `iii-engine` v0.25.0. Stale processes on port 49134 were cleanly stopped using `agentmemory stop --force`.
   - `AGENTMEMORY_SECRET` was configured in `~/.agentmemory/.env` matching `~/Library/Application Support/agentmemory/secret`, securing REST API authentication on port 3111.

## Risks & Mitigations

- **Risk**: Shell syntax error breaking terminal startup.
  - *Mitigation*: Validated with `zsh -n` across `.zshenv`, `.zprofile`, and `.zshrc`.
- **Risk**: Loss of autocompletion functionality when bypassing dynamic eval.
  - *Mitigation*: Verified `_comps[omp]` resolves to `_omp` and test-tab-completed flags/subcommands.
