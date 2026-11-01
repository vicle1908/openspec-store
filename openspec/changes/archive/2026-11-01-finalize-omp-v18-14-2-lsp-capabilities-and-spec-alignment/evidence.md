# Verification Evidence: `finalize-omp-v18-14-2-lsp-capabilities-and-spec-alignment`

## 1. Catalog, Runtime Config & Multi-Language LSP Rollout (Tasks 1.1–1.3)

- **`/Users/androidteam/.omp/agent/models.yml` (`Task 1.1`)**:
  - Updated `maxTokens` from `128000` to `65536` on `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `nx/gemini-4-argon` (`mode 0600`).
  - `omp models --json` verified all 5 `gemini-4-argon*` models report `maxTokens: 65536` and `thinking: ["low", "medium", "high"]`.
- **`/Users/androidteam/.omp/agent/config.yml` (`Task 1.2`)**:
  - Updated `contextPromotion: { enabled: true }`, `compaction` (`reserveTokens: 65536`, `keepRecentTokens: 40000`, `idleEnabled: true`, `asyncEnabled: true`, `dropUseless: true`, `modelThresholds: { "cockpit/*": 220000 }`), `bash` (`autoBackground: { enabled: true }`, `gitGuard: true`, `allowCompoundCommands: true`), `lsp` (`enabled: true`, `diagnosticsOnWrite: true`, `diagnosticsOnEdit: true`, `formatOnWrite: true`), `modelRoles.tiny: google-antigravity/gemini-3.8-flash:low`, and Flash-first failover on `omniroute/gemini-3.8-flash-high` and `smol` (`mode 0600`, `config.yml.lock` preserved untouched).
- **`/Users/androidteam/.omp/agent/lsp.json` & `agent.db` (`Task 1.3`)**:
  - Configured 5 language servers (`gopls`, `basedpyright` with `python.version: "3.15"`, `ruff`, `sourcekit-lsp`, `yaml-language-server`) with `.git` and `.claude` in `rootMarkers` (`mode 0644`).
  - Read-only `agent.db` check confirmed `banned_cnt=0` for `vicgnome19091@gmail.com`, `ascenddevtwo@gmail.com`, and `phamkive425@gmail.com`, and `active_agy=13` (`13/13` returning HTTP 200 on both `retrieveUserQuota` and `fetchAvailableModels`).

## 2. End-to-End Verification, Documentation & OpenSpec Closure (Tasks 2.1–2.2)

- **Multi-Language `xd://lsp` Verification (`Task 2.1`)**:
  - `xd://lsp` `reload`: `Reloaded gopls, basedpyright, ruff, sourcekit-lsp, yaml-language-server`
  - `xd://lsp` `status`: `Language servers: gopls (ready), basedpyright (ready), ruff (ready), sourcekit-lsp (ready), yaml-language-server (ready)`
  - `xd://lsp` `symbols` on `platform/openspec-store/openspec/config.yaml`: returned YAML document symbols (`schema`, `context`, `operations`, `rules`) via `yaml-language-server`.
  - Live `omniroute/gemini-4-argon` probe (`PID 50551`): `rc=0`, `provider="omniroute"`, `model="gemini-4-argon"`, `0` OmniRoute `[CONTEXT] Adjusted invalid or oversized output token fields` warnings, `0` errors or `status=403` warnings in `omp.2026-11-01.50551.log`, and `contextPromotionEnabled: true` confirmed in `Auto-compaction threshold decision`.
