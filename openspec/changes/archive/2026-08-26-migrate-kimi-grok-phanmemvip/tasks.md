# Tasks: Migrate kimi and grok to phanmemvip

## 1. Backup

- [ ] 1.1 Timestamped backups of `~/.kimi-code/config.toml` and `~/.grok/config.toml`. Verify: both `.bak-pre-kimi-grok.<TS>` exist.

## 2. kimi

- [x] 2.1 In `~/.kimi-code/config.toml`: add `[providers.phanmemvip]` (`type = "openai_responses"`, `base_url = "https://api.phanmemvip.shop/v1"`, `api_key` = value of `HERMES_CUSTOM_PHANMEMVIP_API_KEY`); add `[models.phanmemvip-sol]` (provider phanmemvip, model gpt-5.6-sol, 1M context, thinking) and `[models.phanmemvip-claude-fable]` (provider phanmemvip, model Claude-Fable, 1M context, thinking); set `default_model = "phanmemvip-sol"`; remove the four `dlg/*` OmniRoute model entries (`kimi-k2-6`, `gpt-5-5`, `deepseek-v4-pro`, `deepseek-v4-flash`). Preserve the `moonshot-ai` provider and `kimi-k2-thinking` model. Verify: TOML parses; no `dlg/` references; default_model = phanmemvip-sol.
- [ ] 2.2 kimi smoke: `kimi -p "reply only: pong" --model phanmemvip-sol` → pong exit 0. Verify: pong, exit 0.

## 3. grok

- [x] 3.1 In `~/.grok/config.toml`: change `[model_providers.shopapikey]` `api_backend` from `"messages"` to `"responses"` and remove its `[model_providers.shopapikey.extra_headers]` block. Verify: TOML parses; no `extra_headers` under shopapikey; `api_backend = "responses"`.
- [x] 3.2 grok smoke: `grok -p "reply only: pong"` (default) and `grok --model shopapikey-claude-fable -p "reply only: pong"` → both pong exit 0. Verify: both pong, exit 0.

## 4. Audit & housekeeping

- [x] 4.1 Final audit: `grep -nE "giaoduc|Advance|fable-5|dlg/" ~/.kimi/config.toml ~/.grok/config.toml` returns zero matches. Verify: 0 matches.
- [ ] 4.2 Validate: `openspec validate --changes migrate-kimi-grok-phanmemvip --strict --store openspec-store`. Verify: exit 0.
- [ ] 4.3 Archive: `openspec archive migrate-kimi-grok-phanmemvip --store openspec-store --yes`. Verify: archive succeeds; `openspec validate --all --strict --store openspec-store` passes.
- [ ] 4.4 Commit store. Verify: git clean for this change's files.
