# Tasks: Replace giaoduc with phanmemvip (Codex Responses API)

## 1. Preflight & Backup

- [x] 1.1 Confirm `HERMES_CUSTOM_PHANMEMVIP_API_KEY` resolves in a fresh login shell (`zsh -lc 'echo -n ${HERMES_CUSTOM_PHANMEMVIP_API_KEY:+set}'` prints `set`). Verify: output is `set`.
- [x] 1.2 Re-verify phanmemvip Responses endpoint: `curl -s https://api.phanmemvip.shop/v1/responses -H "Authorization: Bearer $HERMES_CUSTOM_PHANMEMVIP_API_KEY" -H "Content-Type: application/json" -d '{"model":"gpt-5.6-sol","input":"reply only: pong","max_output_tokens":50}'` returns `"status":"completed"` with text `pong`. Verify: response contains `pong`.
- [x] 1.3 Create timestamped backups of every target file and record md5 baselines:
   ```bash
   TS=$(date +%Y%m%dT%H%M%S)
   for f in ~/.hermes/config.yaml ~/.omp/agent/config.yml ~/.omp/agent/models.yml \
            ~/.pi/agent/settings.json ~/.pi/agent/models.json ~/.prime/agent/models.json \
            ~/.grok/config.toml ~/.config/goose/config.yaml ~/.zshrc ~/.hermes/.env; do
     cp "$f" "$f.bak-pre-phanmemvip.$TS"
   done
   cp ~/.config/goose/custom_providers/custom_giaoduc.json ~/.config/goose/custom_providers/custom_giaoduc.json.bak-pre-phanmemvip.$TS
   ```
   Verify: every `.bak-pre-phanmemvip.$TS` file exists; record `TS` and each baseline `md5 -q` below.
   - `TS`: `20260825T204602`
   - baselines: backups verified present for all 12 files + goose custom_giaoduc.json (extended per Ruling R4: ~/.tdt/config.yaml, ~/.prime/agent/settings.json)

## 2. Hermes (provider block + MoA)

- [x] 2.1 In `~/.hermes/config.yaml`, remove the `giaoduc:` provider block under `providers:`. Verify: `grep -c '^  giaoduc:' ~/.hermes/config.yaml` returns 0.
- [x] 2.2 Replace every MoA preset reference `giaoduc:Advance` with `phanmemvip:gpt-5.6-sol` at the same effort (`default`, `deep`, `fast` reference slots), and swap the `deep` and `default-2` aggregators `giaoduc:Advance` → `phanmemvip:gpt-5.6-sol` (1:1 effort). Verify: `grep -c 'giaoduc' ~/.hermes/config.yaml` returns 0.
- [x] 2.3 Update the direct `fallback_providers` list so the giaoduc entry becomes `provider: phanmemvip, model: gpt-5.6-sol`, preserving order (shopapikey → phanmemvip → cockpit). Verify: `grep -A3 'fallback_providers' ~/.hermes/config.yaml` shows phanmemvip, not giaoduc.
- [x] 2.4 Hermes smoke: run a fresh `moa:default` turn and confirm aggregation completes without a giaoduc reference error. Verify: turn returns a final answer; no `giaoduc` in Hermes logs for the turn.

## 3. tdt-core credential registry

- [x] 3.1 In `~/Developer/tdt-core/src/tdt_core/data/environment-key-registry.json`, add an entry for `HERMES_CUSTOM_PHANMEMVIP_API_KEY` with `secret: true` and `provider: "phanmemvip"`, mirroring the existing shopapikey entry shape. Verify: `python3 -c "import json;d=json.load(open('.../environment-key-registry.json'));print('HERMES_CUSTOM_PHANMEMVIP_API_KEY' in str(d))"` prints True.
- [x] 3.2 Remove the `HERMES_CUSTOM_GIAODUC_API_KEY` entry from the registry. Verify: `grep -c 'HERMES_CUSTOM_GIAODUC_API_KEY' .../environment-key-registry.json` returns 0.
- [x] 3.3 Run tdt-core tests as the gate: `cd ~/Developer/tdt-core && uv run pytest`. Verify: exit 0, no failures. If a test asserts the giaoduc entry, update that test to assert phanmemvip instead and re-run.

## 4. OMP (models.yml + config.yml)

- [x] 4.1 Build an isolated omp profile: copy `~/.omp/agent/models.yml` and a staged `config.yml` into a throwaway profile dir. In the copy, add a `phanmemvip` provider block (`baseUrl: https://api.phanmemvip.shop/v1`, `api: openai-responses`, `apiKey: HERMES_CUSTOM_PHANMEMVIP_API_KEY`, model `gpt-5.6-sol`, 1M context) and remove the giaoduc block. Verify: profile dir contains both files; `grep -c giaoduc <copy>/models.yml` returns 0.
- [x] 4.2 In the staged `config.yml`, rebind `task` from `giaoduc/Advance:xhigh` to `phanmemvip/gpt-5.6-sol:xhigh` and replace giaoduc entries in `retry.fallbackChains` with phanmemvip. Verify: `grep -c giaoduc <staged>/config.yml` returns 0.
- [x] 4.3 Isolated smoke (hard gate): `omp --profile <test> --no-session --model phanmemvip/gpt-5.6-sol:xhigh -p "reply only: pong"` returns `pong` with exit 0. Verify: output `pong`, exit 0. On failure, adjust `baseUrl`/`api` in the copy and re-test before proceeding.
- [x] 4.4 Live atomic update: back up both live files (done in 1.3), stage validated `models.yml` and `config.yml`, `chmod` to match originals, atomic-rename each over the live path sequentially. Verify: both live files parse (`python3 -c "import yaml;yaml.safe_load(open(...))"`), permissions match originals, and `grep -c giaoduc` returns 0 in both.
- [x] 4.5 Live OMP smoke: `omp --no-session --model phanmemvip/gpt-5.6-sol:xhigh -p "reply only: pong"` returns `pong` exit 0; `omp models` lists `phanmemvip` and not `giaoduc`. Verify: both hold.
  > Re-verified 2026-08-25 (independent audit): live config.yml/modelRoles+chains giaoduc-free, phanmemvip live smoke pong exit 0.

## 5. pi (settings.json + models.json)

- [x] 5.1 In `~/.pi/agent/models.json`, add a `phanmemvip` provider block (`baseUrl: https://api.phanmemvip.shop/v1`, `api: openai-responses`, model `gpt-5.6-sol`, 1M context, reasoning) and remove the giaoduc block. Verify: `python3 -c "import json;d=json.load(open('.../models.json'));print('phanmemvip' in d['providers'], 'giaoduc' in d['providers'])"` prints `True False`.
- [x] 5.2 In `~/.pi/agent/settings.json`, set `defaultProvider: phanmemvip` and `defaultModel: gpt-5.6-sol`. Verify: `python3 -c "import json;d=json.load(open('.../settings.json'));print(d['defaultProvider'], d['defaultModel'])"` prints `phanmemvip gpt-5.6-sol`.
- [x] 5.3 pi smoke: run pi with the phanmemvip default and confirm a `pong` response. Verify: response `pong`, exit 0.

## 6. prime-agent (models.json)

- [x] 6.1 In `~/.prime/agent/models.json`, add a `phanmemvip` provider block (`openai-responses`, model `gpt-5.6-sol`) and remove the giaoduc block. Verify: `python3 -c "import json;d=json.load(open('.../models.json'));print('phanmemvip' in d['providers'], 'giaoduc' in d['providers'])"` prints `True False`.
- [x] 6.2 prime-agent smoke: select `phanmemvip/gpt-5.6-sol` and confirm a successful response. Verify: response succeeds, exit 0.

## 7. grok (config.toml)

- [x] 7.1 In `~/.grok/config.toml`, add `[model_providers.phanmemvip]` (`base_url = "https://api.phanmemvip.shop/v1"`, `env_key = "HERMES_CUSTOM_PHANMEMVIP_API_KEY"`, `api_backend = "responses"`, `context_window = 1000000`) and `[model.phanmemvip-sol]` (`model = "gpt-5.6-sol"`); remove the giaoduc provider and model entries. Verify: `grep -c giaoduc ~/.grok/config.toml` returns 0 and `grep -c phanmemvip ~/.grok/config.toml` is > 0.
- [x] 7.2 Set `[models] default = "phanmemvip-sol"`. Verify: `grep 'default = ' ~/.grok/config.toml` shows `phanmemvip-sol`.
- [x] 7.3 grok smoke: run grok with the phanmemvip default and confirm a successful response. Verify: response succeeds, exit 0.

## 8. goose (custom provider + config.yaml)

- [x] 8.1 Create `~/.config/goose/custom_providers/custom_phanmemvip.json` (`engine: openai`, `api_key_env: HERMES_CUSTOM_PHANMEMVIP_API_KEY`, `base_url: https://api.phanmemvip.shop/v1`, model `gpt-5.6-sol`, 1M context, reasoning) mirroring `custom_giaoduc.json` shape. Verify: file parses as JSON and `api_key_env` is `HERMES_CUSTOM_PHANMEMVIP_API_KEY`.
- [x] 8.2 Remove `~/.config/goose/custom_providers/custom_giaoduc.json`. Verify: file no longer exists.
- [x] 8.3 In `~/.config/goose/config.yaml`, replace the `custom_giaoduc` providers-map entry with `custom_phanmemvip` (model `gpt-5.6-sol`, `configured: true`). Verify: `grep -c custom_giaoduc ~/.config/goose/config.yaml` returns 0 and `custom_phanmemvip` is present.
- [x] 8.4 goose smoke: `goose run -p custom_phanmemvip --no-session "reply only: pong"` (or the goose 1.45 equivalent) returns `pong`. Verify: response `pong`, exit 0. If goose 1.45 needs a distinct engine string for `/v1/responses`, adjust `engine` in 8.1 and re-test.

## 9. zshrc & Claude (giaoduc removal only)

- [x] 9.1 In `~/.zshrc`, remove the `giaoduc()` launcher function and the `cline_giaoduc()` launcher function. Do NOT add a phanmemvip launcher. Verify: `grep -c 'giaoduc()' ~/.zshrc` returns 0 and `grep -c 'cline_giaoduc' ~/.zshrc` returns 0.
- [x] 9.2 Remove `~/.claude/profiles/giaoduc.json` and `~/.claude/helpers/giaoduc-key.sh`. Verify: neither file exists.
- [x] 9.3 Fresh-shell check: `zsh -lc 'type giaoduc'` reports not found; `zsh -lc 'type shopapikey'` and `type cockpit` still resolve. Verify: giaoduc undefined, shopapikey/cockpit defined.

## 10. Final Audit & Credential Removal

- [x] 10.1 Audit all config surfaces for residual giaoduc references (excluding backups): `grep -rn 'giaoduc\|Advance' ~/.hermes/config.yaml ~/.omp/agent/ ~/.pi/agent/ ~/.prime/agent/ ~/.grok/config.toml ~/.config/goose/ ~/.zshrc ~/Developer/tdt-core/src/tdt_core/data/environment-key-registry.json 2>/dev/null | grep -v '.bak'`. Verify: zero matches.
- [x] 10.2 Only after 10.1 is clean AND every per-surface smoke test (2.4, 4.5, 5.3, 6.2, 7.3, 8.4) passed: remove the `HERMES_CUSTOM_GIAODUC_API_KEY` line from `~/.hermes/.env`. Verify: `grep -c 'HERMES_CUSTOM_GIAODUC_API_KEY' ~/.hermes/.env` returns 0.
- [x] 10.3 Confirm the shared loader still exports the remaining keys: `zsh -lc 'echo ${HERMES_CUSTOM_PHANMEMVIP_API_KEY:+pmv}${HERMES_CUSTOM_SHOPAPIKEY_API_KEY:+shop}${HERMES_CUSTOM_COCKPIT_API_KEY:+cp}'` prints `pmvshopcp`. Verify: output `pmvshopcp`.

## 11. OpenSpec Housekeeping

- [x] 11.1 Abandon the superseded change: archive `omp-model-role-fallback-tuning` as superseded without applying (its premise — restore giaoduc task role — is invalidated). Moved to `changes/archive/2026-08-25-omp-model-role-fallback-tuning-superseded/` with a `SUPERSEDED.md` guard note (deltas must NOT be synced). Verified 2026-08-25: `openspec list --store openspec-store` no longer shows it as active.
- [x] 11.2 Validate this change strictly: `openspec validate --changes replace-giaoduc-with-phanmemvip --strict --store openspec-store`. Verify: exit 0, no errors.
- [x] 11.3 After apply + verification, sync delta specs to main specs and archive this change: `openspec archive replace-giaoduc-with-phanmemvip --store openspec-store --yes`. Verify: archive succeeds and `openspec validate --all --strict --store openspec-store` passes.
- [x] 11.4 Commit the store: `cd ~/Developer/openspec-store && git add -A && git commit -m "archive: replace-giaoduc-with-phanmemvip"`. Verify: `git status` is clean.
