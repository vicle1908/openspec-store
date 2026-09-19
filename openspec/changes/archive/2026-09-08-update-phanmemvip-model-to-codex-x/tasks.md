# Tasks: Update phanmemvip Model from gpt-5.6-sol to codex-x + Rotate API Key

**Scope:** phanmemvip provider, OmniRoute routing, and OMP fallback optimization. Cockpit remains separate and unchanged; shopapikey remains separate with Claude-Fable.
**New key:** `pmv_OZht_ENR3m3tsTVWODbmaYbYhLSEYD7t` (verified: codex-x returns pong)
**Total:** 55 edits across 23 files, 24 tasks

## Tasks

### Task 1: Update `~/.hermes/config.yaml` — provider default
- [x] L307: `model: gpt-5.6-sol` → `model: codex-x`
- [x] Verify: `sed -n '307p' ~/.hermes/config.yaml` shows `codex-x`

### Task 2: Update `~/.hermes/config.yaml` — global fallback
- [x] L328: `model: gpt-5.6-sol` → `model: codex-x`
- [x] Verify: `sed -n '328p' ~/.hermes/config.yaml` shows `codex-x`

### Task 3: Update `~/.hermes/config.yaml` — goose custom_phanmemvip
- [x] L416: `model: gpt-5.6-sol` → `model: codex-x`
- [x] Verify: `sed -n '416p' ~/.hermes/config.yaml` shows `codex-x`

### Task 4: Update `~/.hermes/config.yaml` — MoA presets (phanmemvip only)
- [x] L534: `model: gpt-5.6-sol` → `model: codex-x`
- [x] L564: `model: gpt-5.6-sol` → `model: codex-x`
- [x] L569: `model: gpt-5.6-sol` → `model: codex-x`
- [x] L607: `model: gpt-5.6-sol` → `model: codex-x`
- [x] L617: `model: gpt-5.6-sol` → `model: codex-x`
- [x] Verify: cockpit lines (L526, L538, L560, L581, L602, L621) unchanged

### Task 5: Update `~/.config/goose/` (2 files)
- [x] `config.yaml` L159: `model: gpt-5.6-sol` → `model: codex-x`
- [x] `config.yaml` L163: `model: gpt-5.6-sol` → `model: codex-x`
- [x] `custom_providers/custom_phanmemvip.json` L10: `"name": "gpt-5.6-sol"` → `"name": "codex-x"`
- [x] Verify: `grep -rn 'gpt-5.6-sol' ~/.config/goose/ | grep -v '.bak'` returns 0

### Task 6: Update `~/.grok/config.toml` — phanmemvip model
- [x] L53: `model = "gpt-5.6-sol"` → `model = "codex-x"`
- [x] L54: `name = "gpt-5.6-sol (phanmemvip)"` → `name = "codex-x (phanmemvip)"`
- [x] Verify: cockpit (L58-59) and omniroute (L74-75) untouched

### Task 7: Update `~/.omp/agent/config.yml`
- [x] L8: `task: phanmemvip/gpt-5.6-sol:xhigh` → `task: phanmemvip/codex-x:xhigh`
- [x] L64: `- phanmemvip/gpt-5.6-sol:xhigh` → `- phanmemvip/codex-x:xhigh`
- [x] L69: `phanmemvip/gpt-5.6-sol:` → `phanmemvip/codex-x:`
- [x] L92: `- phanmemvip/gpt-5.6-sol:xhigh` → `- phanmemvip/codex-x:xhigh`
- [x] Verify: `grep -n 'gpt-5.6-sol' ~/.omp/agent/config.yml | grep phanmemvip` returns 0

### Task 8: Update `~/.omp/agent/models.yml`
- [x] L132: `id: gpt-5.6-sol` → `id: codex-x`
- [x] L133: `name: gpt-5.6-sol (phanmemvip)` → `name: codex-x (phanmemvip)`
- [x] Verify: omniroute (L70-71, L195-196) and cockpit (L155-156) untouched

### Task 9: Update `~/.pi/agent/models.json` (4 edits)
- [x] L9: `"id": "gpt-5.6-sol"` → `"id": "codex-x"`
- [x] L10: `"name": "gpt-5.6-sol"` → `"name": "codex-x"`
- [x] L273: `"id": "gpt-5.6-sol"` → `"id": "codex-x"`
- [x] L274: `"name": "gpt-5.6-sol"` → `"name": "codex-x"`
- [x] Verify: omniroute sh/ (L180-181, L325-326) untouched

### Task 10: Update `~/.pi/agent/settings.json`
- [x] L39: `"phanmemvip/gpt-5.6-sol": "xhigh"` → `"phanmemvip/codex-x": "xhigh"`
- [x] Verify: cockpit (L31) untouched

### Task 11: Update `~/.config/opencode/opencode.json` — model references
- [x] L8: `"model": "phanmemvip/gpt-5.6-sol"` → `"model": "phanmemvip/codex-x"`
- [x] L9: `"small_model": "phanmemvip/gpt-5.6-sol"` → `"small_model": "phanmemvip/codex-x"`
- [x] L14: explore agent → `"model": "phanmemvip/codex-x"`
- [x] L24: oracle agent → `"model": "phanmemvip/codex-x"`
- [x] L35: frontend agent → `"model": "phanmemvip/codex-x"`
- [x] L41: docwriter agent → `"model": "phanmemvip/codex-x"`
- [x] L189: `"gpt-5.6-sol": {` → `"codex-x": {`
- [x] L190: `"name": "GPT 5.6 Sol"` → `"name": "Codex X"`
- [x] Verify: omniroute (L58/206) and cockpit (L117) untouched

### Task 12: Update `~/.kimi-code/config.toml` — phanmemvip model
- [x] L47: `model = "gpt-5.6-sol"` → `model = "codex-x"`
- [x] Verify: cockpit (L65) and omniroute (L71) untouched

### Task 13: Update `~/.factory/settings.json` (4 edits)
- [x] L26: `"model": "gpt-5.6-sol"` → `"model": "codex-x"`
- [x] L27: `"id": "custom:phanmemvip-gpt-5.6-sol-0"` → `"id": "custom:phanmemvip-codex-x-0"`
- [x] L31: `"displayName": "Phanmemvip · GPT 5.6 Sol"` → `"displayName": "Phanmemvip · Codex X"`
- [x] L71: `"validationWorkerModel": "custom:phanmemvip-gpt-5.6-sol-0"` → `"validationWorkerModel": "custom:phanmemvip-codex-x-0"`
- [x] Verify: `grep -n 'gpt-5.6-sol' ~/.factory/settings.json` returns 0

### Task 14: Update tdt-core test
- [x] L38: `model: gpt-5.6-sol` → `model: codex-x`
- [x] L60: `"codex:gpt-5.6-sol"` → `"codex:codex-x"`
- [x] L61: `"gpt-5.6-sol"` → `"codex-x"`
- [x] L128: `gpt-5.6-sol` → `codex-x`
- [x] Verify: `grep -n 'gpt-5.6-sol' ~/Developer/tdt-core/scripts/verify_v2_codex_acceptance.py` returns 0

### Task 15: Rotate phanmemvip API key — `~/.zshenv`
- [x] L16: `HERMES_CUSTOM_PHANMEMVPNPMVIP_API_KEY='pmv_-I8OvaQ2JHeK7X5z-RHpSCCekkjoErEG'` → `HERMES_CUSTOM_PHANMEMVPNPMVIP_API_KEY='pmv_OZht_ENR3m3tsTVWODbmaYbYhLSEYD7t'`
- [x] Verify: `source ~/.zshenv && echo $HERMES_CUSTOM_PHANMEMVPNPMVIP_API_KEY` shows new key

### Task 16: Rotate phanmemvip API key — `~/.kimi-code/config.toml`
- [x] L27: `api_key = "pmv_-I8OvaQ2JHeK7X5z-RHpSCCekkjoErEG"` → `api_key = "pmv_OZht_ENR3m3tsTVWODbmaYbYhLSEYD7t"`
- [x] Verify: `grep 'api_key.*pmv' ~/.kimi-code/config.toml` shows new key

### Task 17: Update `~/.prime/agent/models.json` (1 edit)
- [x] L9: `"id": "gpt-5.6-sol"` → `"id": "codex-x"` (phanmemvip provider)
- [x] L10: `"name": "gpt-5.6-sol (phanmemvip)"` → `"name": "codex-x (phanmemvip)"`
- [x] Verify: cockpit (L37-38) and omniroute (L73, L90) untouched

### Task 18: Update `~/.prime/agent/settings.json` (1 edit)
- [x] L10: `"phanmemvip/gpt-5.6-sol"` → `"phanmemvip/codex-x"` in recentModels
- [x] Verify: defaultModel "Claude-Fable" untouched

### Task 19: Update `~/.cline/data/settings/models.json` — fix shopapikey + add phanmemvip
- [x] Fix shopapikey: `fable-5` → `Claude-Fable` (model id, name, defaultModelId)
- [x] Add phanmemvip provider with `codex-x` model (baseUrl, protocol, capabilities)
- [x] Verify: both shopapikey/Claude-Fable and phanmemvip/codex-x present

### Task 20: Final verification
- [x] No phanmemvip gpt-5.6-sol remaining (excluding cockpit/omniroute)
- [x] Cockpit references still present
- [x] Shopapikey references untouched
- [x] All CLIs support both shopapikey (Claude-Fable) and phanmemvip (codex-x)
- [x] YAML valid: `python3 -c "import yaml; yaml.safe_load(open('$HOME/.hermes/config.yaml'))"`
- [x] JSON valid: all config files parse without error
- [x] API test: codex-x with new key returns pong

### Task 21: Update OmniRoute shopapikey provider — delete main-2, re-add with new key
- [x] Deleted broken main-2 connection (Claude-Fableol forbidden)
- [x] Added new main-2 with API key pmv_OZht_ENR3m3tsTVWODbmaYbYhLSEYD7t
- [x] Default model: codex-x
- [x] 11 models imported from phanmemvip API
- [x] Connection status: connected ✅

### Task 22: Enable OmniRoute main connection + verify both models
- [x] Enabled main connection (was disabled)
- [x] main-2 connection: connected with codex-x ✅
- [x] main connection: connected with Claude-Fable ✅
- [x] sh/codex-x via OmniRoute: pong ✅
- [x] pm/Claude-Fable via OmniRoute: pong ✅

### Task 23: Update sh/ OmniRoute model references to sh/codex-x
- [x] goose config.yaml L175: sh/gpt-5.6-sol → sh/codex-x
- [x] kimi-code config.toml L71: sh/gpt-5.6-sol → codex-x
- [x] pi models.json L180, L325: sh/gpt-5.6-sol → sh/codex-x
- [x] opencode.json L58, L206: sh/gpt-5.6-sol → sh/codex-x
- [x] factory settings.json L37: sh/gpt-5.6-sol → sh/codex-x
- [x] prime-agent models.json L73, L90: sh/gpt-5.6-sol → sh/codex-x
- [x] OMP models.yml: already had sh/codex-x ✅
- [x] Verify: all CLIs have sh/codex-x

### Task 24: Final verification — all CLIs support sh/Claude-Fable + sh/codex-x
- [x] goose: sh/codex-x ✅
- [x] kimi-code: codex-x ✅
- [x] pi: sh/codex-x + sh/Claude-Fable ✅
- [x] opencode: sh/codex-x + sh/Claude-Fable ✅
- [x] factory: sh/codex-x ✅
- [x] prime-agent: sh/codex-x ✅
- [x] OMP: sh/codex-x ✅
- [x] OmniRoute: both sh/codex-x and pm/Claude-Fable verified working

### Task 25: Optimize OMP OmniRoute fallback routing
- [x] Add `omniroute/sh/Claude-Fable:xhigh` to the default fallback chain in `~/.omp/agent/config.yml`
- [x] Add `omniroute/sh/Claude-Fable:xhigh` to the `phanmemvip/codex-x` fallback chain
- [x] Preserve `omniroute/sh/codex-x:xhigh` as task/default
- [x] Preserve direct `phanmemvip/codex-x` and `shopapikey/Claude-Fable` fallbacks
- [x] Preserve cockpit as a separate provider

### Task 26: Verify OMP fallback behavior
- [x] Validate `~/.omp/agent/config.yml`
- [x] Run OMP with `omniroute/sh/codex-x`
- [x] Run OMP with `omniroute/sh/Claude-Fable`
- [x] Confirm both return successful responses

### Task 27: Final verification after OMP optimization
- [x] All direct phanmemvip CLI tests pass
- [x] Both OmniRoute routes pass
- [x] OMP default remains `omniroute/sh/codex-x:xhigh`
- [x] OMP fallback includes `omniroute/sh/Claude-Fable:xhigh`

### Task 28: Remove legacy Giaoduc from active CLI configuration
- [x] Remove the active `giaoduc` provider block from `~/.cline/data/settings/models.json`
- [x] Remove any other active CLI provider entries using `giaoduc`, `GIAODUC`, or `api.giaoduc.online`
- [x] Preserve historical backups, logs, sessions, and archived artifacts
- [x] Verify active CLI configs contain only shopapikey, phanmemvip, cockpit, and OmniRoute provider families
- [x] Verify Cline still exposes `shopapikey/Claude-Fable` and `phanmemvip/codex-x` after removal

### Task 30: Update Hermes cockpit MoA references to gpt-6-astra
- [x] Add `gpt-6-astra: {}` to the cockpit model catalog in `~/.hermes/config.yaml`
- [x] Change `goals.goal_judge` cockpit model to `gpt-6-astra`
- [x] Change cockpit references in `moa.presets.default`, `deep`, `fast`, and `default-2` to `gpt-6-astra`
- [x] Change the global MoA cockpit reference to `gpt-6-astra`
- [x] Preserve cockpit as a separate provider

### Task 31: Verify Hermes MoA cockpit configuration
- [x] Validate `~/.hermes/config.yaml`
- [x] Verify no intended MoA cockpit reference uses `gpt-5.6-sol`
- [x] Test cockpit `gpt-6-astra` through its configured endpoint — PASS
- [x] Confirm phanmemvip, shopapikey, cockpit, and OmniRoute remain configured

### Task 32: Add missing provider families to Goose and Cline
- [x] Add cockpit provider/model configuration to `~/.config/goose/config.yaml`
- [x] Preserve Goose shopapikey, phanmemvip, and OmniRoute providers
- [x] Add cockpit provider to `~/.cline/data/settings/models.json` using `http://localhost:51006/v1`
- [x] Add OmniRoute provider to `~/.cline/data/settings/models.json` using `http://localhost:20128/v1`
- [x] Add Cline OmniRoute models `sh/codex-x`, `sh/Claude-Fable`, and `pm/Claude-Fable`
- [x] Preserve Cline shopapikey/Claude-Fable and phanmemvip/codex-x

### Task 33: Verify complete four-provider topology
- [x] Validate all active JSON/YAML/TOML configuration files
- [x] Confirm every active coding CLI exposes shopapikey, phanmemvip, cockpit, and OmniRoute
- [x] Run direct phanmemvip `codex-x` test
- [x] Run direct shopapikey `Claude-Fable` test
- [x] Run OmniRoute `sh/codex-x` test
- [x] Run OmniRoute `sh/Claude-Fable` test
- [x] Run OMP with both OmniRoute models
- [x] Run Cline with direct and OmniRoute models
- [x] Confirm no active Giaoduc provider remains
- [x] Confirm Hermes MoA uses cockpit `gpt-6-astra` for all intended references
- [x] Confirm cockpit remains configured and separate

### Task 34: Resolve external cockpit verification
- [x] Test cockpit `gpt-6-astra` after upstream cooldown expires — PASS
- [x] Record successful response

### Task 35: Final provider topology verification
- [x] Confirm all four providers are configured for every active coding CLI
- [x] Confirm all direct, OmniRoute, and OMP tests pass
- [x] Confirm OpenSpec validation passes before archive

