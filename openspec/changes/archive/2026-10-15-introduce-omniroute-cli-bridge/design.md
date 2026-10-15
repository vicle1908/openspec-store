# Design

## Context

See `proposal.md` for motivation. OmniRoute runs in Docker Desktop (`omniroute` container on loopback ports `20128` and `20129`) running official latest image `diegosouzapw/omniroute:latest` (v3.8.51, multi-arch index digest `sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218`). The SQLite database is isolated inside Docker named volume `omniroute-data` (`/app/data/storage.sqlite`).

The workstation has 45 official OmniRoute skills installed in `~/.agents/skills/`. The 22 `omni-*` REST skills function cleanly via HTTP loopback. However, the 21 `cli-*` skills invoke `omniroute <subcmd>`, which fails because no `omniroute` executable exists on `$PATH`.

Key architectural discoveries from research:
1. **Upstream Dual-Mode Execution**: In `bin/cli/runtime.mjs`, `withRuntime()` checks `isServerUp()`. When the Docker daemon answers on port `20128`, the CLI executes entirely over HTTP (`apiFetch()`).
2. **DB Fallback Is Reachable and Unsafe — CORRECTS AN EARLIER ASSUMPTION**: The HTTP branch is *not* guaranteed. When `isServerUp()` is false and the command did not request `requireServer: true`, `withRuntime()` falls through to `makeDbContext()`, which dynamically imports `src/lib/db/combos.ts` and opens SQLite locally. Measured: `bun bin/omniroute.mjs combo list --output json --base-url http://127.0.0.1:1` emitted `[DB] SQLite database ready: /Users/androidteam/.omniroute/storage.sqlite` and advanced that file's mtime. `resolveDataDir()` (`bin/cli/data-dir.mjs`) returns `~/.omniroute` whenever that legacy directory exists. There is consequently a stale host-side `~/.omniroute/storage.sqlite` (15.6 MB, last written 2026-08-24) that the CLI will silently open and mutate when the container is down. It is a *different* database from the container's authoritative volume, so a fallback write both corrupts a stale artifact and returns misleading empty results.
3. **DATA_DIR Relocation Neutralizes the Fallback — PROVEN**: Pointing `DATA_DIR` at an ephemeral directory redirects the DB branch away from `~/.omniroute`. Measured with `DATA_DIR=/tmp/omp-probe2`: a fresh `storage.sqlite` was created inside the temp directory and `~/.omniroute/storage.sqlite` mtime was unchanged (`1792031065` before and after). The decisive demonstration uses a real command against a dead server: `keys list --output json` with the default `DATA_DIR` returned **8 records** read from the stale orphan, while the same command with `DATA_DIR` pinned to an empty directory returned **`{"keys":[]}`**.
3b. **The Fallback Is Pervasive, Not an Edge Case**: Classifying commands against `--base-url http://127.0.0.1:1` showed `keys`, `status`, and `quota` all returning exit 0 with local-DB data, while `cost` and `health` failed with `HTTP 404`. The HTTP/DB choice hinges on whether a command passes `requireServer: true`, which only some do. Fail-closed exit codes therefore cannot be the primary mitigation; the `DATA_DIR` pin is.
3c. **`health --json` Emits No Payload on the v3.8.49 Checkout**: `bun bin/omniroute.mjs health --json` printed only the two `📋 Loaded env from` banner lines and exited 1, so `omniroute health --json | jq .status` cannot serve as a validation example. `keys list --output json`, `combo list --output json`, and `status --output json` do emit JSON; `providers list` ignores `--output json` and renders a table. `omniroute --version` is clean because `isVersionFastPath()` exits before `loadEnvFile()`.
4. **Bun Auto-Install Is the Mechanism — CORRECTS AN EARLIER ASSUMPTION**: Host Bun (`/opt/homebrew/bin/bun`, 1.4.3) executes `~/Omniroute/bin/omniroute.mjs` successfully in ~0.25–1.6s. Host `~/Omniroute/node_modules` is **absent**, and `bun --no-install bin/omniroute.mjs` **fails** with `error: Cannot find package 'update-notifier'`. So the run does not work "without installing": Bun's auto-install (`--install=auto`, the default when `node_modules` is missing) installs dependencies against the repo's `bun.lock` into its **global cache** (`~/.bun/install/cache`, ~1.0 GB observed, containing `tsx@4.23.15` and `update-notifier@7.3.1`) instead of into `node_modules`. Consequences: (a) no host `node_modules` and no global npm prefix pollution; (b) no C++ compilation, because Bun loads the shipped native artifacts; (c) the dependency payload lands in the Bun cache, so "zero footprint" is **false** — it is cache-resident rather than absent; (d) on a **cold cache the first invocation requires network egress to the npm registry**, and offline operation is not guaranteed.
5. **Official Image Ships CLI Modules But Not the Entrypoint — REFINES AN EARLIER CLAIM**: `docker exec omniroute ls /app/bin` returns only `chatgpt-web-codex-mcp.mjs` and `cli/` (whose sole child is `commands/`). `/app/bin/omniroute.mjs` is **ABSENT**, yet `/app/package.json` still declares `"bin": {"omniroute": "bin/omniroute.mjs"}`, and the container's own version is **3.8.51** (node v26.10.0). Next.js standalone tracing pulled in the `bin/cli/` modules the server imports while pruning the declared CLI entrypoint. The accurate statement is therefore *the entrypoint is missing from the image*, not *the CLI is entirely absent* — and no `omniroute` executable exists anywhere on the container's `$PATH`.
6. **Stdout Corruption Is Multi-Source**: `bin/omniroute.mjs:142` prints `  📋 Loaded env from ${envPath}` via `console.log` from `loadEnvFile()`, which is invoked at line 146 — before Commander parses flags. `-q`/`--quiet` does **not** suppress it (measured). Piped JSON consumers therefore break (`omniroute health --json | jq .` → `Expecting value: line 1 column 3`). A second class of noise appears only on the DB branch: `[DB] Changing cache_size...`, `[DB] cache_size changed...`, `[DB] SQLite database ready: ...`. Bare `--version`/`-V` is exempt because `isVersionFastPath()` (`bin/cli/utils/versionFastPath.mjs`) exits before `loadEnvFile()` runs — measured `bun bin/omniroute.mjs --version` prints only `3.8.51`.
7. **Version Skew Resolved — Checkout Refreshed to v3.8.51**: The local checkout at `~/Omniroute` was fast-forwarded to commit `fd95f823d` (origin/main), achieving exact version parity across all three tiers: checkout `3.8.51` == container `3.8.51` == npm `3.8.51`. The local `@types/bun: latest` edit was superseded upstream by a pin to `1.4.2`, and `docker-compose.override.yml` is now cleanly gitignored upstream.
8. **Interactive Zsh Precedence**: In `~/.zshrc` line 313, `omniroute()` is defined as a Claude Code profile launcher governed by spec `claude-code-omniroute-pm-routing`. Measured: `zsh -c 'command -v omniroute'` returns nothing (no binary on `$PATH` today), while `zsh -i -c 'whence -w omniroute'` returns `omniroute: function`. Non-interactive agent subshells ignore `~/.zshrc` and will resolve `$PATH` directly once the bridge exists, while interactive user terminals need subcommand multiplexing.

## Goals / Non-Goals

**Goals:**
- Implement `~/.local/bin/omniroute` as an executable Bun bridge pointing to `/Users/androidteam/Omniroute/bin/omniroute.mjs`.
- Normalize `OMNIROUTE_BASE_URL` by stripping a trailing `/v1`, defensively (it is already normalized to `http://localhost:20128` on this workstation, so this guards the documented hazard rather than an active one).
- Pass through `OMNIROUTE_API_KEY` / `OMNIROUTE_KEY`, which `~/.zshenv` already exports into every zsh and bash process (verified: both `SET`, length 35). Fall back to `~/.claude/helpers/omniroute-key.sh` only when unset; it is a read-only parser of `~/.zshenv`, so it never mutates state.
- Stream-filter standard output to suppress the `📋 Loaded env from` startup banner and `[DB]` diagnostics for clean JSON pipelines.
- Pin `DATA_DIR` to an ephemeral directory so an unreachable server can never make the CLI read or mutate the stale host-side `~/.omniroute/storage.sqlite`. This is the load-bearing mitigation: measured, `keys list --output json` against a dead server returns **8 stale orphan records with exit 0**, and the same command with a pinned empty `DATA_DIR` returns `{"keys":[]}`.
- Rely on the CLI's own non-zero exit for server-dependent commands where it is set (`cost`, `health` both fail with an error), and NOT as a universal guarantee — several management commands silently succeed via the local DB branch.
- Multiplex the `omniroute()` shell function in `~/.zshrc` to forward CLI subcommands to `command omniroute "$@"` while preserving default Claude Code launcher behavior.

**Non-Goals:**
- Installing global npm packages into `/opt/homebrew` or host `node_modules` into `~/Omniroute`.
- Modifying Docker container packaging or running CLI commands via `docker exec`.
- Recompiling or altering upstream git-tracked files in `~/Omniroute`.

## Decisions

### 1. Bun Bridge Executable at `~/.local/bin/omniroute`
- **Choice**: Author `~/.local/bin/omniroute` using `#!/opt/homebrew/bin/bun`.
- **Rationale**:
  - `~/.local/bin` is already in `$PATH` (verified: entry `/Users/androidteam/.local/bin`), and no `omniroute` binary exists on it today (`command -v omniroute` returns nothing), so the bridge introduces a new name rather than shadowing an existing one.
  - Bun resolves dependencies into its **global cache** rather than a repo `node_modules`. Measured real cost of the rejected alternative: the published tarball unpacks to **546 MB across 26,761 files** (`npm view omniroute dist.unpackedSize dist.fileCount`), which supersedes the earlier ~420 MB estimate.
  - Cold start latency is ~0.25–1.6s, well within agent tool timeout budgets.
  - Avoids a global npm prefix and avoids triggering `inventory-workstation-toolchain.py` `DENY_ROSTER` rules — but it is **not** zero-footprint: dependencies are cache-resident (~1.0 GB cache observed) and a cold cache needs registry egress.
- **Alternatives considered**:
  - `npm install -g omniroute`: Rejected due to a measured 546 MB / 26,761-file payload, placement in a global npm prefix that the workstation toolchain inventory does not own, and duplication of dependencies already present in the Bun cache.
  - `npx -y omniroute`: Rejected due to measured 66-second latency per invocation and the same 546 MB unpack.

### 2. Stream-Level Banner Filtering for Stdout JSON Integrity
- **Choice**: In `~/.local/bin/omniroute`, spawn the child process with `stdio: ["inherit", "pipe", "inherit"]` and strip lines matching `/^[ 	]*📋 Loaded env from[^\n]*\n?/gm` from `stdout` before forwarding chunks to `process.stdout.write`.
- **Rationale**:
  - `bin/omniroute.mjs` executes `loadEnvFile()` before Commander parses CLI flags, so passing `--json`, `--output json`, or `--quiet` cannot prevent the banner from polluting stdout.
  - Filtering at the stream level guarantees that `omniroute health --json | jq .` succeeds reliably without patching git-tracked upstream files.
- **Alternatives considered**: Patching `bin/omniroute.mjs` directly. Rejected because it would dirty the git worktree of `~/Omniroute` and cause merge conflicts during upstream updates.

### 3. Interactive Shell Function Multiplexing in `~/.zshrc`
- **Choice**: Update `omniroute()` in `~/.zshrc` (line 313) to inspect `$1`:
  ```zsh
  omniroute() {
      case "$1" in
          health|models|providers|combo|combos|keys|resilience|doctor|serve|chat|repl|status|configure|connect|contexts|eval|memory|pricing|quota|nodes|simulate|cost|test|--help|-h|--version|-v)
              command omniroute "$@"
              return $?
              ;;
      esac
      if ! _claude_has; then
          echo "Error: claude not in PATH" >&2
          return 1
      fi
      _claude_require_helper "$HOME/.claude/helpers/omniroute-key.sh" "omniroute" || return 1
      (
          unset ANTHROPIC_AUTH_TOKEN
          export ANTHROPIC_BASE_URL="http://localhost:20128"
          _claude_with_profile "$HOME/.claude/profiles/omniroute-pm.json" "gemini-3.8-flash-high" "$@"
      )
  }
  ```
- **Rationale**:
  - In non-interactive subshells (where agent tool calls execute), functions in `~/.zshrc` are not loaded; the binary in `~/.local/bin/omniroute` is invoked directly.
  - In interactive terminals, users expect `omniroute health` or `omniroute --version` to execute the CLI, while entering `omniroute` with prompt arguments continues launching Claude Code per `claude-code-omniroute-pm-routing`.
- **Alternatives considered**: Renaming the CLI binary or renaming the Claude Code launcher. Rejected because both names are fixed conventions in their respective specs.

## Architecture

```
+─────────────────────────────────────────────────────────────────────────────+
|                         OmniRoute CLI Bridge Flow                           |
+─────────────────────────────────────────────────────────────────────────────+
|                                                                             |
|  Agent / Non-Interactive (zsh -c, bash -c)   Interactive Terminal (zsh)     |
|              │                                           │                  |
|              │                                           ▼                  |
|              │                          [ ~/.zshrc: omniroute() ]           |
|              │                          - Matches CLI subcommand/flag?      |
|              │                            ├─ YES ──> command omniroute "$@" |
|              │                            └─ NO  ──> Claude Code Launcher   |
|              │                                           │                  |
|              ▼                                           ▼                  |
|  [ ~/.local/bin/omniroute ] <────────────────────────────┘                  |
|  1. Normalize OMNIROUTE_BASE_URL (strip trailing /v1).                      |
|  2. Auto-hydrate OMNIROUTE_API_KEY from omniroute-key.sh if unset.          |
|  3. Pin DATA_DIR to an ephemeral dir (blocks stale host SQLite fallback).   |
|  4. Spawn: /opt/homebrew/bin/bun ~/Omniroute/bin/omniroute.mjs "$@".        |
|  5. Filter stdout: strip "📋 Loaded env from" and "[DB]" diagnostic lines.  |
|  6. Exit 3 (ServerOfflineError) when the container is unreachable.          |
|              │                                                              |
|              ▼ (HTTP API over Loopback)                                     |
|  http://127.0.0.1:20128                                                     |
|  Docker Container (`omniroute`, SQLite WAL on named volume)                 |
|                                                                             |
+─────────────────────────────────────────────────────────────────────────────+
```

## Risks / Trade-offs

| Risk | Mitigation |
| :--- | :--- |
| Upstream adds a new CLI subcommand not listed in the zsh multiplexer | Multiplexer covers all 25 top-level subcommands and standard flags; users can always use `command omniroute <subcmd>` for unlisted commands. |
| Upstream changes internal `bin/omniroute.mjs` path | `~/.local/bin/omniroute` references `/Users/androidteam/Omniroute/bin/omniroute.mjs`, which is the canonical repository entrypoint. |
| **Version skew (RESOLVED)**: checkout is refreshed to commit `fd95f823d` (v3.8.51) | Three-tier parity confirmed: checkout `3.8.51` == container `3.8.51` == npm `3.8.51`. Task 1.0 enforces this match before bridge creation. |
| **Stale host database fallback**: `~/.omniroute/storage.sqlite` (last written 2026-08-24) is a different database from the container volume | `DATA_DIR` is pinned to an ephemeral directory, so the DB branch never reaches the legacy path. Verified by mtime comparison in task 3.4. |
| Bun resolves dependencies into its ~1.0 GB global cache rather than a repo install | Accepted, and stated accurately: this is **not** zero-footprint. Dependencies already cached (`tsx@4.23.15`, `update-notifier@7.3.1`); the bridge adds no new dependency and performs no explicit install. |
| **Cold cache needs registry egress** | First invocation on a cold cache performs a one-time registry fetch; the change does not claim offline operation for that case. Task 1.4 confirms the cache is warm before relying on it. |
| **`bun --no-install` does not work here** — it fails with `Cannot find package 'update-notifier'` | The bridge deliberately relies on Bun auto-install (`--install=auto`). It must NOT pass `--no-install`, or every invocation would fail. |
| Offline invocation could return misleading empty or stale results | The `DATA_DIR` pin is the load-bearing control and is **proven**: dead server + default `DATA_DIR` returned 8 orphan records with exit 0; pinned `DATA_DIR` returned `{"keys":[]}`. Exit codes are secondary and not universal — `cost`/`health` fail loudly, but `keys`/`status`/`quota` succeed silently against the local branch. |
| Docker daemon offline | The bridge never reaches the container's SQLite and cannot corrupt the `omniroute-data` volume; it also cannot reach the stale host orphan once `DATA_DIR` is pinned. |
