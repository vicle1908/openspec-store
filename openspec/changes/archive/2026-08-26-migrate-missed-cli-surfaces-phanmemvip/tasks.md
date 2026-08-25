# Tasks: Migrate missed CLI surfaces to phanmemvip

## 1. Backup

- [x] 1.1 Timestamped backups of `~/.config/opencode/opencode.json`, `~/.factory/settings.json`, `~/.cline/data/settings/providers.json`. Verify: all `.bak-pre-missed-cli.<TS>` exist.

## 2. opencode

- [x] 2.1 In `~/.config/opencode/opencode.json`: remove the `giaoduc` provider block; add a `phanmemvip` provider block (`baseURL: https://api.phanmemvip.shop/v1`, `api: "responses"`, `apiKey` = value of `HERMES_CUSTOM_PHANMEMVIP_API_KEY`, models: `gpt-5.6-sol` with context 1000000/output 128000); rename shopapikey model `fable-5` → `Claude-Fable`; set `model` and `small_model` to `phanmemvip/gpt-5.6-sol`. Verify: JSON parses; `grep -c giaoduc` = 0; `grep -c fable-5` = 0; phanmemvip provider present.
- [x] 2.2 opencode smoke: `opencode run -m phanmemvip/gpt-5.6-sol "reply only: pong"` → pong exit 0. Verify: pong, exit 0. If `api: "responses"` is rejected, fall back to `npm: "@ai-sdk/openai-compatible"` (chat-completions), record the fallback, and re-test.

## 3. droid

- [x] 3.1 In `~/.factory/settings.json` `customModels`: remove the `Advance` entry; rename the `fable-5` entry's `model` and `displayName` to `Claude-Fable` (keep `anthropic` type + `https://api.phanmemvip.shop` baseUrl); add a `gpt-5.6-sol` entry (`baseUrl: https://api.phanmemvip.shop/v1`, provider `openai`, apiKey = `HERMES_CUSTOM_PHANMEMVIP_API_KEY` value, displayName `Phanmemvip · GPT 5.6 Sol`, maxOutputTokens 16384). Verify: JSON parses; no `Advance`/`giaoduc`/`fable-5` in customModels.
- [x] 3.2 droid smoke: `droid exec --model <gpt-5.6-sol custom model id> "reply only: pong"` (or the droid exec model-selection equivalent) → pong exit 0. Verify: pong, exit 0.

## 4. cline

- [x] 4.1 Re-register cline providers: `cline auth -p openai-native -k <HERMES_CUSTOM_PHANMEMVIP_API_KEY> -m "gpt-5.6-sol" -b "https://api.phanmemvip.shop/v1"`; then remove the `giaoduc` entry from `~/.cline/data/settings/providers.json` and set `lastUsedProvider` to `openai-native`. Verify: providers.json has no giaoduc entry; openai-native references gpt-5.6-sol.

## 5. Re-audit & housekeeping

- [x] 5.1 Re-audit goose/pi/omp/prime-agent for giaoduc/Advance/fable-5 residue (expect zero — no changes). Verify: 0 matches.
- [x] 5.2 Final audit across all seven CLIs: opencode.json, settings.json (droid), providers.json (cline), plus omp/goose/pi/prime configs — zero `giaoduc`/`Advance`/`fable-5` matches. Verify: 0 matches.
- [x] 5.3 Validate: `openspec validate --changes migrate-missed-cli-surfaces-phanmemvip --strict --store openspec-store`. Verify: exit 0.
- [x] 5.4 Archive: `openspec archive migrate-missed-cli-surfaces-phanmemvip --store openspec-store --yes`. Verify: archive succeeds; `openspec validate --all --strict --store openspec-store` passes.
- [x] 5.5 Commit store. Verify: git clean for this change's files.
