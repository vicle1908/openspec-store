# Proposal

## Why

Real-feature end-to-end verification and official OMP `v18.14.2` documentation audits (`omp://`, Context7 `/can1357/oh-my-pi`, DeepWiki `can1357/oh-my-pi`) identified four additional optimization opportunities across `~/.omp/agent/` (`models.yml`, `config.yml`, `lsp.json`, `agent.db`) and four OpenSpec specifications (`omp-provider-routing`, `omp-fresh-shell-contract`, `lsp-user`, `lsp-python`) that must be captured and aligned:

1. **Argon Output Token Cap Mismatch (`~/.omp/agent/models.yml`)**: In OmniRoute's `model_capability_overrides` and upstream Antigravity definitions, `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `nx/gemini-4-argon` have an output ceiling of `65536` tokens. Declaring `maxTokens: 128000` in `~/.omp/agent/models.yml` causes OmniRoute to log `[CONTEXT] Adjusted invalid or oversized output token fields (max_tokens); ... (output ceiling in effect: 65536, antigravity/gemini-4-argon-high's own cap)` on every request and skews OMP's local output-reserve calculations.
2. **Multi-Language `xd://lsp` Discovery (`~/.omp/agent/lsp.json` & `config.yml`)**: In OMP `v18.14.2` (`packages/coding-agent/src/lsp/config.ts`), `BV(u)` only reads `servers` and `idleTimeoutMs` from `lsp.json` (requiring `lsp: { enabled: true, diagnosticsOnWrite: true, diagnosticsOnEdit: true, formatOnWrite: true }` in `config.yml`), and `eNe` filters servers by non-recursive `wZ(cwd, server.rootMarkers)` and executable path resolution. In addition to `gopls` (`/Users/androidteam/go/bin/gopls`), `basedpyright` (`/opt/homebrew/bin/basedpyright-langserver`, `python.version: "3.15"`), and `ruff` (`/opt/homebrew/bin/ruff`), the workstation also has `/usr/bin/sourcekit-lsp` (Swift/iOS) and `/Users/androidteam/.local/bin/yaml-language-server` (YAML) installed, which are filtered out in `/Users/androidteam/Developer` unless configured with `.git` and `.claude` in `rootMarkers`.
3. **Official OMP `v18.14.2` Context Promotion, Idle Compaction, Tiny Role & OAuth Pool Hygiene (`~/.omp/agent/config.yml`, `agent.db`)**:
   - Enabling `contextPromotion: { enabled: true }` allows OMP (`omp://compaction.md`) to promote overflowing turns from smaller-window models to 1M-window models before compacting.
   - Enabling `compaction.idleEnabled: true` (alongside `asyncEnabled: true`, `dropUseless: true`, `reserveTokens: 65536`, `keepRecentTokens: 40000`, `modelThresholds: { "cockpit/*": 220000 }`) and `bash.allowCompoundCommands: true` (alongside `gitGuard: true`) aligns `config.yml` with official OMP v18.14.2 best practices.
   - Setting `modelRoles.tiny: google-antigravity/gemini-3.8-flash:low`, ordering `omniroute/gemini-3.8-flash-high` and `smol` fallback chains to fail over to `google-antigravity/gemini-3.8-flash:high` before `google-antigravity/gemini-4-argon:high`, and pruning the newly 403-disabled `google-antigravity` OAuth credential `id=7` (`email:phamkive425@gmail.com`) leaves `13` active `200 OK` OAuth accounts and eliminates all `status=403` log warnings.
4. **OpenSpec Spec Drift (`omp-provider-routing`, `omp-fresh-shell-contract`, `lsp-user`, `lsp-python`)**: The main specs need to reflect the `65536` `maxTokens` ceiling on `gemini-4-argon*`, `modelRoles.tiny: google-antigravity/gemini-3.8-flash:low`, `contextPromotion.enabled: true`, `compaction.idleEnabled: true`, `bash.allowCompoundCommands: true`, the `config.yml` `lsp:` block, `13` healthy `google-antigravity` OAuth accounts, and the 5-server user-level `~/.omp/agent/lsp.json` (`gopls`, `basedpyright`, `ruff`, `sourcekit-lsp`, `yaml-language-server` with `.git` and `.claude` root markers and Python `3.15`).

### Non-Goals

- Modifying any application source code or OmniRoute container code.
- Changing `modelRoles.default` (`omniroute/gemini-4-argon`), `modelRoles.plan` (`google-antigravity/gemini-4-argon:high`), `modelRoles.advisor` (`google-antigravity/gemini-3.8-flash:high`), `modelRoles.smol` (`omniroute/gemini-3.8-flash-high:high`), or `modelRoles.judge` (`typesafe/jev-1.14.0`).

## What Changes

- **Align `gemini-4-argon*` `maxTokens: 65536` in `/Users/androidteam/.omp/agent/models.yml`**:
  - Update `maxTokens` from `128000` to `65536` on `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `nx/gemini-4-argon` under `providers.omniroute.models` (`mode 0600`).
- **Enable `contextPromotion`, `compaction.idleEnabled`, `bash.allowCompoundCommands`, `lsp`, and `tiny` role optimization in `/Users/androidteam/.omp/agent/config.yml`**:
  - Configure `contextPromotion: { enabled: true }`, `compaction.idleEnabled: true`, `compaction.asyncEnabled: true`, `compaction.dropUseless: true`, `bash.allowCompoundCommands: true`, `lsp: { enabled: true, diagnosticsOnWrite: true, diagnosticsOnEdit: true, formatOnWrite: true }`, `modelRoles.tiny: google-antigravity/gemini-3.8-flash:low`, and Flash-first failover on `omniroute/gemini-3.8-flash-high` and `smol` (`mode 0600`).
- **Expand `/Users/androidteam/.omp/agent/lsp.json` to 5 workstation language servers**:
  - Configure `gopls` (`/Users/androidteam/go/bin/gopls`), `basedpyright` (`/opt/homebrew/bin/basedpyright-langserver`, `python.version: "3.15"`), `ruff` (`/opt/homebrew/bin/ruff`, `isLinter: true`), `sourcekit-lsp` (`/usr/bin/sourcekit-lsp`), and `yaml-language-server` (`/Users/androidteam/.local/bin/yaml-language-server`, `--stdio`) with `.git` and `.claude` included in `rootMarkers` (`mode 0644`).
- **Reconcile OpenSpec specs (`omp-provider-routing`, `omp-fresh-shell-contract`, `lsp-user`, `lsp-python`) and sync Wiki + Notion + AgentMemory**:
  - Update all 4 capability specs to match the verified `omp v18.14.2` state, update `wiki/entities/omp.md`, and sync Notion (`40ac4b21-deb4-8159-b891-cb85a17a2d73` and `3e0c4b21-deb4-817a-ae9f-f9b7144cefb0`).

## Capabilities

### New Capabilities
*(None)*

### Modified Capabilities
- `omp-provider-routing`: Align `gemini-4-argon*` `maxTokens: 65536`, `modelRoles.tiny: google-antigravity/gemini-3.8-flash:low`, `contextPromotion.enabled: true`, `compaction.idleEnabled: true`, `bash.allowCompoundCommands: true`, `lsp` block in `config.yml`, and Flash-first fallback ordering on `omniroute/gemini-3.8-flash-high` and `smol`.
- `omp-fresh-shell-contract`: Update active `google-antigravity` OAuth account count to `13` after pruning banned `vicgnome19091@gmail.com`, `ascenddevtwo@gmail.com`, and `phamkive425@gmail.com`.
- `lsp-user`: Specify the 5 workstation language servers (`gopls`, `basedpyright`, `ruff`, `sourcekit-lsp`, `yaml-language-server`) with absolute binary paths and `.git`/`.claude` root markers in `~/.omp/agent/lsp.json`, plus `lsp` runtime flags in `~/.omp/agent/config.yml`.
- `lsp-python`: Align workspace Python LSP requirements to CPython `3.15` (`python.version: "3.15"`) via user-level `~/.omp/agent/lsp.json` (`basedpyright` + `ruff`) and workspace root markers (`.git`, `.claude`).

## Impact

- **Ownership Boundaries**: `/Users/androidteam/.omp/agent/{models.yml,config.yml,lsp.json,agent.db}`, `/Users/androidteam/Developer/platform/openspec-store/openspec/specs/{omp-provider-routing,omp-fresh-shell-contract,lsp-user,lsp-python}/spec.md`, `/Users/androidteam/Developer/wiki/entities/omp.md`, and Notion pages `40ac4b21-deb4-8159-b891-cb85a17a2d73` & `3e0c4b21-deb4-817a-ae9f-f9b7144cefb0`.
