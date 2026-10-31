# Tasks: Reconcile OMP Installation and Shell PATH Hygiene

## 1. Package Installation and Validation
- [x] 1.1 Install `can1357/tap/omp` v18.14.0 via Homebrew
- [x] 1.2 Verify `omp --version` and `omp --help` exit with code 0
- [x] 1.3 Verify internal CLI autocompletion engine (`omp __complete models`, `omp __complete sessions`)

## 2. Shell Configuration and Latency Optimization
- [x] 2.1 Back up `~/.zshrc` to `~/.zshrc.bak-20261030-omp-check`
- [x] 2.2 Optimize OMP completions block in `~/.zshrc` with `_comps[omp]` check
- [x] 2.3 Standardize `kimi-code` PATH addition to use `_path_prepend`
- [x] 2.4 Validate syntax with `zsh -n ~/.zshenv` and `zsh -n ~/.zshrc`
- [x] 2.5 Measure shell startup latency improvement

## 3. Toolchain & Environment Verification
- [x] 3.1 Verify CLI resolution in interactive login shell
- [x] 3.2 Verify CLI resolution in clean environment (`env -i`)
- [x] 3.3 Verify zero stderr noise across non-interactive, interactive, and login shells

## 4. Persistent Memory & Knowledge Synchronization
- [x] 4.1 Reconcile `agentmemory` engine and secret configuration
- [x] 4.2 Save structured memory into `agentmemory`
- [x] 4.3 Save memory entry into OMP local memories
- [x] 4.4 Record OpenSpec change and sync knowledge to Notion
