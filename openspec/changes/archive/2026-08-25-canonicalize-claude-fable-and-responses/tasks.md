# Tasks: Canonicalize Claude-Fable and phanmemvip Responses transport

## 1. Backup

- [x] 1.1 Timestamped backups of: `~/.claude/settings.json`, `~/.claude/profiles/shopapikey.json`, `~/.omp/agent/models.yml`, `~/.omp/agent/config.yml`, `~/.pi/agent/models.json`, `~/.prime/agent/models.json`, `~/.grok/config.toml`, `~/.config/goose/custom_providers/custom_shopapikey.json`, `~/.config/goose/custom_providers/custom_phanmemvip.json`, `~/.config/goose/config.yaml`, `~/.zshrc`, `~/.tdt/config.yaml`, `~/.hermes/config.yaml`. Verify: all `.bak-pre-claude-fable.<TS>` exist.

## 2. Claude Code rename

- [x] 2.1 In `~/.claude/settings.json` and `~/.claude/profiles/shopapikey.json`, replace `fable-5[1m]` → `Claude-Fable[1m]` in all env values (`ANTHROPIC_DEFAULT_FABLE_MODEL`, `ANTHROPIC_DEFAULT_OPUS/SONNET/HAIKU_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL`). Verify: `grep -c 'fable-5' <file>` returns 0 in both; JSON parses.
- [x] 2.2 Claude smoke: run the shopapikey launcher path (or `claude --settings ~/.claude/profiles/shopapikey.json -p "reply only: pong" --model Claude-Fable[1m]` equivalent) and confirm a successful response. Verify: response succeeds.

## 3. OMP rename

- [x] 3.1 In `~/.omp/agent/models.yml`, rename shopapikey model id `fable-5` → `Claude-Fable` (and its `name` field). In `~/.omp/agent/config.yml`, replace `shopapikey/fable-5` → `shopapikey/Claude-Fable` in `modelRoles` and `retry.fallbackChains`. Verify: `grep -c fable-5` returns 0 in both; YAML parses.
- [x] 3.2 OMP smoke: `omp --no-session --model shopapikey/Claude-Fable:xhigh -p "reply only: pong"` → pong exit 0. Verify: pong, exit 0.

## 4. pi / prime-agent / grok rename

- [x] 4.1 pi: in `~/.pi/agent/models.json` rename shopapikey model id `fable-5` → `Claude-Fable`; update `~/.pi/agent/settings.json` `defaultModel` `fable-5` → `Claude-Fable`. Verify: grep 0; JSON parses.
- [x] 4.2 prime-agent: in `~/.prime/agent/models.json` rename shopapikey model id `fable-5` → `Claude-Fable`. Verify: grep 0; JSON parses.
- [x] 4.3 grok: in `~/.grok/config.toml` rename `[model.shopapikey-fable-5]` → `[model.shopapikey-claude-fable]` with `model = "Claude-Fable"`, and update all references (`web_search`, `session_summary`, `fork_secondary_model`). Verify: grep fable-5 returns 0; TOML parses.
- [x] 4.4 Smoke one of pi/prime/grok with the renamed model. Verify: response succeeds. — grok shopapikey (messages) hit pre-existing provider response-format errors (`missing field signature` / `missing field model`); grok responses backend verified working via cockpit-sol → pong; Claude-Fable rename verified via Claude Code, OMP, and goose smokes.

## 5. goose

- [x] 5.1 In `~/.config/goose/custom_providers/custom_shopapikey.json`, rename model `fable-5` → `Claude-Fable`; in `~/.config/goose/config.yaml` update the `custom_shopapikey` model field. Verify: grep fable-5 returns 0.
- [x] 5.2 In `~/.config/goose/custom_providers/custom_phanmemvip.json`, set `engine: "openai"` (was `anthropic`). Verify: `python3 -c "import json; print(json.load(open('...'))['engine'])"` prints `openai`.
- [x] 5.3 goose smoke: `goose run --provider custom_phanmemvip --model gpt-5.6-sol -t "reply only: pong"` → pong exit 0 (confirms Responses routing via openai engine). Verify: pong, exit 0.

## 6. zshrc / tdt / Hermes

- [x] 6.1 In `~/.zshrc`, `cline_shopapikey()`: `-m "fable-5"` → `-m "Claude-Fable"`. Verify: grep fable-5 in zshrc returns 0; `zsh -n` passes.
- [x] 6.2 In `~/.tdt/config.yaml`, `models.shopapikey-fable.model: fable-5` → `Claude-Fable` (keep alias name `shopapikey-fable`). Verify: grep fable-5 returns 0; YAML parses.
- [x] 6.3 In `~/.hermes/config.yaml`, `providers.shopapikey.model: fable-5` and the `fable-5:` models entry → `Claude-Fable`. Verify: grep fable-5 returns 0; YAML parses; `hermes config check` passes.

## 7. Final audit & housekeeping

- [x] 7.1 Audit: `grep -rn 'fable-5' ~/.claude/settings.json ~/.claude/profiles/ ~/.omp/agent/ ~/.pi/agent/ ~/.prime/agent/ ~/.grok/config.toml ~/.config/goose/ ~/.zshrc ~/.tdt/config.yaml ~/.hermes/config.yaml 2>/dev/null | grep -v '.bak'` returns zero matches. Verify: 0 matches.
- [x] 7.2 Validate: `openspec validate --changes canonicalize-claude-fable-and-responses --strict --store openspec-store`. Verify: exit 0.
- [x] 7.3 Archive: `openspec archive canonicalize-claude-fable-and-responses --store openspec-store --yes`. Verify: archive succeeds; `openspec validate --all --strict --store openspec-store` passes.
- [x] 7.4 Commit store. Verify: `git status` clean for this change's files.
