# Proposal: Harden Terminal & Shell Resilience and Remediate Startup Latency

## Why

Following macOS system reboots and high load, iTerm2, Terminal.app, and interactive zsh shells experience hanging, UI stalls, and startup latencies exceeding 900ms. Profiling identified blocking synchronous initializations in `~/.zshrc` (synchronous `nvm` sourcing, unconstrained `ssh-add` keychain calls, synchronous `cce` provider configuration, un-cached `compinit`), coupled with severe host memory/swap exhaustion (12.9 GB swap used, <75 MB free physical RAM) and low disk headroom (30 GiB available / 93% capacity).

## What Changes

- **Lazy-load NVM in `~/.zshrc`**: Replace synchronous sourcing of `$NVM_DIR/nvm.sh` and bash completions (~50ms startup cost and subshell latency) with function wrappers triggered on first command invocation (`nvm`, `node`, `npm`, `npx`).
- **Guard SSH Keychain Execution**: Wrap `ssh-add --apple-use-keychain` with an interactive terminal check (`[[ -t 0 ]]`) and fail-safe timeout prevention so background or non-interactive shells never hang waiting for agent/keychain access.
- **Guard and Defer `cce use`**: Avoid synchronous execution of `cce use` during shell startup; defer provider environment resolution or check provider daemon availability before attempting evaluation.
- **Optimize Completion Dump & Compinit**: Leverage cached `.zcompdump` with `-C` flag verification to eliminate repeated security checks and file audits during every shell launch.
- **Reclaim Disk Space & Clear Simulator Stalls**: Clean build caches, remove stale iOS simulator caches/devices, and run disk reclamation to boost free disk headroom above 50 GiB, reducing swap compression pressure.
- **System Daemon Watchdog Verification**: Terminate runaways such as `AddressBookSourceSync` and monitor memory pressure.

## Capabilities

### New Capabilities
None. This is an operational tooling and developer environment resilience change (`skip_specs: true`).

### Modified Capabilities
None.

## Impact

- Affects `~/.zshrc` for interactive zsh sessions.
- Drastically reduces interactive shell startup latency from ~920ms toward <150ms.
- Eliminates blocking hangs in iTerm2, Terminal.app, and subshell executions.
- Frees local disk space on `/System/Volumes/Data`.
