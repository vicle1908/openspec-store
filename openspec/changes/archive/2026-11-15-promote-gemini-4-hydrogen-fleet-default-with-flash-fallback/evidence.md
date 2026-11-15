# Evidence

## Execution Summary

- **Change**: `promote-gemini-4-hydrogen-fleet-default-with-flash-fallback`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Timestamp**: `2026-11-15T00:00:00Z`
- **Host**: `iosteam-mac-mini` (`100.70.16.83`, macOS arm64)
- **Apply Status**: `18/18` tracked tasks complete (`validate-archive-readiness.py` `status: "ready"`, `openspec validate --strict` valid).

## Phase 1: Pre-Flight Backups & SQLite Snapshots

- **Backup Directory**: `/Users/androidteam/.omniroute/backups/promote-gemini-4-hydrogen-fleet-default-with-flash-fallback/` (`0700`, `files/` `0700`) containing all 22 pre-change config files (`0600`).
- **OMP `agent.db` Backup**: `/Users/androidteam/.omniroute/backups/promote-gemini-4-hydrogen-fleet-default-with-flash-fallback/agent.db.bak` (`0600`, `14,483,456` bytes, `PRAGMA quick_check = ok`).
- **SHA-256 Ledger**: `sha256-pre.txt` (`0600`) and `sha256-manifest.json` (`0600`, `30` entries).
- **OmniRoute SQLite Snapshot**: `/Users/androidteam/.omniroute/snapshots/pre-hydrogen-default-20261114T094555Z.sqlite` (`0600`, `307,511,296` bytes, SHA-256 `228de9c3c104864ba02dd96886166491fdd9d8be3baacb52e8efb853eed75db7`, `PRAGMA quick_check = ok`, `5` snapshots retained).
- **Combos Backup**: `combos-pre.json` (`0600`, `57,257` bytes, SHA-256 `cc6cd50a57a0505d248a301ad8077d80e4e825bf3ed0961feba57de4db5ac497`).
- **OmniRoute Git Purity**: `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` -> `0` lines.

## Phase 2: OmniRoute Gateway Pruning & `muse-spark-1.3` Cutover

- **Banned Connection Pruning (`38782750-7a60-46d4-ae3f-e8c13cda296b`)**:
  - `gemini-4-hydrogen-{xhigh,high,medium,low}` (`fd5706a2`, `7ca84ebf`, `69251d75`, `a2620b38`): `PUT 200`, banned `38782750` pruned initially (`6` steps), and `62af823b` (`vicgnome19094@gmail.com`) subsequently pruned after Google returned HTTP `403`/`401` during Phase 5 burst probes, leaving `5` active WTU-Pro steps `[9c033d6f, 37f9924d, 573e3f41, 3f3085b1, a94216f4]` with zero Flash steps.
  - `gemini-3.8-flash-high` (`7555d851`), `claude-opus-5.5` (`4b2430da`), `claude-sonnet-5.5` (`9447399c`): `PUT 200`, 10 active non-banned Pro `agy` steps remaining `[9c033d6f, 37f9924d, 573e3f41, 3f3085b1, a94216f4, a7580e21, f511d061, 9ad0a196, 9d66311f, ce95e1cb]`.
- **`muse-spark-1.3` (`453c5dd3-f7f4-4c44-bd4b-6c3c1d0f4e5b`)**: `PUT 200` with `strategy: "priority"`, `context_cache_protection: false`, `nestedComboMode: "execute"`, `targetTimeoutMs: 180000`, `models`: `[combo-ref: gemini-4-hydrogen-high, combo-ref: gemini-3.8-flash-high]`.
- **Cooldown Clear**: `DELETE /api/resilience/model-cooldowns` (`{"all": true}`) -> `HTTP 200`.
- **Catalog & Routing Verification**:
  - `GET /v1/models` (`Accept-Encoding: gzip`): `33,294` bytes (`<= 35,000`), `1,294` models, `max_output_tokens: 262144` on all 5 `gemini-4-hydrogen*` combos.
  - `POST /api/settings/reasoning-routing-rules/simulate`: `low` -> `gemini-4-hydrogen-low`, `medium` -> `gemini-4-hydrogen-medium`, `xhigh` -> `gemini-4-hydrogen-xhigh`, and `high` falls through (`matched: false`) to base combo `combo-ref: gemini-4-hydrogen-high`.

## Phase 3: OMP OAuth Pruning, Isolated Smoke Gate & Promotion

- **OMP `agent.db` Pruning**: Deleted 7 banned `google-antigravity` rows (`id IN (5, 8, 9, 12, 13, 16, 19)`) inside `PRAGMA busy_timeout=5000; BEGIN IMMEDIATE;`; `6` active rows remain (`id IN (2, 3, 6, 10, 14, 15)`). `~/.omp/agent/models.yml` untouched (SHA-256 `b93bbe0cf13733cdb23efb024aa8d67612ba2ffaa64b3b2969980145cb315e37`).
- **Isolated Smoke Gate (`--profile hydrogen-default-smoke`, empty `fallbackChains`, `advisor.enabled: false`, `memory.backend: off`)**:
  - `omniroute/gemini-4-hydrogen:high` -> exit `0`, `pong`, `masquerade=0`
  - `omniroute/gemini-4-hydrogen:low` -> exit `0`, `pong`, `masquerade=0`
  - `omniroute/gemini-4-hydrogen-low:low` -> exit `0`, `pong`, `masquerade=0`
  - `google-antigravity/gemini-3.8-flash:high` -> exit `0`, `pong`, `masquerade=0`
  - `NO_RCS` (`zsh -fc` with stripped env keys) -> exit `0`, `pong` via `.env`
- **Live Promotion & Cleanup**: Atomically promoted `~/.omp/agent/config.yml` (`0600`), removed scratch profile directory, and verified live `omp --config <overlay> --mode json --no-session --no-tools --model smol -p "reply only: pong"` served by `gemini-4-hydrogen`.

## Phase 4: Fleet Cutover (`15` Companion Clients/IDEs + State + `~/.shb/.env`)

- **Claude Code**: `~/.claude/profiles/omniroute-pm.json` (`0600`, `ANTHROPIC_BASE_URL: http://127.0.0.1:20129`, `model: gemini-4-hydrogen`, `CLAUDE_CODE_EFFORT_LEVEL: high`, haiku/subagent `gemini-4-hydrogen-low`, `gemini-3.8-flash-high` retained) + `~/.zshrc` (`0600`, `:20129` + `"gemini-4-hydrogen"`).
- **Codex CLI**: `~/.codex/{config.toml,omniroute.config.toml}` (`0600`, `model = "gemini-4-hydrogen"`, `model_reasoning_effort = "high"`) + `cockpit-model-catalog.json` (`0644`, object-array `supported_reasoning_levels` clamped per tier).
- **Hermes**: `~/.hermes/config.yaml` (`0600`, `providers.omniroute.model: gemini-4-hydrogen`, `moa.presets.{default,deep}` & root `moa.{reference_models,aggregator}` updated, `fallback_providers: [{provider: omniroute, model: gemini-3.8-flash-high}]`).
- **Pi & Prime Agent**: `~/.pi/agent/settings.json` (`0600`, `defaultModel: gemini-4-hydrogen`, `defaultThinkingLevel: high`, `modelThinkingLevels`, `subagents.agentOverrides` with `reviewer -> gemini-4-hydrogen-xhigh`, `models.json` untouched) + `~/.prime/agent/settings.json` (`0600`, `defaultModel: gemini-4-hydrogen`, `recentModels[0]: omniroute-responses/gemini-4-hydrogen`). Zero `.bak*` files.
- **OpenCode & Kilo Code**: `~/.config/opencode/opencode.json` (`0600`), `~/.local/state/opencode/model.json` (`0600`), `~/.config/kilo/kilo.jsonc` (`0600`), `~/.local/state/kilo/model.json` (`0600`, `model.code.modelID: gemini-4-hydrogen` only).
- **Kimi Code, Grok, Goose, Factory Droid, Qwen Code, Muse Code**: All verified (`0600`); Factory Droid updated both `sessionDefaultSettings.model` and `missionModelSettings.workerModel` to `custom:OmniRoute-gemini-4-hydrogen`.
- **Zed, Cline, Continue, `~/.shb/.env`**: All updated (`0600`), including Continue `tabAutocompleteModel` (`gemini-4-hydrogen-low`, `completionOptions: {"reasoning": false}`) and `~/.shb/.env` (`SHB_DEFAULT_MODEL=gemini-4-hydrogen`, `SHB_FALLBACK_MODEL=gemini-3.8-flash-high`).

## Phase 5: End-to-End Verification, Permissions, Docs/Notion/Mesh Sync

- **Installed CLI Headless `"pong"` Probes (`12/13` passed, `1` pre-existing Codex v0.169.0 stream timeout)**:
  - `claude`: exit `0`, `pong` (`17.22s`)
  - `hermes`: exit `0`, `pong` (`34.18s`)
  - `pi` (`env -u PI_CODING_AGENT_DIR`): exit `0`, `pong` (`13.701s`; note OMP parent process sets `PI_CODING_AGENT_DIR=~/.omp/agent`)
  - `prime-agent`: exit `0`, `pong` (`~6s`, after stopping stale Nov 01 daemon PID `7922` bound to deleted Node `26.13.0_2`)
  - `opencode`: exit `0`, `pong` (`23.75s`)
  - `kilo`: exit `0`, `pong` (`26.76s`)
  - `kimi -p "reply only: pong"`: exit `0`, `pong` (`6.717s`)
  - `grok`: exit `0`, `pong` (`11.678s`)
  - `goose`: exit `0`, `pong` (`11.600s`)
  - `droid exec -m "custom:OmniRoute-gemini-4-hydrogen"`: exit `0`, `pong` (`8.958s`) + JSON read-back verified
  - `muse`: exit `0`, `pong` (`12.263s`)
  - `qwen`: exit `0`, `pong` (`9.645s`)
  - `codex exec`: timed out (`exit 124`, `Reconnecting... 1/5`–`2/5`); baseline control `codex exec -c model="gemini-3.8-flash-high"` also timed out (`exit 124`, `35.8s`), confirming a pre-existing Codex v0.169.0 `/v1/responses` behavior while direct `/v1/responses` (`gemini-4-hydrogen`, `effort: "high"`, `summary: "detailed"`) returned `HTTP 200` + `response.completed` + `pong` (`6.83s`).
- **IDE Protocol & Fallback Probes**:
  - Cline `/v1/chat/completions`: `HTTP 200`, `5.577s`, `gemini-4-hydrogen-high` `'pong'`.
  - Continue `/v1/chat/completions`: chat `HTTP 200` (`3.981s`, `'pong'`), autocomplete `HTTP 200` (`4.060s`, `'pong'`).
  - `muse-spark-1.3` fallback probe: `HTTP 200`, `3.543s`, `call_logs` confirmed `gemini-4-hydrogen-high` execution (`status: 200`, `2840–3255ms`).
- **Permissions, Secrets & Bootstrap Parity**:
  - `/usr/bin/stat -L -f '%Mp%Lp %N'` verified `0600` across all 22 credential/config files (including re-enforced `0600` on `~/.factory/settings.json` after `droid exec`) and `0644` on `~/.codex/cockpit-model-catalog.json`.
  - Zero secret leaks across non-secret files.
  - `setup-macbook-omniroute-client.sh` SHA-256 identical (`14efa442ee2537bcf435a817b5925199eaabef9f108a4f09b09c1ef5d8b1b2a5`); added Tailnet `ServerAliveInterval 15` block to `~/.ssh/config` (`0600`) and verified `setup-macbook-omniroute-client.sh --check` exits `0` (`[omniroute-client] SUCCESS (check)`) across Tailscale Serve, all 19 `/v1/models` combos, `:20129`, `:20132`, and all 18 host client config URLs (`HOST_CLIENT_CONFIG_URL_CHECK_PASSED=18`).
- **Docs, Notion & AgentMemory Sync**:
  - Updated `wiki/entities/{pi,omniroute,goose}.md` and `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md`.
  - `sync-notion-knowledge.sh --section entities` updated Notion pages `3efc4b21-deb4-81ae-800f-dceee31b04fe` (`OmniRoute`), `3efc4b21-deb4-8129-b9c3-d7c22a453212` (`Pi`), and `3fcc4b21-deb4-813c-b022-dfd12a6e7603` (`Goose CLI`).
  - AgentMemory mesh sync (`127.0.0.1:3111` & `100.106.143.78:3111`) -> `success: true`, `errors: []`.
  - Compat patch: `docker exec omniroute sh /app/container-entrypoint-compat.sh --patch-only` -> verified clean.
