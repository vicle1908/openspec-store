# Tasks: omp-three-provider-verification

## 1. Provider registration (completed by previous change)

- [x] 1.1 shopapikey/fable-5 registered in `models.yml` with `api: anthropic-messages`
- [x] 1.2 giaoduc/Advance registered in `models.yml` with `api: anthropic-messages`
- [x] 1.3 cockpit/gpt-5.6-luna registered in `models.yml` with `api: openai-responses`, `baseUrl: http://localhost:51006/v1`
- [x] 1.4 All `apiKey` values reference `HERMES_CUSTOM_*` env vars

## 2. Role assignment (completed by previous change)

- [x] 2.1 `default: cockpit/gpt-5.6-luna:high`
- [x] 2.2 `smol: shopapikey/fable-5`
- [x] 2.3 `slow: cockpit/gpt-5.6-luna:max`
- [x] 2.4 `plan: cockpit/gpt-5.6-luna:max`
- [x] 2.5 `commit: shopapikey/fable-5`
- [x] 2.6 `task: giaoduc/Advance`
- [x] 2.7 No role references OmniRoute

## 3. Fresh-shell CLI verification

- [x] 3.1 Fresh shell resolves `omp` to `~/.bun/bin/omp` v17.2.15
- [x] 3.2 All three credential env vars SET in fresh shell
- [x] 3.3 No `PI_*_MODEL` overrides set in fresh shell
- [x] 3.4 `cockpit/gpt-5.6-luna:high` → pong, exit 0
- [x] 3.5 `cockpit/gpt-5.6-luna:max` → pong, exit 0
- [x] 3.6 `shopapikey/fable-5` → pong, exit 0
- [x] 3.7 `giaoduc/Advance` → pong, exit 0
- [x] 3.8 Live default (no `--model`) → pong, exit 0

## 4. Structural invariants

- [x] 4.1 `models.yml` contains exactly 4 providers: cockpit, giaoduc, omniroute, shopapikey
- [x] 4.2 `modelRoles` exists in `config.yml` but NOT in `models.yml`
- [x] 4.3 OmniRoute block and `equivalence` preserved (semantic comparison)
- [x] 4.4 No provider `baseUrl` references adapter ports (8787, 8788)
- [x] 4.5 All 11 programmatic invariant checks PASS

## 5. Default-role drift investigation

- [x] 5.1 Observed drift: `default` was `giaoduc/Advance` (expected `cockpit/gpt-5.6-luna:high`)
- [x] 5.2 Disposable-profile persistence test: `--model` does NOT persist into `config.yml`
- [x] 5.3 Cause of earlier drift: **unknown** — not reproducible, not caused by `--model` flag
- [x] 5.4 Default role restored to `cockpit/gpt-5.6-luna:high`

## 6. Permissions

- [x] 6.1 `config.yml` restored to mode 644 (was 600 during direct rewrite)
- [x] 6.2 `models.yml` remains mode 644

## 7. Cleanup

- [x] 7.1 All disposable profiles removed (persistence-test, verify-cockpit, verify-shopapikey, verify-giaoduc)
- [x] 7.2 Stale `config.yml.fix-backup` removed
- [x] 7.3 Stale `/tmp/external_hashes.json` removed

## Evidence

**Live file hashes (final):**
- `models.yml`: `e223d68e0598fdef178db9be02cc23f0` (mode 644)
- `config.yml`: `238154c5ec2c29deffb95ef3f725db25` (mode 644)

**Backup file:** `~/.omp/agent/models.yml.pre-native-cockpit-20260812_150334` (mode 600)

**Fresh-shell test results:**
- All 4 unique selectors: pong, exit 0
- Live default resolution: pong, exit 0
- 11/11 programmatic invariant checks: PASS

**Observations (not root-caused):**
- Default-role drift occurred during verification session; cause unknown
- Two omp installations coexist (Bun + Homebrew, both v17.2.15); fresh shell picks Bun
