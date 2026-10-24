# Implementation Evidence: `optimize-omniroute-rtk-and-combo-resilience`

## 1. Compression, Adaptive Context Budget, Thinking Budget, Cache, Database & Feature Flag Verification (Tasks 1.1–1.4)

- **`GET /api/settings/compression` & `GET /api/context/rtk/config`**:
  ```json
  {
    "enabled": true,
    "preserveSystemPrompt": true,
    "engines.rtk": { "enabled": true, "level": "minimal" },
    "rtkConfig.enabled": true,
    "rtkConfig.intensity": "minimal",
    "rtkConfig.applyToToolResults": true,
    "contextBudget": {
      "mode": "replace-autotrigger",
      "policy": "reserve-output",
      "outputReserve": 4096,
      "safetyMargin": 1024,
      "pct": 0.85,
      "absoluteBudget": 0
    },
    "contextEditing": { "enabled": true }
  }
  ```
- **`POST /api/context/rtk/test` (`"command": "vitest run"`)**:
  ```json
  {
    "detection": {
      "type": "test-vitest",
      "command": "vitest run",
      "confidence": 1,
      "category": "test"
    },
    "originalTokens": 75,
    "compressedTokens": 39,
    "rulesApplied": ["test-vitest:strip", "test-vitest:keep", "test-vitest:collapse"]
  }
  ```
- **`GET /api/settings/thinking-budget`**:
  ```json
  {
    "mode": "passthrough",
    "customBudget": 10240,
    "effortLevel": "medium"
  }
  ```
- **`GET /api/settings/cache-config` & `GET /api/settings/database`**:
  ```json
  {
    "embeddingProvider": "voyage-ai",
    "embeddingModel": "voyage-code-3",
    "embeddingDim": 1024,
    "backup": {
      "autoBackupEnabled": true,
      "autoBackupFrequency": "daily",
      "keepLastNBackups": 5
    }
  }
  ```
- **`GET /api/settings/feature-flags` (5 v3.8.52 Resilience Flags)**:
  ```json
  {
    "CREDENTIAL_GATE_AUTH_DIAGNOSES_ONLY": ["true", "db"],
    "ANTIGRAVITY_ACCOUNT_LEASE_ENABLED": ["true", "db"],
    "COMBO_EMPTY_POOL_NO_ELIGIBLE_TARGETS_ENABLED": ["true", "db"],
    "STREAM_LATE_OUTPUT_PROBE_ENABLED": ["true", "db"],
    "RETRY_AFTER_PROVENANCE_ENABLED": ["true", "db"]
  }
  ```

## 2. Combo Routing, Dual Quota-Cache Keys, Bridge Port `20129` & Connection Hygiene Verification (Tasks 2.1–2.3)

- **`GET /api/combos` Summary Across All 8 Combos**:
  - `gemini-3.8-flash-high`: `strategy=auto`, `context_cache_protection=false`, `resetWindowQuotaCacheTtlMs=300000`, `resetAwareQuotaCacheTtlMs=300000`, `models=15`
  - `gemini-4-argon`: `strategy=auto`, `context_cache_protection=false`, `resetWindowQuotaCacheTtlMs=300000`, `resetAwareQuotaCacheTtlMs=300000`, `models=2` (`338764b8-1cd7-4946-b789-ee5dad4c5073` `vinhghtk1908@gmail.com` and `0532bad4-2486-4286-8f06-510e9c678620` `vinhvumobile@gmail.com`)
  - `gemini-4-argon-high`: `strategy=auto`, `context_cache_protection=false`, `resetWindowQuotaCacheTtlMs=300000`, `resetAwareQuotaCacheTtlMs=300000`, `models=2` (`338764b8`, `0532bad4`)
  - `gemini-4-argon-medium`: `strategy=auto`, `context_cache_protection=false`, `resetWindowQuotaCacheTtlMs=300000`, `resetAwareQuotaCacheTtlMs=300000`, `models=2` (`338764b8`, `0532bad4`)
  - `gemini-4-argon-low`: `strategy=auto`, `context_cache_protection=false`, `resetWindowQuotaCacheTtlMs=300000`, `resetAwareQuotaCacheTtlMs=300000`, `models=2` (`338764b8`, `0532bad4`)
  - `muse-spark-1.3`: `strategy=priority`, `context_cache_protection=false`, `nestedComboMode=execute`, `resetWindowQuotaCacheTtlMs=300000`, `resetAwareQuotaCacheTtlMs=300000`, `models=2`
  - `claude-opus-5.5`: `strategy=auto`, `context_cache_protection=false`, `nestedComboMode=flatten`, `resetWindowQuotaCacheTtlMs=300000`, `resetAwareQuotaCacheTtlMs=300000`, `models=9` (8 active `agy/claude-opus-5-5-high` connections + 1 `combo-ref: gemini-3.8-flash-high`)
  - `phanmemvip`: `strategy=round-robin`, `context_cache_protection=true`, `models=1` (`anthropic-compatible-6408e370-2373-4ae0-9942-7f4095ba976c/Claude-Fable`)
- **Provider Connection Hygiene**:
  - Expired `codex` connection `0ee99889-6643-4fe8-a68a-6c4350de961f`: `isActive: false`.
  - `muse-code` connection `51795cf9-4c03-4c22-af9d-9ce4de975dc1`: preserved `isActive: true` so `/v1/muse-code/models` and `/muse-code/models` serve the 40-model catalog (`muse-spark-1.3` first).
- **Container Bridge Port `20129` (`API_HOST=0.0.0.0` in `~/Omniroute/docker-compose.override.yml`)**:
  - Recreated `omniroute-base` under `/usr/bin/lockf` on `~/.omniroute/update.lock` and verified `ensure-muse-wire-compat.sh omniroute` (`Muse Code wire-compat normalization verified (already_ok)`).
  - `GET http://127.0.0.1:20129/v1/models` $\rightarrow$ `200 OK`, `count: 1157`.

## 3. OmniRoute Skill Enhancements & Workspace Skill Surface Verification (Tasks 3.1–3.3)

- **Enhanced `~/.agents/skills/*/SKILL.md` Line Counts (all $\le 500$ lines, wrapped in `<!-- skill:custom-start -->` / `<!-- skill:custom-end -->`)**:
  - `omni-compression`: 155 lines
  - `omni-context-rtk`: 147 lines
  - `omni-combos-routing`: 223 lines
  - `omni-settings`: 203 lines
  - `omni-resilience`: 164 lines
  - `omni-auth`: 168 lines
  - `omni-inference`: 464 lines
  - `omni-providers`: 145 lines
  - `cli-health`: 97 lines
  - `cli-keys`: 237 lines
  - `cli-routing`: 110 lines
- **`sync-workspace-agent-skills.py --check` Output**:
  ```text
  canonical_direct_roots=111 containers=2 codex_selected=66 claude_selected=25 hermes_selected=6 openspec_targets=12 claude_commands=12 check=True
  containers=generated,gitnexus
  malformed_entries=0
  workspace_agents: created=0 removed=0 conflicts=0 broken=0
  user_agents: created=0 removed=0 conflicts=0 broken=0
  workspace_claude_skills: created=0 removed=0 conflicts=0 broken=0
  user_claude_skills: created=0 removed=0 conflicts=0 broken=0
  user_hermes_skills: created=0 removed=0 conflicts=0 broken=0
  workspace_claude_commands: created=0 removed=0 conflicts=0 broken=0
  user_claude_commands: created=0 removed=0 conflicts=0 broken=0
  snapshot_check=ok
  ```

## 4. Live Loopback Inference Smoke Tests Across Ports `20128` and `20129` (Task 4.1)

- `POST http://127.0.0.1:20128/v1/chat/completions` (`model: "gemini-3.8-flash-high"`) $\rightarrow$ `200 OK`, `id: chatcmpl-1792821308449-a083df72`, `reply: "PONG"`
- `POST http://127.0.0.1:20129/v1/chat/completions` (`model: "gemini-3.8-flash-high"`) $\rightarrow$ `200 OK`, `id: chatcmpl-1792821320281-11048644`, `reply: "PONG"`
- `POST http://127.0.0.1:20128/v1/chat/completions` (`model: "gemini-4-argon"`) $\rightarrow$ `200 OK`, `id: chatcmpl-1792821326773-f5a79e50`, `reply: "PONG"`
- `POST http://127.0.0.1:20129/v1/chat/completions` (`model: "gemini-4-argon"`) $\rightarrow$ `200 OK`, `id: chatcmpl-1792821345303-c8bcbf77`, `reply: "PONG"`
- `POST http://127.0.0.1:20128/v1/chat/completions` (`model: "muse-spark-1.3"`) $\rightarrow$ `200 OK`, `id: chatcmpl-1792821348215-0e3a190e`, `reply: "PONG"`
- `POST http://127.0.0.1:20128/v1/chat/completions` (`model: "claude-opus-5.5"`) $\rightarrow$ `200 OK`, `id: chatcmpl-1792821351303-1628f44a`, `reply: "PONG"`
