# Design

## Context

See `proposal.md - Why`.

## Goals / Non-Goals

**Goals:**
- Align `maxTokens: 65536` on `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `nx/gemini-4-argon` in `/Users/androidteam/.omp/agent/models.yml` to match OmniRoute's `model_capability_overrides` and Antigravity's 65,536-token output ceiling.
- Configure all 5 installed workstation language servers (`gopls`, `basedpyright`, `ruff`, `sourcekit-lsp`, `yaml-language-server`) in `/Users/androidteam/.omp/agent/lsp.json` with absolute binary paths and `.git` + `.claude` root markers, paired with `lsp: { enabled: true, diagnosticsOnWrite: true, diagnosticsOnEdit: true, formatOnWrite: true }` in `/Users/androidteam/.omp/agent/config.yml`.
- Enable official OMP `v18.14.2` context and execution optimizations (`contextPromotion.enabled: true`, `compaction.idleEnabled: true`, `compaction.asyncEnabled: true`, `compaction.dropUseless: true`, `bash.allowCompoundCommands: true`, `modelRoles.tiny: google-antigravity/gemini-3.8-flash:low`, and Flash-first failover on `omniroute/gemini-3.8-flash-high` and `smol`).
- Reconcile `omp-provider-routing`, `omp-fresh-shell-contract`, `lsp-user`, and `lsp-python` in `openspec-store`.

**Non-Goals:**
- Modifying any application source code or OmniRoute container code.

## Decisions

### 1. `maxTokens: 65536` on All 5 `gemini-4-argon*` Models in `models.yml`
- **Decision**: Set `maxTokens: 65536` on `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `nx/gemini-4-argon` in `/Users/androidteam/.omp/agent/models.yml`.
- **Rationale**: In OmniRoute's `model_capability_overrides` SQLite table and upstream Antigravity definitions, `gemini-4-argon*` has a 65,536-token output limit. Declaring `128000` in `models.yml` triggers OmniRoute's `[CONTEXT] Adjusted invalid or oversized output token fields (max_tokens)` log warning on every turn and skews OMP's local output-reserve calculations.

### 2. Five-Server `~/.omp/agent/lsp.json` + `config.yml` `lsp:` Namespace
- **Decision**: Configure `gopls` (`/Users/androidteam/go/bin/gopls`), `basedpyright` (`/opt/homebrew/bin/basedpyright-langserver`, `python.version: "3.15"`), `ruff` (`/opt/homebrew/bin/ruff`, `isLinter: true`), `sourcekit-lsp` (`/usr/bin/sourcekit-lsp`), and `yaml-language-server` (`/Users/androidteam/.local/bin/yaml-language-server`, `args: ["--stdio"]`) in `/Users/androidteam/.omp/agent/lsp.json` with `.git` and `.claude` appended to `rootMarkers`, and set `lsp: { enabled: true, diagnosticsOnWrite: true, diagnosticsOnEdit: true, formatOnWrite: true }` in `/Users/androidteam/.omp/agent/config.yml`.
- **Rationale**: In OMP `v18.14.2` (`packages/coding-agent/src/lsp/config.ts`), `BV(u)` reads only `servers` and `idleTimeoutMs` from `lsp.json` while runtime flags (`diagnosticsOnWrite`, `diagnosticsOnEdit`, `formatOnWrite`) are read from `config.yml`, and `eNe` filters servers by non-recursive `wZ(cwd, server.rootMarkers)`. Adding `.git` and `.claude` to `rootMarkers` allows all 5 installed workstation language servers to initialize when OMP starts in `/Users/androidteam/Developer`, while `ensureWorkspaceFolder()` dynamically attaches individual sub-repositories via `workspace/didChangeWorkspaceFolders`.

### 3. Official `v18.14.2` Context Promotion, Idle Compaction, and Compound Bash Settings
- **Decision**: Enable `contextPromotion: { enabled: true }`, `compaction.idleEnabled: true`, `compaction.asyncEnabled: true`, `compaction.dropUseless: true`, and `bash.allowCompoundCommands: true` in `/Users/androidteam/.omp/agent/config.yml`.
- **Rationale**: Per `omp://compaction.md` and `omp config list --json`, `contextPromotion.enabled: true` promotes overflowing turns to larger-context models before compacting, `compaction.idleEnabled: true` + `asyncEnabled: true` + `dropUseless: true` keep long-running sessions within prefix budgets without blocking active turns, and `bash.allowCompoundCommands: true` allows safe `&&` inspection pipelines while keeping `bash.gitGuard: true` and `bashInterceptor.enabled: true`.

## Risks / Trade-offs

- **[Risk] Concurrent OMP processes reading `models.yml`, `config.yml`, or `lsp.json` during update** → **Mitigation**: Use same-directory temp files + `os.replace` (`mode 0600` on `models.yml` and `config.yml`, `mode 0644` on `lsp.json`, preserving `config.yml.lock` untouched).
