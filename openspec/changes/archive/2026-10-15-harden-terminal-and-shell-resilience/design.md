# Design: Harden Terminal & Shell Resilience and Remediate Startup Latency

## Context

Detailed profiling via `zmodload zsh/zprof` revealed the interactive shell startup cost is ~920ms, dominated by:
1. `compinit` / `compdef` / `compdump` (over 700ms aggregate across 815 definitions without aggressive `-C` caching).
2. Synchronous `nvm` initialization (`nvm_auto`, `nvm_process_parameters`, sourcing `nvm.sh` and bash completions) taking ~50ms synchronously on every shell creation.
3. Synchronous `cce use` execution (~20ms) querying a local HTTP provider daemon synchronously.
4. SSH Keychain addition (`ssh-add --apple-use-keychain`) lacking a TTY test, which can hang non-interactive or background subshells indefinitely if macOS Keychain prompts for biometric or password auth.

Simultaneously, host metrics showed:
- High memory pressure with 12.9 GB swap used out of 13.3 GB.
- `/System/Volumes/Data` storage down to 30 GiB available (93% capacity).
- Runaway background process `AddressBookSourceSync` consuming 80–90% CPU.

## Goals / Non-Goals

**Goals:**
- Eliminate all blocking synchronous hooks that could freeze iTerm2 or Terminal.app on launch.
- Cut interactive shell startup latency from ~920ms to under 250ms.
- Lazy-load NVM so `nvm.sh` is only sourced when `nvm`, `node`, `npm`, or `npx` is first executed.
- Ensure `ssh-add` is strictly guarded by `[[ -t 0 ]]` (interactive TTY) and cannot block subshells.
- Make `cce use` safe against daemon stalls.
- Reclaim disk space on `/System/Volumes/Data` to give macOS VM paging room and prevent disk I/O thrashing.

**Non-Goals:**
- Do not modify Oh-My-Zsh framework source code.
- Do not modify `~/.zshenv` secrets tier (managed by OpenSpec change `standardize-zshenv-shared-secrets`).
- Do not disable Starship prompt or user-defined aliases.

## Decisions

### Decision 1: Lazy-load NVM via on-demand wrapper functions
*Rationale:* NVM's startup scripts (`nvm.sh` and bash completion) execute hundreds of shell lines and subshell forks on every terminal tab, adding 50–100ms and creating latency.
*Design:*
```zsh
export NVM_DIR="/opt/homebrew/opt/nvm"
unset npm_config_prefix
_load_nvm() {
  unset -f nvm node npm npx _load_nvm
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
}
nvm()  { _load_nvm; nvm "$@"; }
node() { _load_nvm; node "$@"; }
npm()  { _load_nvm; npm "$@"; }
npx()  { _load_nvm; npx "$@"; }
```
*Alternatives Considered:* Eager loading on every shell. Rejected because >90% of subshells or quick commands do not invoke Node.

### Decision 2: Guard `ssh-add` with `[[ -t 0 ]]`
*Rationale:* When `ssh-add` is run without an interactive TTY, it can trigger an invisible macOS UI modal or hang in Mach IPC waiting for input.
*Design:*
```zsh
if [[ -t 0 ]] && ! ssh-add -l &>/dev/null; then
  ssh-add -q --apple-use-keychain 2>/dev/null
fi
```

### Decision 3: Guard `cce use` with provider check and quiet fallback
*Rationale:* Sourcing `cce` runs `__cce_apply_current_provider` synchronously. If the local endpoint is unreachable, it should fail immediately without delaying prompt rendering.
*Design:* Keep the function definition, but execute provider application with non-blocking redirection or guard.

### Decision 4: Completion Cache Acceleration
*Rationale:* Oh-My-Zsh compiles `.zcompdump` to `.zwc`. Removing any stale `.zcompdump*` files and compiling the current dump ensures fast cached loads.

### Decision 5: Host Hygiene and Disk Reclamation
*Rationale:* 30 GiB free on a 460 GiB APFS volume with 13 GiB active swap leads to severe disk write throttling and page translation stalls. Running targeted cache cleanup (`DerivedData`, Gradle build cache, Docker build cache, old iOS simulators) will restore 15–30+ GiB of free space.

## Risks / Trade-offs

- **[Risk]** First invocation of `node` or `npm` in a new shell takes ~50ms to load NVM.
  → *Mitigation:* This 50ms is paid only once per session on demand, rather than on every single tab/subshell spawn.
- **[Risk]** Removing old build caches might require re-downloading dependencies on next build.
  → *Mitigation:* Only purge stale temporary caches (`DerivedData`, `.gradle/caches` older than 30 days, unused Docker builder cache).

## Migration Plan

1. Create a timestamped backup of `~/.zshrc` (`~/.zshrc.pre-resilience-hardening`).
2. Apply surgical edits to `~/.zshrc` for NVM lazy-loading and guarded `ssh-add`.
3. Validate syntax via `zsh -n ~/.zshrc`.
4. Run disk cleanup tasks to reclaim space.
5. Re-measure startup latency with `time zsh -i -c exit`.
6. Verify interactive tool functionality (`node -v`, `npm -v`, `nvm --version`).
