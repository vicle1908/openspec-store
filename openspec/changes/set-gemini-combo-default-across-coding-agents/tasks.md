# Tasks: Standardize Gemini Combo as Default Across Coding Agents

## 1. Preparation & Pre-mutation Backups

- [x] 1.1 Create mode-600 backups with SHA-256 for all target configuration files:
  - `~/.pi/agent/models.json` & `settings.json`
  - `~/.codex/config.toml`
  - `~/.prime/agent/models.json` & `settings.json`
  - `~/.config/opencode/opencode.json`
  - `~/.grok/config.toml`
  - `~/.factory/settings.json`
  - `~/.config/goose/config.yaml`
- [x] 1.2 Verify OmniRoute loopback health on port 20128 and confirm combo `gemini-3.8-flash-high` is healthy.

## 2. Configuration Mutations

- [x] 2.1 Update Pi coding agent (`~/.pi/agent/models.json` and `settings.json`):
  - Register `gemini-3.8-flash-high` under `omniroute-responses` with `openai-responses` API.
  - Set `defaultProvider: "omniroute-responses"` and `defaultModel: "gemini-3.8-flash-high"`.
- [x] 2.2 Update Codex CLI (`~/.codex/omniroute.config.toml`):
  - Configure `model = "gemini-3.8-flash-high"`, `model_provider = "omniroute"`.
  - Ensure `[model_providers.omniroute]` sets `base_url = "http://localhost:20128/v1"`, `wire_api = "responses"`, `env_key = "OMNIROUTE_API_KEY"`.
- [x] 2.3 Update Prime Agent (`~/.prime/agent/models.json` and `settings.json`):
  - Register `gemini-3.8-flash-high` under `omniroute-responses` provider with `openai-responses` API.
  - Set `defaultProvider: "omniroute-responses"` and `defaultModel: "gemini-3.8-flash-high"`.
- [x] 2.4 Update OpenCode (`~/.config/opencode/opencode.json`):
  - Add `gemini-3.8-flash-high` to `provider.omniroute-responses.models`.
  - Set top-level `model` and subagents to `omniroute-responses/gemini-3.8-flash-high`.
- [x] 2.5 Update Grok Build CLI (`~/.grok/config.toml`):
  - Add `[model.omniroute-gemini-flash]` with `model = "gemini-3.8-flash-high"` and `model_provider = "omniroute"`.
  - Set `[models] default = "omniroute-gemini-flash"`.
- [x] 2.6 Update Factory Droid (`~/.factory/settings.json`):
  - Add `custom:OmniRoute-gemini-3-8-flash-high` to `customModels` with baseUrl `http://localhost:20128/v1`.
  - Set `sessionDefaultSettings.model = "custom:OmniRoute-gemini-3-8-flash-high"`.
- [x] 2.7 Update Block Goose (`~/.config/goose/config.yaml`):
  - Configure `custom_omniroute` provider with `model: gemini-3.8-flash-high`.
  - Set active provider/model in Goose settings.

## 3. Real Sentinel Execution & Validation

- [x] 3.1 Execute direct HTTP sentinel probe against OmniRoute `/v1/responses` with `gemini-3.8-flash-high`.
- [x] 3.2 Execute non-interactive sentinel probe with `pi` using default model.
- [x] 3.3 Execute non-interactive sentinel probe with `prime-agent` using default model.
- [x] 3.4 Execute non-interactive sentinel probe with `opencode` using default model.
- [x] 3.5 Execute non-interactive sentinel probe with `grok` using default model.
- [x] 3.6 Execute non-interactive sentinel probe with `droid` using default model.
- [x] 3.7 Execute non-interactive sentinel probe with `goose` using default model.

## 4. Governance & Finalization

- [x] 4.1 Validate OpenSpec change strictly (`openspec validate ... --strict --store openspec-store`).
- [x] 4.2 Record verification evidence and commit store changes.
