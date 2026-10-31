# Verification Evidence: `optimize-omp-v18-14-runtime-and-ecosystem-alignment`

## 1. Pre-Flight Backups & Isolated-Profile Smoke Verification (Tasks 1.1–1.3)

- **Timestamped Backups (`Task 1.1`)**:
  - Directory: `/Users/androidteam/.omp/agent/backups/pre-v18-14-align-20261031T154928Z` (`mode 0700`)
  - Pre-flight MD5 hashes:
    - `models.yml`: `6d5d26b78741b4b236baf4fd1c9c6c74` (`9,853` B, `mode 0600`)
    - `config.yml`: `a2f0c020363f3ec0120b8ed172b991bb` (`3,480` B, `mode 0600`)
    - `mcp.json`: `cd6bafd1666b1fe4b6de5a30dbbe7314` (`252` B, `mode 0600`)
    - `lsp.json`: `311dc7b76afe9715996788b4440081c0` (`576` B, `mode 0644`)
    - `agent.db`: `bf4c81241039c4e3db39833c377b95db` (`11,141,120` B via `sqlite3 .backup`, `mode 0600`)
    - `models.db`: `9,707,520` B via `sqlite3 .backup` (`mode 0600`)
    - `.env`: `567` B (`mode 0600`)
- **Isolated Smoke Profile Staging & Catalog Validation (`Tasks 1.2–1.3`)**:
  - Staged at `/Users/androidteam/.omp/profiles/omp-v18-14-smoke/agent` (`mode 0700`); live MD5 hashes verified byte-identical after staging.
  - `omp --profile omp-v18-14-smoke models --kind all --json`:
    - `omniroute/gemini-4-argon`: `thinking: ["low", "medium", "high"]`
    - `omniroute/gemini-4-argon-high`: `thinking: ["low", "medium", "high"]`
    - `omniroute/gemini-4-argon-medium`: `thinking: ["low", "medium", "high"]`
    - `omniroute/gemini-4-argon-low`: `thinking: ["low", "medium", "high"]`
    - `omniroute/nx/gemini-4-argon`: `thinking: ["low", "medium", "high"]`
    - Available `ollama` models: `0`; available `openrouter` models: `0`.
  - Uncached `omp find` judge probes (`OMP_JUDGMENT_CACHE_DB` pointed to fresh temp files):
    - `zsh -lic`: `coverage="complete"`, `stats.requests=5`, `stats.failed=0`
    - Stripped `env -u ... zsh -fc`: `coverage="complete"`, `stats.requests=6`, `stats.failed=0`
  - Fallback-stripped attributed smoke probes (`--profile omp-v18-14-smoke --no-prewalk --no-skills --mode json --no-session --no-tools`):
    - `omniroute/gemini-4-argon`: `rc=0`, `provider="omniroute"`, `model="gemini-4-argon"`, `text="pong"`, `fallbacks=0`
    - `omniroute/gemini-3.8-flash-high`: `rc=0`, `provider="omniroute"`, `model="gemini-3.8-flash-high"`, `text="pong"`, `fallbacks=0`
    - `google-antigravity/gemini-4-argon:high`: `rc=0`, `provider="google-antigravity"`, `model="gemini-4-argon"`, `text="pong"`, `fallbacks=0`

## 2. Live Catalog & Runtime Configuration Rollout (Tasks 2.1–2.2)

- **`/Users/androidteam/.omp/agent/models.yml` (`Task 2.1`)**:
  - Atomically replaced (`mode 0600`, MD5 `b8df38f7ca020bf99fc82f9637a51c3c`).
  - `providers.omniroute.headers`: `{"x-omniroute-no-memory": "true"}`
  - `providers.omniroute.compat`: `{"supportsReasoningEffort": true, "supportsDeveloperRole": true}`
  - `providers.omniroute-anthropic.headers`: `{"x-omniroute-no-memory": "true"}`
  - Root `equivalence` key removed; no `promptCache` keys on `omniroute` models; `providers.cockpit.models` verified at `10` text-only models.
- **`/Users/androidteam/.omp/agent/config.yml` (`Task 2.2`)**:
  - Atomically replaced (`mode 0600`, MD5 `22d73307c8611622014c86333d9d7f55`, `config.yml.lock` preserved untouched).
  - `modelRoles`: `default: omniroute/gemini-4-argon`, `plan: google-antigravity/gemini-4-argon:high`, `smol: omniroute/gemini-3.8-flash-high:high`, `judge: typesafe/jev-1.14.0` (`modelRoles.memory` omitted).
  - `disabledProviders`: `["openrouter", "lm-studio", "llama.cpp", "vscode", "ollama"]`
  - `prewalk`: `{"enabled": false, "auto": "off", "into": "@smol", "autoTarget": "@smol"}`
  - `title`: `{"generator": "tiny"}`, `memories`: `{"stage1Concurrency": 2}`
  - `compaction`: `{"enabled": true, "reserveTokens": 65536, "keepRecentTokens": 40000, "autoContinue": true, "handoffSaveToDisk": true, "modelThresholds": {"cockpit/*": 220000}}`
  - `bash`: `{"autoBackground": {"enabled": true}, "gitGuard": true}`
  - `retry`: `rateLimitWalksChain: true`, `usageAwareFallback: true`, `usageReservePolicy: "auto"`, plus `advisor`, `smol`, and `omniroute/*` fallback chains.

## 3. Credential Store Hygiene, Profile Cleanup, MCP & LSP Alignment (Tasks 3.1–3.3)

- **`/Users/androidteam/.omp/agent/agent.db` (`Task 3.1`)**:
  - Deleted `1` row (`identity_key='email:vicgnome19091@gmail.com'`) inside `PRAGMA busy_timeout=5000; BEGIN IMMEDIATE;`.
  - Read-only verification: `rejected_cnt=0`, `active_agy=15`, `typesafe=[('typesafe', 'api_key', 'login', 107)]`, `openrouter=0`.
- **`/Users/androidteam/.omp/profiles` (`Task 3.2`)**:
  - Removed `omp-v18-14-smoke`, `omp-fresh-cockpit`, `omp-fresh-giaoduc`, and `omp-fresh-shopapikey`.
- **`/Users/androidteam/.omp/agent/mcp.json` & `lsp.json` (`Task 3.3`)**:
  - `mcp.json` (`mode 0600`): Added `"$schema": "https://raw.githubusercontent.com/can1357/oh-my-pi/main/packages/coding-agent/src/config/mcp-schema.json"`, `"type": "stdio"`, `"timeout": 300000`; preserved existing 37-char `env.MCPR_TOKEN`.
  - `lsp.json` (`mode 0644`): Updated `servers.basedpyright.settings["python.version"]` to `"3.15"`.

## 4. Live End-to-End Smoke Verification & Knowledge Sync (Tasks 4.1–4.2)

- **Live End-to-End Smoke Verification (`Task 4.1`)**:
  - `default (lic)`: `rc=0`, `provider="omniroute"`, `model="gemini-4-argon"`, `text="pong"`, `fallbacks=0`
  - `smol (lic)`: `rc=0`, `provider="omniroute"`, `model="gemini-3.8-flash-high"`, `text="pong"`, `fallbacks=0`
  - `advisor (lic)`: `rc=0`, `provider="omniroute"`, `model="gemini-3.8-flash-high"`, `text="pong"`, `fallbacks=0`
  - `default (fc)`: `rc=0`, `provider="omniroute"`, `model="gemini-4-argon"`, `text="pong"`, `fallbacks=0`
  - Live uncached `omp find` (`lic`): `coverage="complete"`, `requests=5`, `failed=0`
  - Live uncached `omp find` (`fc`): `coverage="complete"`, `requests=7`, `failed=0`
  - Newly created session logs (`omp.2026-10-31.{72044,72450,72926,73262,73664,73983}.log`): `0` occurrences of `403` or `vicgnome19091`.
- **Wiki & Notion Sync (`Task 4.2`)**:
  - Updated `/Users/androidteam/Developer/wiki/entities/omp.md` and ran `/Users/androidteam/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh --section entities` -> Notion page `40ac4b21-deb4-8159-b891-cb85a17a2d73` verified via `ntn pages get`.
