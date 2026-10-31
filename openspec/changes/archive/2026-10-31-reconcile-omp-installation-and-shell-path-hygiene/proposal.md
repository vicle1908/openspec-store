# Reconcile OMP Installation and Shell PATH Hygiene

## Why

1. `omp` (the CLI coding agent from `can1357/tap/omp`) was referenced in `~/.zshrc` and had existing session state and models configured in `~/.omp/`, but the Homebrew formula was missing from `/opt/homebrew/bin/omp`, causing command not found errors.
2. In `~/.zshrc`, `eval "$(omp completions zsh)"` ran unconditionally on every interactive shell launch. Homebrew already links `_omp` to `/opt/homebrew/share/zsh/site-functions/_omp`, which is loaded automatically by oh-my-zsh `compinit`. Evaluating the dynamic script every startup added ~100ms of unnecessary latency.
3. In `~/.zshrc`, `kimi-code` was added via a raw string prepend `export PATH="/Users/androidteam/.kimi-code/bin:$PATH"` rather than the idempotent `_path_prepend` helper.
4. `agentmemory` local daemon was stopped due to an engine version mismatch on port 49134 and missing `AGENTMEMORY_SECRET` in `~/.agentmemory/.env`.

## What Changes

- Install `can1357/tap/omp` v18.14.0 via Homebrew so `omp` is accessible across all login, interactive, and non-interactive environments.
- Optimize `~/.zshrc` completion handling for `omp` to check `_comps[omp]` before spawning the subshell eval, reducing interactive startup latency by ~100ms.
- Standardize the `kimi-code` PATH addition in `~/.zshrc` to use `_path_prepend "$HOME/.kimi-code/bin"`.
- Restart `agentmemory` daemon with pinned `iii-engine` v0.25.0 and configure `AGENTMEMORY_SECRET` to align with the server key.
- Validate toolchain resolution across interactive, login, and clean (`env -i`) environments.

## Non-Goals

- No credential rotation or modification of provider keys.
- No alteration of `omp` internal models or session history.
- No changes to unrelated PATH entries or application repositories.

## Impact

- `~/.zshrc` startup time improves from ~290ms to ~188ms.
- Full completion support for `omp` preserved.
- Consistent CLI resolution for all developer tools (`omp`, `bun`, `brew`, `node`, `pnpm`, `git`, `python3`, `pi`, `qoder`, `kimi`, `starship`).
- `agentmemory` REST API and worker health restored.
