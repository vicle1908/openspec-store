# Tasks

## 1. OmniRoute Pool Hygiene & 429 Remediation

- [x] 1.1 Evict banned connection `20369f65-4fae-4fa0-b02b-4f15047bee79` (`phamkive425@gmail.com`) from `gemini-3.8-flash-high`, `claude-opus-5.5`, and `claude-sonnet-5.5` in OmniRoute SQLite `combos`, ensuring zero banned accounts remain in any combo definition.
- [x] 1.2 Prune quota-exhausted account `ce95e1cb-27a4-433f-9c50-bdb6ad0b6b6b` (`vicgnome19097@gmail.com`, 0% weekly Gemini quota) from `gemini-3.8-flash-high`, leaving 9 healthy Pro accounts with 87%–100% remaining quota.

## 2. Codex Tool-Calling Protection & Primary Agent Role Upgrades

- [x] 2.1 Set `web_search = "disabled"` in `/Users/androidteam/.codex/config.toml` (`mode 0600`) and set `supports_search_tool = false`, `context_window = 1000000`, `prefer_websockets = false` across all 10 OmniRoute slugs in `/Users/androidteam/.codex/cockpit-model-catalog.json` (`mode 0644`).
- [x] 2.2 Configure `agent.plan`, `agent.orchestrator`, `agent.debug`, and `agent.code` in `/Users/androidteam/.config/kilo/kilo.jsonc` (`mode 0600`) and `/Users/androidteam/.local/state/kilo/model.json` to active OmniRoute combos.
- [x] 2.3 Add `modelThinkingLevels` for all 10 OmniRoute combos in `/Users/androidteam/.pi/agent/settings.json` (`mode 0600`), and configure `providerBackupModel = "omniroute-responses/claude-sonnet-5.5"` and `callTimeoutMs = 300000` in `/Users/androidteam/.prime/agent/settings.json` (`mode 0600`).
- [x] 2.4 Configure `agent.oracle.model` (`omniroute-responses/claude-opus-5.5`) and `agent.librarian.model` (`omniroute-responses/gemini-3.8-flash-high`) in `/Users/androidteam/.config/opencode/opencode.json` (`mode 0600`) and `/Users/androidteam/.local/state/opencode/model.json`.
- [x] 2.5 Configure `agent.reasoning_overrides` and cross-family Mixture-of-Agents (`moa.presets.deep`) in `/Users/androidteam/.hermes/config.yaml` (`mode 0600`).

## 3. Secondary Agent Upgrades & Live High-Concurrency Verification

- [x] 3.1 Upgrade multimodal vision in `/Users/androidteam/.kimi-code/config.toml` (`mode 0600`), fork secondary model in `/Users/androidteam/.grok/config.toml` (`mode 0600`), planner model in `/Users/androidteam/.config/goose/config.yaml` (`mode 0600`), 800K compaction and mission models in `/Users/androidteam/.factory/settings.json` (`mode 0600`), modelOverrides in `/Users/androidteam/.claude/profiles/omniroute-pm.json` (`mode 0600`), generationConfig in `/Users/androidteam/.qwen/settings.json` (`mode 0600`), and thinking defaults in `/Users/androidteam/.config/zed/settings.json` (`mode 0600`).
- [x] 3.2 Execute 10 concurrent requests to `gemini-3.8-flash-high` (verifying 100% HTTP 200 and zero 429s) and multi-turn tool-calling verification across all coding agents.
