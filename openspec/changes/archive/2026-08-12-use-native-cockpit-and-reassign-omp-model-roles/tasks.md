# Tasks: use-native-cockpit-and-reassign-omp-model-roles

## 1. Preflight

- [x] 1.1 Confirm live `models.yml` hash is `d1317008703e224db1455621571d51f9`
- [x] 1.2 Confirm live `config.yml` hash is `31b76c4454fc06945fabf0ddbabbd468`
- [x] 1.3 Confirm port 51006 is listening and cockpit-cliproxy owns it
- [x] 1.4 Confirm native `/v1/responses` succeeds with `model: gpt-5.6-luna`
- [x] 1.5 Confirm current cockpit is `http://localhost:8788` / `anthropic-messages`
- [x] 1.6 Confirm all three credential env vars are SET (no values printed)
- [x] 1.7 Confirm adapter host port 8788 maps to container 8787 (Docker Compose)
- [x] 1.8 Confirm port 8787 is occupied by Hermes WebUI (not the adapter)

## 2. Backups

- [x] 2.1 Timestamped backup of `models.yml` created
- [x] 2.2 Timestamped backup of `config.yml` created
- [x] 2.3 Both backups set to mode 600

## 3. Isolated profile

- [x] 3.1 Stale profile removed
- [x] 3.2 Profile directory created
- [x] 3.3 Current live `models.yml` parsed, cockpit block replaced
- [x] 3.4 Assert cockpit: `baseUrl=http://localhost:51006/v1`, `api=openai-responses`
- [x] 3.5 Assert no provider references `8787` or `8788`
- [x] 3.6 Current live `config.yml` parsed, `modelRoles` replaced
- [x] 3.7 Assert `modelRoles` exists in `config.yml` but NOT in `models.yml`
- [x] 3.8 Assert OmniRoute block and `equivalence` unchanged
- [x] 3.9 Both files written and re-parsed to verify

## 4. Isolated verification

- [x] 4.1 `omp --profile omp-native-cockpit-test models` — all providers listed
- [x] 4.2 `--model cockpit/gpt-5.6-luna:high` — pong, exit 0
- [x] 4.3 `--model cockpit/gpt-5.6-luna:max` — pong, exit 0
- [x] 4.4 `--model shopapikey/fable-5` — pong, exit 0
- [x] 4.5 `--model giaoduc/Advance` — pong, exit 0
- [x] 4.6 Default-role resolution — pong, exit 0
- [x] 4.7 Programmatic: no role value references `omniroute`
- [x] 4.8 Programmatic: no provider `baseUrl` references `8787` or `8788`
- [x] 4.9 Programmatic: OmniRoute + equivalence semantically identical to live baseline

## 5. Live application

- [x] 5.1 Temp `models.yml` prepared: parse live, replace cockpit block, write, re-parse
- [x] 5.2 Atomic rename temp → live `models.yml`
- [x] 5.3 Verify: `md5 -q models.yml` = `e223d68e0598fdef178db9be02cc23f0`
- [x] 5.4 Temp `config.yml` prepared: parse live, replace `modelRoles`, write, re-parse
- [x] 5.5 Verify temp `config.yml` parses correctly
- [x] 5.6 Atomic rename temp → live `config.yml`

## 6. Live verification

- [x] 6.1 `omp models` — all providers, OmniRoute present
- [x] 6.2 `omp -p "reply only: pong"` — default role resolves, pong, exit 0
- [x] 6.3 `--model cockpit/gpt-5.6-luna:high` — pong, exit 0
- [x] 6.4 `--model cockpit/gpt-5.6-luna:max` — pong, exit 0
- [x] 6.5 `--model shopapikey/fable-5` — pong, exit 0
- [x] 6.6 `--model giaoduc/Advance` — pong, exit 0
- [x] 6.7 Programmatic: exact role map matches proposal (6 roles, 4 unique selectors)
- [x] 6.8 Programmatic: cockpit block = `http://localhost:51006/v1` / `openai-responses`
- [x] 6.9 Programmatic: no `baseUrl` references `8787` or `8788`
- [x] 6.10 Programmatic: OmniRoute block + equivalence unchanged (semantic compare)
- [x] 6.11 Programmatic: no plaintext secrets (env-var references only)
- [x] 6.12 Programmatic: 18/18 semantic invariant checks PASSED

## 7. Rollback

- Rollback NOT required (all gates passed)

## 8. Cleanup

- [x] 8.1 Isolated profile removed

## Execution Evidence

**Pre-change baselines:**
- `models.yml`: `d1317008703e224db1455621571d51f9`
- `config.yml`: `31b76c4454fc06945fabf0ddbabbd468`

**Post-change hashes:**
- `models.yml`: `e223d68e0598fdef178db9be02cc23f0`
- `config.yml`: `d82e130d2fdd1d117b506189e5895db3`

**Backup paths:**
- `~/.omp/agent/models.yml.pre-native-cockpit-20260812_150334` (perms 600)
- `~/.omp/agent/config.yml.pre-native-cockpit-20260812_150334` (perms 600)

**Live file permissions:** both 644

**Smoke test results:**
- `cockpit/gpt-5.6-luna:high` → pong, exit 0
- `cockpit/gpt-5.6-luna:max` → pong, exit 0
- `shopapikey/fable-5` → pong, exit 0
- `giaoduc/Advance` → pong, exit 0
- Default role (no `--model`) → pong, exit 0

**Semantic invariant results (18/18 PASS):**
- 4 providers present
- cockpit.baseUrl = http://localhost:51006/v1
- cockpit.api = openai-responses
- cockpit.apiKey = HERMES_CUSTOM_COCKPIT_API_KEY
- No adapter ports (8787, 8788)
- modelRoles absent from models.yml
- Exact role map matches proposal
- No omniroute in any role
- OmniRoute block identical to pre-change
- Equivalence section identical to pre-change
- All 3 custom apiKey values are env-var references
- No pmv_, agt_, sk-ant- in models.yml
- 4 unique selectors

**Isolated profile:** removed

**Status:** READY TO ARCHIVE
