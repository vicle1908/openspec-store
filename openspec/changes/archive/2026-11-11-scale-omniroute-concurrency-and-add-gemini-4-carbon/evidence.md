# Evidence: `scale-omniroute-concurrency-and-add-gemini-4-carbon`

- **Change**: `scale-omniroute-concurrency-and-add-gemini-4-carbon`
- **Date**: 2026-11-11
- **Gateway Version**: `diegosouzapw/omniroute@sha256:b52a1766a1aff42fb78f3494e236f98dc55b57274f28559f8387622eef8eed` (`v3.8.53`)
- **Upstream Git State**: `HEAD = 094a1aa1c` (`0` commits ahead, `0` commits behind `origin/main`; `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` returns 0 lines)
- **Pre-Mutation SQLite Snapshot**: `/Users/androidteam/.omniroute/snapshots/pre-carbon-concurrency-20261111-015747.sqlite` (`117,268,480` bytes, `PRAGMA quick_check = ok`)
- **Backup Manifest**: `/Users/androidteam/.omniroute/backups/scale-omniroute-concurrency-and-add-gemini-4-carbon/sha256-manifest.json` (`mode 0600`)

---

## 1. Gateway Concurrency & Runtime Customization Verification

- **Configuration Variables Applied (`/Users/androidteam/Omniroute/.env:799-813` & `/Users/androidteam/Omniroute/docker-compose.override.yml:18-22`)**:
  - `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=32` (`32` primary heavy slots + `32` healthy-heap headroom slots = `64` immediate heavy request streams)
  - `OMNIROUTE_CHAT_ADMISSION_MAX_QUEUED_BYTES=67108864` (`64 MB` parked queue byte cap)
  - `OMNIROUTE_CHAT_MAX_INFLIGHT_BYTES=268435456` (`256 MB` active in-flight body byte cap)
  - `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=30000` (`30,000 ms` queue fairness wait)
  - `UV_THREADPOOL_SIZE=32` (`32` libuv worker threads)
- **Container Recreation & Runtime Patch Verification**:
  - Recreated under `/usr/bin/lockf -s -t 60 /Users/androidteam/.omniroute/update.lock` (`docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base`).
  - `/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh omniroute` → `Muse Code wire-compat normalization verified (already_ok)`.
  - `docker exec omniroute sh /app/container-entrypoint-compat.sh --patch-only` → `already_ok`.
  - Gate 8b probe (`/Users/androidteam/Omniroute/scripts/update.sh:456-520`) → `MEM_OFF|CACHE_ALIGNED|COMP_OFF|TTFT_ZERO|PATCH_OK`.

---

## 2. SQLite Capability Overrides, 15-Combo Pool Isolation, & Resilience Settings

- **Capability & Context Overrides (`PATCH /api/model-capability-overrides` -> `/app/data/storage.sqlite`)**:
  - `antigravity/gemini-4-carbon-high`: `context_length=1048576`, `max_input_tokens=1048576`, `max_output_tokens=262144`, `reasoning_efforts=["low","medium","high"]`
  - `antigravity/gemini-4-carbon-medium`: `context_length=1048576`, `max_input_tokens=1048576`, `max_output_tokens=262144`, `reasoning_efforts=["low","medium","high"]`
  - `antigravity/gemini-4-carbon-low`: `context_length=1048576`, `max_input_tokens=1048576`, `max_output_tokens=262144`, `reasoning_efforts=["low","medium","high"]`
- **Catalog Verification (`GET http://127.0.0.1:20128/v1/models`)**:
  - All 14 active combos advertised (`owned_by: "combo"`), with `gemini-4-carbon{,-high,-medium,-low}` advertising `context_length: 1000000`, `max_output_tokens: 262144`, and `effort_tiers: ["low", "medium", "high"]`.
- **15 Active Combos in `/app/data/storage.sqlite` (`combos` table)**:

| Combo Name | Strategy | Steps | Pool / Target Accounts | Floor (%) | `predictiveTtftMs` | `targetTimeoutMs` |
|---|---|---|---|---|---|---|
| `gemini-4-carbon` | `quota-weighted` | 3 | 3 Ultra (`0532bad4`, `338764b8`, `62af823b`) -> `agy/gemini-4-carbon-high` | `5` | `0` | `180000` |
| `gemini-4-carbon-high` | `quota-weighted` | 3 | 3 Ultra (`0532bad4`, `338764b8`, `62af823b`) -> `agy/gemini-4-carbon-high` | `5` | `0` | `180000` |
| `gemini-4-carbon-medium` | `quota-weighted` | 3 | 3 Ultra (`0532bad4`, `338764b8`, `62af823b`) -> `agy/gemini-4-carbon-medium` | `5` | `0` | `180000` |
| `gemini-4-carbon-low` | `quota-weighted` | 3 | 3 Ultra (`0532bad4`, `338764b8`, `62af823b`) -> `agy/gemini-4-carbon-low` | `5` | `0` | `180000` |
| `gemini-4-argon` | `quota-weighted` | 3 | 3 Ultra (`0532bad4`, `338764b8`, `62af823b`) -> `agy/gemini-4-argon-high` | `5` | `0` | `180000` |
| `gemini-4-argon-high` | `quota-weighted` | 3 | 3 Ultra (`0532bad4`, `338764b8`, `62af823b`) -> `agy/gemini-4-argon-high` | `5` | `0` | `180000` |
| `gemini-4-argon-medium` | `quota-weighted` | 3 | 3 Ultra (`0532bad4`, `338764b8`, `62af823b`) -> `agy/gemini-4-argon-medium` | `5` | `0` | `180000` |
| `gemini-4-argon-low` | `quota-weighted` | 3 | 3 Ultra (`0532bad4`, `338764b8`, `62af823b`) -> `agy/gemini-4-argon-low` | `5` | `0` | `180000` |
| `gemini-3.8-flash-high` | `quota-weighted` | 11 | 11 Active Pro (`38782750`, `9d66311f`, `ce95e1cb`, `9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`) | `1` | `0` | `120000` |
| `claude-opus-5.5` | `quota-weighted` | 11 | 11 Active Pro (9 on `agy/claude-opus-5-5-high` + 2 on `agy/claude-opus-4-6-thinking`) | `1` | `0` | `180000` |
| `claude-sonnet-5.5` | `quota-weighted` | 11 | 11 Active Pro (9 on `agy/claude-sonnet-5-5-high` + 2 on `agy/claude-sonnet-4-6`) | `1` | `0` | `120000` |
| `deepseek-v4.1-flash` | `priority` | 3 | `nx` -> `ollama` -> `or` | — | `0` | `120000` |
| `kimi-k3.1-pro` | `priority` | 3 | `kmc` -> `ollama` -> `or` | — | `0` | `120000` |
| `muse-spark-1.3` | `priority` | 1 | `meta/muse-spark-1.3` | — | `0` | `25000` |
| `phanmemvip` | `round-robin` | 1 | `pm/Claude-Fable` | — | `0` | — |

- **Rate-Limit Protection & Request Queue (`POST /api/rate-limits` & `PATCH /api/resilience`)**:
  - All 14 active `agy` connections in `provider_connections` have `rate_limit_protection = 0`.
  - `GET /api/resilience` (`settings.resilienceSettings.requestQueue`) confirms `concurrentRequests: 64`, `requestsPerMinute: 600`, `maxWaitMs: 15000`.
  - `GET /api/settings/feature-flags` confirms `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED: "false"` and `COMBO_AUTO_PRUNE_STALE_STEPS: "false"`.
- **`gemini-3.8-flash-high` Timeout & 11/11 Pro Account Resolution**:
  - `config.targetTimeoutMs` is set to `120000` (`120,000 ms`, raised from `25,000 ms`) so large-context `effort=high` agent turns do not prematurely abort at 25s and trigger `modelLockout` cascades.
  - Verified active `11/11` (`Trying model 1/11`) Pro account UUID resolution (`38782750-7a60-46d4-ae3f-e8c13cda296b`, `9d66311f-9db7-49b2-90f5-277c5f311f2a`, `ce95e1cb-27a4-433f-9c50-bdb6ad0b6b6b`, `9c033d6f-ec87-42f7-9e8a-e42858a7644c`, `37f9924d-7480-44e5-9c2e-f04b10cc2de1`, `573e3f41-5d58-4e3f-9af3-4cb4efffb721`, `3f3085b1-a0f3-4771-b500-c3747bea3bd1`, `a94216f4-907f-4aec-a38d-e5250697f258`, `a7580e21-ff65-41b8-a7be-c44b26b91546`, `f511d061-dacc-4b6e-9dd9-7a56dad76c36`, `9ad0a196-a8c7-450e-9516-06df2b29125a`).

---

## 3. Parallel Burst & Live Carbon Inference Verification (`call_logs`)

1. **`resetAwareQuotaCache` Warm-Up**:
   - Single warm-up probes across `gemini-4-carbon`, `gemini-4-argon`, `gemini-3.8-flash-high`, `claude-opus-5.5`, and `claude-sonnet-5.5` all returned `HTTP 200` (`OK`).
2. **20-Request Concurrent Burst (`gemini-3.8-flash-high`)**:
   - `20/20 HTTP 200` (`1,932 ms – 5,585 ms`), `0` `503 chat_admission_busy`, `0` `429`.
   - `call_logs` distribution across 8 distinct Pro accounts (`0` Ultra calls): `37f9924d` (4), `f511d061` (4), `3f3085b1` (3), `573e3f41` (2), `9c033d6f` (2), `a7580e21` (2), `a94216f4` (2), `9ad0a196` (1).
3. **6-Request Concurrent Carbon Burst (`gemini-4-carbon{,-high,-medium,-low}`)**:
   - `6/6 HTTP 200` including `max_tokens: 200000` (`> 65536`) on `gemini-4-carbon-high` and `max_tokens: 131072` on `gemini-4-carbon`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low`.
   - `call_logs` distribution across healthy Ultra accounts: `338764b8` (`vinhghtk1908@gmail.com`, 5 calls) and `0532bad4` (`vinhvumobile@gmail.com`, 1 call), while `62af823b` (`vicgnome19094@gmail.com`, `3.7% < 5%` floor) received `0` calls.

---

## 4. 18-File Pre/Post SHA-256 Backup & Workstation Client Rollout Register

| # | Target File | Mode | Pre-Mutation SHA-256 | Post-Mutation SHA-256 | Verification Notes |
|---|---|---|---|---|---|
| 1 | `/Users/androidteam/Omniroute/.env` | `0600` | `acf794d64553c9e6aef5d49709bfb556f96ce00c49b20aab38cfecb623bbd6da` | `8146c9845b1dfe3cac2226ccbac406d217eff1c8b850c285ccc949b13ce49ce1` | 5 concurrency vars scaled (`32` heavy, `64 MB` queue, `256 MB` inflight, `30s`, `UV_THREADPOOL_SIZE=32`) |
| 2 | `/Users/androidteam/Omniroute/docker-compose.override.yml` | `0644` | `6b716d7cb06768527e58a4c531b1f87fd1413e42ad949ea32b7fc5268da303e1` | `55c16df4fe2fb34c22061e632e57009ad66d6ec7771e66786da714a58dde3494` | Propagated 5 env vars under `omniroute-base` |
| 3 | `/Users/androidteam/.omp/agent/models.yml` | `0600` | `865b4fd91eecb9d2f2d4ffa099f38058cb15fb5a6fe68b838c9e7f7730e1cd1e` | `8aec9462925ee649860783fe813354293dce9f9a96e9805c057ea554ee003e12` | Surgical `+68/-0` lines: 4 Carbon models (`maxTokens: 262144`, `efforts: [low, medium, high]`) |
| 4 | `/Users/androidteam/.omp/agent/config.yml` | `0600` | `a174062249f770d9c6d7a6d502c5528d13d2476efd70673ed5e04c6b43a89377` | `224cc4d92d93070bb9f8f10f07591325bdefb062caa110d2b00a821139ba46e9` | Surgical `+12/-0` lines: 4 per-model `retry.fallbackChains` keys; `default: omniroute/gemini-4-argon` preserved |
| 5 | `/Users/androidteam/.pi/agent/models.json` | `0600` | `db27aa2ede0ac4c0f822edd96d7907962d962e3e20a32cb27657ace6182fe528` | `ee502fd35decee4d06e44fa752f6c8783e16b1ea409f62dbda657145cfd03f12` | 4 Carbon entries under `omniroute-responses` (`maxTokens: 262144`, `x-omniroute-no-memory: "true"`) |
| 6 | `/Users/androidteam/.prime/agent/models.json` | `0600` | `f68cdc02d7e5bc1f75ecb08d381971db86f4654aab831013654dde417bf2b647` | `d8bb9a89ded75aa4f71b033ad72dc331ffc8236cc5af0455d25fe8d49a94bccf` | 4 Carbon entries under `omniroute-responses` (`maxTokens: 262144`, `x-omniroute-no-memory: "true"`) |
| 7 | `/Users/androidteam/.hermes/config.yaml` | `0600` | `bbcb86b0a4e50a0f8502f7e3b197d7b29af8ddc1ec9aaf433a790ab13a4923eb` | `f35a2588de96878c2cc0aad6a14fb801dc942bf0f608967cf7b5b440d24b4474` | Surgical `+8/-0` lines: 4 Carbon models + 4 per-tier `agent.reasoning_overrides` |
| 8 | `/Users/androidteam/.config/opencode/opencode.json` | `0600` | `a11e79c624ef46fec2a9ece7a2198625905d53b3bdfa90fff051f4a7c0ee4d90` | `02071e5a7d30b4c427f61b977b327ae9cb2bbd7b8b2698c4adb39289cf47109d` | 4 Carbon models under `omniroute-responses` (`output: 262144`) |
| 9 | `/Users/androidteam/.config/kilo/kilo.jsonc` | `0600` | `f04869eb463273e79efb07b00cd9c0217e8a2b1f25da161577ab4fe3ab14798e` | `a12522632f8d35f67838c843a248a21e2e2a54491129858a72af73cf3202fa74` | 4 Carbon models under `omniroute-responses` (`output: 262144`) |
| 10 | `/Users/androidteam/.codex/cockpit-model-catalog.json` | `0644` | `40d26f5505d5e75d43e42ed6a2a7282880b95fb6c358783893298228066ec82d` | `4ce8295fbee16ddb3769277ba0ec0dc655c3506f1fa34aae21419caaa1b19f63` | Surgical `+424/-0` lines: 4 Carbon entries (`priority: 1021..1024`, tier-matched `default_reasoning_level`, `["low","medium","high"]`) |
| 11 | `/Users/androidteam/.factory/settings.json` | `0600` | `fe4147ea8591b9c44e0e6213f7591c773b3a0d15773da3bafe8e5fe00af9f2ae` | `f8743673a9392014418e65d18144a8640ffea3d44325e25acde98a3c52dbd703` | 4 `custom:OmniRoute-gemini-4-carbon*` entries (`maxOutputTokens: 262144`) |
| 12 | `/Users/androidteam/.claude/profiles/omniroute-pm.json` | `0600` | `656957874edfb71e0394432cdfaf1671228518ea863173d216624c617b65d613` | `72b3137cf5f510e11859c47907fe2c864ea9e9f8b407f4849974e7666ef2418c` | 4 Carbon entries in `availableModels` and `customModels` |
| 13 | `/Users/androidteam/.kimi-code/config.toml` | `0600` | `2fb3fb8ef03afb5c3af40db1219e34e47e9cd310b51ad872c80bff483f0b191c` | `d1d651269f9a9e529c48d36d06f53ccd5f92965d9c740892e37cc47b23bd9b68` | 4 `[models."gemini-4-carbon*"]` tables (`max_output_size = 65536`, `capabilities = ["thinking", "image_in", "tool_use"]`) |
| 14 | `/Users/androidteam/.grok/config.toml` | `0600` | `7faeab3708002f1e0edbbc006dead45ca261413ea6c9af757adebfd4f9ef3265` | `a455a024e0d97bb192ad80cdb7fc3dc3c05ca84264f4a6b7c19b3c3f9d1e6552` | 4 `[models.omniroute-gemini-4-carbon*]` tables |
| 15 | `/Users/androidteam/.config/goose/custom_providers/custom_omniroute.json` | `0600` | `7a76269d07ffe95037784479e2666e7d8606f31ae5a5cc7ddaf92308e4db0f21` | `e991161aee5ab540e1e774c8b30eeccf1edce4b9ef72382a3fb6668d7ac35719` | 4 Carbon entries (`context_limit: 1048576`, `supports_vision: true`, `x-omniroute-no-memory: "true"`) |
| 16 | `/Users/androidteam/.config/muse/settings.json` | `0600` | `427a9791e967b20cb842214ced8e6753a22b79eb9d3fef3028c80dd56ccfe552` | `7607d4533a55e7c4ba28ceccf99ce91866cdadd2eff1039893d34fb3d8a59f5c` | 4 Carbon entries (`display_order: 10..13`, `output_limit: 65536`); `auth.json` `schema_version: 1` (`0600`) |
| 17 | `/Users/androidteam/.qwen/settings.json` | `0600` | `2430f2a2161d67df31e8dcaa7637fa53f09d75af79d537dcccc5c5c8361d715f` | `734495ad1c95d23d3587d428260be07ede29d953bcd24fcc6a8336426e7a7a9f` | 4 Carbon entries (`maxOutputTokens: 65536`) |
| 18 | `/Users/androidteam/.config/zed/settings.json` | `0600` | `c35e270a7988c63c91674dc20cf7f808777994eca44d811052d61481e9d47093` | `1c8553a2846f0e5b1475eed8c7a16616b6bbc100fe411183730d5baf0ac122f1` | 4 Carbon entries (`max_output_tokens: 262144`) |

---

## 5. Live Real CLI Binary Execution Matrix (14/14 Coding Agent CLIs)

| # | Coding Agent CLI | Invocation Command | Exit Code | Output Token |
|---|---|---|---|---|
| 1 | **OMP** (`omp`) | `omp -p --model omniroute/gemini-4-carbon-low --no-tools "Reply with exactly: OMP_CARBON_OK"` | `0` | `OMP_CARBON_OK` |
| 2 | **Pi** (`pi`) | `pi -p --provider omniroute-responses --model gemini-4-carbon-low --no-tools "Reply with exactly: PI_CARBON_OK"` | `0` | `PI_CARBON_OK` |
| 3 | **Prime Agent** (`prime-agent`) | `prime-agent -p --provider omniroute-responses --model gemini-4-carbon-low --no-tools "Reply with exactly: PRIME_CARBON_OK"` | `0` | `PRIME_CARBON_OK` |
| 4 | **Hermes** (`hermes`) | `hermes chat -q "Reply with exactly: HERMES_CARBON_OK" -m gemini-4-carbon-low` | `0` | `HERMES_CARBON_OK` |
| 5 | **OpenCode** (`opencode`) | `opencode run -m omniroute-responses/gemini-4-carbon-low "Reply with exactly: OPENCODE_CARBON_OK"` | `0` | `OPENCODE_CARBON_OK` |
| 6 | **Kilo** (`kilo`) | `kilo run -m omniroute-responses/gemini-4-carbon-low "Reply with exactly: KILO_CARBON_OK"` | `0` | `KILO_CARBON_OK` |
| 7 | **Codex** (`codex`) | `codex exec -c model_provider="omniroute" -m gemini-4-carbon-low --skip-git-repo-check "Reply with exactly: CODEX_CARBON_OK"` | `0` | `CODEX_CARBON_OK` |
| 8 | **Kimi Code** (`kimi`) | `kimi -m gemini-4-carbon-low -p "Reply with exactly: KIMI_CARBON_OK"` | `0` | `• KIMI_CARBON_OK` |
| 9 | **Grok** (`grok`) | `grok --model omniroute-gemini-4-carbon-low -p "Reply with exactly: GROK_CARBON_OK"` | `0` | `GROK_CARBON_OK` |
| 10 | **Goose** (`goose`) | `GOOSE_PROVIDER=custom_omniroute GOOSE_MODEL=gemini-4-carbon-low goose run --no-session -t "Reply with exactly: GOOSE_CARBON_OK"` | `0` | `GOOSE_CARBON_OK` |
| 11 | **Factory Droid** (`droid`) | `droid exec -m custom:OmniRoute-gemini-4-carbon-low "Reply with exactly: DROID_CARBON_OK"` | `0` | `DROID_CARBON_OK` |
| 12 | **Claude Code** (`claude`) | `claude --settings ~/.claude/profiles/omniroute-pm.json -p --model gemini-4-carbon-low "Reply with exactly: CLAUDE_CARBON_OK"` | `0` | `CLAUDE_CARBON_OK` |
| 13 | **Muse Code** (`muse`) | `TBH_CREDENTIAL_BACKEND=file muse exec --model gemini-4-carbon-low --disable-approval --no-session-log "Reply with exactly: MUSE_CARBON_OK"` | `0` | `MUSE_CARBON_OK` |
| 14 | **Qwen Code** (`qwen`) | `qwen --safe-mode -m gemini-4-carbon-low -p "Reply with exactly: QWEN_CARBON_OK"` | `0` | `QWEN_CARBON_OK` |
