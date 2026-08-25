# Tasks: omp-model-role-fallback-tuning

## 1. Prerequisites

- [x] 1.1 Verify giaoduc credentials are valid by running `omp --no-session --model giaoduc/Advance:xhigh -p "reply only: pong"` and confirming exit 0. If it returns `401 invalid_api_key`, **pause apply** and inform the user that `/Users/androidteam/.omp/agent/.env` (or the relevant credential loader) must be repaired outside this change's scope before the nine-selector smoke test can pass. Do not attempt credential repair.
- [x] 1.2 Build isolated smoke-test profile: copy `/Users/androidteam/.omp/agent/models.yml` and a staged temporary `config.yml` (containing the proposed role/fallback content) into a throwaway profile directory; do not touch live credentials or live config paths. Verify: profile dir contains both files.

## 2. Isolated Smoke Tests (hard gate — all nine must pass)

- [ ] 2.1 For each of the nine role selectors, run `omp --profile <test> --no-session --model <selector> -p "reply only: pong"` and confirm "pong" with exit 0: `openrouter/stealth/ox-alpha:max`, `cockpit/gpt-5.6-luna:max`, `cockpit/gpt-5.6-sol:max`, `giaoduc/Advance:xhigh`, `cockpit/gpt-5.6-sol:xhigh`, `google-antigravity/gemini-3.7-flash:high` (used by `smol`, `tiny`, `vision`), `shopapikey/fable-5:low`. A giaoduc 401 blocks apply and returns to task 1.1.
- [ ] 2.2a Isolated chain-hopping check, case A (giaoduc-only failure, first hop): within the throwaway profile, point the profile-copy's giaoduc `apiKey` at a deliberately invalid env-var name (fable-5 and sol remain valid). Run `omp --profile <test> --no-session --model giaoduc/Advance:xhigh -p "reply only: pong"`. Verify: the request recovers to `shopapikey/fable-5` and returns "pong" with exit 0.
- [ ] 2.2b Isolated chain-hopping check, case B (giaoduc + fable-5 both fail, second hop): within the throwaway profile, point both giaoduc and fable-5 `apiKey` at invalid env-var names (sol remains valid). Run the same command. Verify: the request recovers to `cockpit/gpt-5.6-sol` and returns "pong" with exit 0.
- [ ] 2.3 Restore or discard the throwaway profile; confirm no live files or credentials were mutated during steps 2.2a/2.2b.

## 3. Live Atomic Config Update (sequential per canonical requirement)

- [ ] 3.1 Create timestamped backups of both live files, capturing the timestamp for reuse:
   ```bash
   TS=$(date +%Y%m%dT%H%M%S)
   cp /Users/androidteam/.omp/agent/models.yml "/Users/androidteam/.omp/agent/models.yml.bak.$TS"
   cp /Users/androidteam/.omp/agent/config.yml "/Users/androidteam/.omp/agent/config.yml.bak.$TS"
   ```
   Record both `md5 -q` baselines. Verify: both backup files exist and hashes are recorded below.
   - `TS`: `<record>`
   - `models.yml` baseline md5: `<record>`
   - `config.yml` baseline md5: `<record>`
- [ ] 3.2 Stage the fully validated `config.yml` (same content as the tested profile copy) in the same filesystem as the live file; set its permissions to match the live original (`chmod $(stat -f '%Lp' /Users/androidteam/.omp/agent/config.yml) <staged-file>`), then atomically rename it over the live path (`mv <staged-file> /Users/androidteam/.omp/agent/config.yml`). Do NOT touch `models.yml`. Verify: `config.yml` permissions match the original and `md5 -q /Users/androidteam/.omp/agent/models.yml` still equals the 3.1 baseline.
- [ ] 3.3 Verify `models.yml` is byte-identical after the rename. Verify: `diff -q /Users/androidteam/.omp/agent/models.yml "/Users/androidteam/.omp/agent/models.yml.bak.$TS"` reports no differences.

## 4. Post-Apply Verification

- [ ] 4.1 Authoritative validation: parse with `uv run --with pyyaml python -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" /Users/androidteam/.omp/agent/config.yml` and confirm exit 0.
- [ ] 4.2 Cross-check selectors: run `omp config list --json` (or `omp --no-session --model <selector> -p "reply only: pong"` for each) to confirm every non-wildcard selector in `modelRoles` and every chain entry resolves against the effective catalog (`models.yml` ids plus native providers `openrouter`, `google-antigravity`). For wildcard chain keys (`google-antigravity/*`) and wildcard entries (`google/*`, `google-vertex/*`), validate the `provider/*` syntax format; absent target providers are expected and permitted per the spec ("skipped if absent"). Verify: script reports zero unknown non-wildcard selectors and all wildcard entries match `provider/*` syntax.
- [ ] 4.3 Diff final config against every spec scenario (chain order, cockpit/giaoduc/antigravity chains, `:high` flash suffixes, no `omniroute/`). Verify: scenario-by-scenario checklist all pass.
- [ ] 4.4 If any live verification fails, restore both backups from `$TS` and verify `md5 -q` of each restored file equals the 3.1 baselines. Verify: both hashes match.

## 5. Wrap-up

- [ ] 5.1 Report applied config and smoke-test evidence to user; note a running OMP process needs a reload/new session to pick up changes. Verify: user-visible summary delivered.