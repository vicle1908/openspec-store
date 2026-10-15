# Tasks

## 1. Safety Backup & Baseline Measurement

- [x] 1.1 Create safety backup of `~/.zshrc` at `~/.zshrc.pre-resilience-hardening` and verify backup file exists with non-zero size.
- [x] 1.2 Record baseline startup latency via `time zsh -i -c exit` to establish pre-change benchmark (measured 0.919s).

## 2. Shell Configuration Hardening in ~/.zshrc

- [x] 2.1 Implement lazy-loading for NVM (`nvm`, `node`, `npm`, `npx`) replacing synchronous `$NVM_DIR/nvm.sh` sourcing, and verify `node -v` works on demand.
- [x] 2.2 Guard `ssh-add` execution with `[[ -t 0 ]]` so headless or non-interactive shells never hang waiting for agent or keychain access.
- [x] 2.3 Safeguard `cce` initialization to ensure local provider queries do not block shell startup when the endpoint is unready.
- [x] 2.4 Clean stale `~/.zcompdump*` files and ensure `.zcompdump.zwc` recompilation functions cleanly.
- [x] 2.5 Run syntax verification `zsh -n ~/.zshrc` and confirm exit code 0.

## 3. Host Storage & Process Remediation

- [x] 3.1 Verify runaway daemon `AddressBookSourceSync` is stopped and system CPU load stabilizes.
- [x] 3.2 Clean Xcode DerivedData and unavailable simulator runtimes to increase available disk space on `/System/Volumes/Data`.

## 4. Verification & Validation

- [x] 4.1 Measure post-hardening startup latency with `time zsh -i -c exit` and verify significant speedup compared to the 920ms baseline (achieved 0.17s–0.19s, ~5x faster).
- [x] 4.2 Verify essential CLI tools (`node -v`, `npm -v`, `nvm --version`) execute cleanly in a fresh subshell.
- [x] 4.3 Validate OpenSpec change strictly via `openspec validate harden-terminal-and-shell-resilience --strict --store openspec-store`.
