# Verification Evidence: `register-gemini-4-argon-across-coding-agents`

- **Change**: `register-gemini-4-argon-across-coding-agents`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Timestamp (UTC)**: `2026-10-20T03:15:00Z`
- **External Backup & Ledger Root**: `/Users/androidteam/.omniroute/backups/register-gemini-4-argon-across-coding-agents/` (`mode: 0700`)

---

## 1. External Execution Packet & Governance Gates

1. **External Root Authorization**:
   - Authorized by user invocation of `/opsx:apply` on `register-gemini-4-argon-across-coding-agents` (`2026-10-20`).
   - Scope: 14 external `$HOME` configuration files under `/Users/androidteam/` plus relocation of 4 stale `.bak*` files and `backups/` directory out of `/Users/androidteam/.prime/agent/` into `/Users/androidteam/.omniroute/backups/register-gemini-4-argon-across-coding-agents/prime-stale-backups/`.
2. **Owner Mode-Tightening Ratification (`0644 -> 0600`)**:
   - `/Users/androidteam/.factory/settings.json`: `0644 -> 0600` (`stat -L -f '%04Lp'`)
   - `/Users/androidteam/.config/muse/settings.json`: `0644 -> 0600` (`stat -L -f '%04Lp'`)
   - `/Users/androidteam/.qwen/settings.json`: `0644 -> 0600` (`stat -L -f '%04Lp'`)
   - Public metadata catalog `/Users/androidteam/.codex/cockpit-model-catalog.json` preserved at mode `0644` (zero credentials or provider URLs), with its backup in `~/.omniroute/backups/...` at mode `0600`.
3. **Kimi Code Rotation-Gate Waiver Reference**:
   - `/Users/androidteam/.kimi-code/config.toml` updated value-blind in memory (`providers` table byte-identical before and after mutation) under the owner's accepted-risk rotation release recorded in `2026-09-02-invalidate-archive-gaps-closure-fabrications/evidence/rotation-gate-release.json` (`decision: "authorized_without_rotation"`).

---

## 2. Preflight Gateway & OMP Read-Only Baseline (Task 1.1)

- **OmniRoute `/v1/models` Check (`GET http://127.0.0.1:20128/v1/models`)**:
  - `gemini-4-argon`: `owned_by: "combo"`
  - `gemini-4-argon-high`: `owned_by: "combo"`
  - `gemini-4-argon-medium`: `owned_by: "combo"`
  - `gemini-4-argon-low`: `owned_by: "combo"`
- **OMP (`omp models --json` & `~/.omp/agent/config.yml`)**:
  - Verified `providers.omniroute` exposes `["gemini-4-argon", "gemini-4-argon-high", "gemini-4-argon-low", "gemini-4-argon-medium"]` with intact `retry.fallbackChains` and `modelRoles` (`default` resolving to `cockpit/gpt-6.1-sol:high`, `advisor: cockpit/gpt-6.1-sol:xhigh`, `plan`/`task: google-antigravity/gemini-4-argon:high`, `smol: google-antigravity/gemini-4-argon`, `tiny`/`vision`/`slow`/`commit: omniroute/gemini-3.8-flash-high`).

---

## 3. Applied-Surface Register (Pre/Post SHA-256 & Mode Ledger)

| Task | Surface | Target Path | Pre Mode → Post Mode (`stat -L`) | Pre-Mutation SHA-256 | Post-Mutation SHA-256 | Backup Path (`mode: 0600`) | Preserved Startup Default |
|---|---|---|---|---|---|---|---|
| **2.1** | `pi` | `/Users/androidteam/.pi/agent/models.json` | `0600 -> 0600` | `f7104795640b2c3f9e3f4a40ef0ddb05dee1f1798546e833a31c24db9c940594` | `eed1fa2b64c241d7bdd0df1af9be8d2c0caaca7f900ba9c0f82dc43cb873c1b6` | `.../pi__models.json.bak` | `omniroute-responses/gemini-3.8-flash-high` |
| **2.2** | `prime-agent` | `/Users/androidteam/.prime/agent/models.json` | `0600 -> 0600` | `6cad8c7dfcc9706838d881da63ddcba680389a408f4d4b7d1f1cea953bebfd7d` | `bf81667159ebf05bfbe24ad295762276ed64d701dd9d58725a97775026f87e84` | `.../prime-agent__models.json.bak` | `omniroute-responses/gemini-3.8-flash-high` |
| **2.3** | `hermes` | `/Users/androidteam/.hermes/config.yaml` | `0600 -> 0600` | `934cd33ee5dab1ed7c09f06448b7727bac2e3e53fd88d9423c35c52f8bd34eec` | `d39b1696ce23ffc2fa2c2d1992a775109117d40be7381fac98fb3c04f051a64b` | `.../hermes__config.yaml.bak` | `model.provider: moa`, `model.default: default` |
| **2.4** | `opencode` | `/Users/androidteam/.config/opencode/opencode.json` | `0600 -> 0600` | `4afed5c937ceaa0b44bed10770a0357f5df8c9e1bb0efa1e0c61f0d0913ed0c1` | `fb6ecd95d655fca536bfe0429afdd039670eb2c936d8c5d5ebce36362ab38fe5` | `.../opencode__opencode.json.bak` | `omniroute-responses/gemini-3.8-flash-high` |
| **2.5** | `kilo` | `/Users/androidteam/.config/kilo/kilo.jsonc` | `0600 -> 0600` | `cd6f8596fb76bd306993a770fcec98543d3514649b567ab7e92ffa8b993c1165` | `ddb591a8d17fe8a7583ede280e932c36b9942d9495aea554f8417456681b05e5` | `.../kilo__kilo.jsonc.bak` | `omniroute/sh/codex` |
| **3.1** | `codex` | `/Users/androidteam/.codex/cockpit-model-catalog.json` | `0644 -> 0644` | `0aa0b804cf8869f8854c9041467b6dd46b2b6b101aaa22878a51ce3b94c2a2b3` | `3260f2fde1e78ce21ef43b2c3edec6e055afa21c58dd6558023171578a20dcb9` | `.../codex__cockpit-model-catalog.json.bak` | `gemini-3.8-flash-high` (`model_provider = "omniroute"`) |
| **3.2** | `kimi` | `/Users/androidteam/.kimi-code/config.toml` | `0600 -> 0600` | `0b85994a5e151a40cc774818f44ae1629f099a35a89cb1511530612d7e7d6580` | `863f532fad669eebbb7329371ca440f0b0fb9a4ac52f9e20784203ae2f3361d0` | `.../kimi__config.toml.bak` | `gemini-3.8-flash-high` |
| **3.3** | `grok` | `/Users/androidteam/.grok/config.toml` | `0600 -> 0600` | `408052c84e950d60704688612e76d6c85d7f96dc9678aebba48541939b05800f` | `81c4f47f5059ea5f39c79ca46ba36ad2b996ed921a2b29eafcc58bec4bb6c024` | `.../grok__config.toml.bak` | `omniroute-gemini-flash` (`chat_completions`) |
| **3.4** | `goose` | `/Users/androidteam/.config/goose/custom_providers/custom_omniroute.json` | `0600 -> 0600` | `b0d16a0e042d4e3836eb93ea626acff5caa828f0ff43d15097e106c33cc5cd2e` | `8a66b462cd9f5474075af22ea059cfb0a0e9f16e39ec05ada40b10895a68a3c6` | `.../goose__custom_omniroute.json.bak` | `gemini-3.8-flash-high` (`chat/completions`) |
| **3.5** | `droid` | `/Users/androidteam/.factory/settings.json` | `0644 -> 0600` | `6fc391383fa23d880c5c3d0f0aff5047773ec4399c670fe3b678eef8c3f5ed0f` | `21b00ce531b5b42f64d91dd99116a6b90afe3c8108f3c63fa4a32c220a888586` | `.../droid__settings.json.bak` | `custom:OmniRoute-gemini-3-8-flash-high` |
| **4.1** | `claude` | `/Users/androidteam/.claude/profiles/omniroute-pm.json` | `0600 -> 0600` | `a3dda02134bd6fb5b1a2578cedc3bbcffede49eee6fc86214c378bbc4ef99800` | `0dc93512b5fdac77ffcc589a16a800fc3dbb206d08c3840d4b50f0ec7bbcd82a` | `.../claude__omniroute-pm.json.bak` | `gemini-3.8-flash-high` |
| **4.2** | `muse` | `/Users/androidteam/.config/muse/settings.json` | `0644 -> 0600` | `fc06c0ba5d382530aaa91bf65cb63c164164db7ade3c72e3f46ac0f6c6c23419` | `a2a0340734a91784bc4275078484e8039e4277d424416565e2007885d76ddef9` | `.../muse__settings.json.bak` | `muse-spark-1.3` (`is_default: true`) |
| **4.3** | `qwen` | `/Users/androidteam/.qwen/settings.json` | `0644 -> 0600` | `b88a799732bccba7de30ce222b3c112db450d92718eb4d239a2a357b3d9c65af` | `d6c18a0a54be4dd0147e60873a25ca0cde7235b9841bda2608dc2f5ee881e7e1` | `.../qwen__settings.json.bak` | `gemini-3.8-flash-high` |
| **4.4** | `zed` | `/Users/androidteam/.config/zed/settings.json` | `0600 -> 0600` | `2889b0ad7acd22c7859727f7778778e3168f409d36bff2fb85f5d4c83037fc9f` | `2886732169a219aec6f08bb12b89504dd5680a5915b72b8fbaee097a6b79f6d2` | `.../zed__settings.json.bak` | `mc/muse-spark-1.3` (`omniroute`) |

### Untouched Read-Only & Unconfigured Files (`pre_sha256 == post_sha256`)

- `/Users/androidteam/.omp/agent/models.yml`: mode `0600`, SHA-256 `2dd10d1fe5bfbdd8f6578cee5133ead526536643179196d69268147ebe86e933` (`unchanged: true`)
- `/Users/androidteam/.omp/agent/config.yml`: mode `0600`, SHA-256 `d887ff4f5de3f588c4bc4bdc94361d4f25bbcaa7eea434d261056e2af6408b7b` (`unchanged: true`)
- `/Users/androidteam/.pi/agent/settings.json`: mode `0600`, SHA-256 `3f72d47355c6beae8a4ded3d73368de0e5b57e8a8e0d898f448ca81ce1019b1e` (`unchanged: true`)
- `/Users/androidteam/.prime/agent/settings.json`: mode `0600`, SHA-256 `256b2f6c0a766d9a3c61b94c5e530faab1baaad9d52000a72a5c0afc8fb51ba0` (`unchanged: true`, `0` `.bak*` files in `~/.prime/agent/`)
- `/Users/androidteam/.codex/config.toml`: mode `0600`, SHA-256 `1d746f5d2642d1d1b176ebbe1f0e9a721924468531ee62df9e696bc9576cc027` (`unchanged: true`)
- `/Users/androidteam/.kimi/config.toml`: mode `0600`, SHA-256 `c1194a6f0b584f8ba8a37b83991928eb8032b8d4b86bbd68d254ad043dffd482` (`unchanged: true`)
- `/Users/androidteam/.config/goose/config.yaml`: mode `0600`, SHA-256 `ad160958a813c6b302444c072ea2dfdcd2c91945ce844c286e4754ee35b281a8` (`unchanged: true`)
- `/Users/androidteam/.qoder/settings.json`: mode `0644`, SHA-256 `b8593d6ed2658edd536b63494aa6e9b6e7a4cc6614f8e1a72c7852cd03112754` (`unchanged: true`)
- `/Users/androidteam/.cursor/cli-config.json`: mode `0644`, SHA-256 `ec209e0e873014c6f83abdf4598463631406b4e0ed8c0e82ee860718aa479aa6` (`unchanged: true`)
- `/Users/androidteam/.augment/.auggie.json`: mode `0644`, SHA-256 `ebb75494e8a1a17f82a0653cd1fc58c81b9360683d1ce51e2607426a5a1a8d7c` (`unchanged: true`)
- `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no`: `0` lines (clean).

---

## 4. Catalog & Attributed 1-Turn Sentinel Probe Results

| Task | Tool | 4-Model Catalog Check | 1-Turn `gemini-4-argon-low` Sentinel Command & Output | OmniRoute Gateway Attribution |
|---|---|---|---|---|
| **2.1** | `pi` | `pi --list-models gemini-4-argon` → `omniroute-responses` lists `gemini-4-argon{,-high,-low,-medium}` (`1M`, `65.5K`, `thinking=yes`, `images=yes`) | `pi -p --no-session --no-mcp --no-extensions --no-skills --model omniroute-responses/gemini-4-argon-low "Reply with exactly: ARGON_PI_OK"` → `ARGON_PI_OK` (`rc=0`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **2.2** | `prime-agent` | `prime-agent model list gemini-4-argon` → `omniroute-responses` lists `gemini-4-argon{,-high,-low,-medium}` (`1M`, `65.5K`, `thinking=yes`, `images=yes`) | `prime-agent -p --no-session --no-tools --no-extensions --no-skills --provider omniroute-responses --model gemini-4-argon-low "Reply with exactly: ARGON_PRIME_OK"` → `ARGON_PRIME_OK` (`rc=0`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **2.3** | `hermes` | `uv run --with pyyaml` verified `["gemini-4-argon", "gemini-4-argon-high", "gemini-4-argon-medium", "gemini-4-argon-low"]` in `providers.omniroute.models` | `hermes chat --oneshot -Q --provider omniroute -m gemini-4-argon-low --reasoning low -q "Reply with exactly: ARGON_HERMES_OK"` → `ARGON_HERMES_OK` (`rc=0`, `session_id: 20261020_100443_889223`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **2.4** | `opencode` | `opencode models omniroute-responses` → lists `omniroute-responses/gemini-4-argon{,-high,-low,-medium}` | `opencode run --pure -m omniroute-responses/gemini-4-argon-low "Reply with exactly: ARGON_OPENCODE_OK"` → `ARGON_OPENCODE_OK` (`rc=0`, `> build · gemini-4-argon-low`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **2.5** | `kilo` | `kilo models omniroute-responses` → lists `omniroute-responses/gemini-4-argon{,-high,-low,-medium}` | `kilo run --pure -m omniroute-responses/gemini-4-argon-low "Reply with exactly: ARGON_KILO_OK"` → `ARGON_KILO_OK` (`rc=0`, `> code · gemini-4-argon-low`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **3.1** | `codex` | `jq` verified `gemini-4-argon{,-high,-medium,-low}` (`visibility: "list"`, `prefer_websockets: false`, `use_responses_lite: false`, `tool_mode: null`, `apply_patch_tool_type: "freeform"`, `context_window: 1000000`) | `codex exec --ephemeral --skip-git-repo-check -c model_provider="omniroute" -m gemini-4-argon-low -c model_reasoning_effort="low" "Reply with exactly: ARGON_CODEX_OK" </dev/null` → `ARGON_CODEX_OK` (`rc=0`, session `01a15747-5156-7592-8bf0-6fa222917aa0`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **3.2** | `kimi` | `kimi doctor` (`OK config.toml`, `OK tui.toml`) + `tomllib` verified all 4 `[models."gemini-4-argon*"]` tables | `kimi -m gemini-4-argon-low -p "Reply with exactly: ARGON_KIMI_OK" </dev/null` → `• ARGON_KIMI_OK` (`rc=0`, `session_9cea7ee5-4c3d-47ec-909f-5238da9de6ea`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **3.3** | `grok` | `grok models` → lists `omniroute-gemini-4-argon{,-high,-medium,-low}` with `* omniroute-gemini-flash (default)` | `grok -p "Reply with exactly: ARGON_GROK_OK" -m omniroute-gemini-4-argon-low --max-turns 1 </dev/null` → `ARGON_GROK_OK` (`rc=0`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **3.4** | `goose` | `jq` verified `gemini-4-argon{,-high,-medium,-low}` (`context_limit: 1048576`, `supports_vision: true`) in `custom_omniroute.json` | `goose run --no-session --no-profile -q --max-turns 1 --provider custom_omniroute --model gemini-4-argon-low -t "Reply with exactly: ARGON_GOOSE_OK" </dev/null` → `ARGON_GOOSE_OK` (`rc=0`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **3.5** | `droid` | `jq` verified `custom:OmniRoute-gemini-4-argon{,-high,-medium,-low}` (`maxOutputTokens: 65536`) in `customModels[]` | `droid exec --disable-builtin-skills -m custom:OmniRoute-gemini-4-argon-low -r low "Reply with exactly: ARGON_DROID_OK" </dev/null` → `ARGON_DROID_OK` (`rc=0`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **4.1** | `claude` | `jq` verified all 5 `modelPicker.options` rows (`gemini-3.8-flash-high` + 4 `gemini-4-argon*` rows, `behavesAs: "claude-fable-5-1"`) | `claude -p --bare --no-session-persistence --settings ~/.claude/profiles/omniroute-pm.json --model gemini-4-argon-low --effort low "Reply with exactly: ARGON_CLAUDE_OK"` → `ARGON_CLAUDE_OK` (`rc=0`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **4.2** | `muse` | `muse model-profile show gemini-4-argon` (`rc=0`) + `jq` verified 5 visible `model_catalog` rows (`muse-spark-1.3` default + 4 `gemini-4-argon*` rows) | `/opt/homebrew/bin/muse exec --disable-approval --disable-reminders --no-session-log --reasoning-effort low --model gemini-4-argon-low "Reply with exactly: ARGON_MUSE_OK"` → `ARGON_MUSE_OK` (`rc=0`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **4.3** | `qwen` | `jq` verified 5 `modelProviders.openai[]` entries (`$version: 4` nested `capabilities` & `generationConfig`) | `qwen --safe-mode --chat-recording=false --max-session-turns 1 -m gemini-4-argon-low "Reply with exactly: ARGON_QWEN_OK" </dev/null` → `ARGON_QWEN_OK` (`rc=0`) | `comboName=gemini-4-argon-low` → `agy/gemini-4-argon-low` (`0 fallbacks`, `status: 200`) |
| **4.4** | `zed` | `jq` verified `53` `available_models[]` entries (`gemini-4-argon{,-high,-medium,-low}` with `1000000` context, `65536` output, full `capabilities`) and preserved `mc/muse-spark-1.3` default | GUI editor surface (programmatic JSON/schema check passed; interactive Agent panel dropdown is a GUI verification surface) | N/A (GUI surface) |
