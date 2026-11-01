# omniroute-agent-cli-routing Spec Delta

## MODIFIED Requirements

### Requirement: Codex CLI and Muse Code Local Model Catalogs SHALL Advertise Tiered Gemini 4 Argon Selectors Without Dirtying Upstream Git
Codex CLI and Muse Code local model catalogs SHALL advertise tiered Gemini 4 Argon selectors with `web_search = "disabled"` and `supports_search_tool: false` on OmniRoute Gemini slugs to protect Gemini `functionDeclarations` tool translation without modifying git-tracked files in `/Users/androidteam/Omniroute`.

#### Scenario: Codex TUI model catalog lists Gemini 4 Argon tiers with standard tool mode and HTTP SSE transport
- **WHEN** `~/.codex/cockpit-model-catalog.json` and `~/.codex/config.toml` are inspected
- **THEN** `~/.codex/config.toml` SHALL declare `web_search = "disabled"` and `[model_providers.omniroute]` with `http_headers = { "x-omniroute-no-memory" = "true" }`
- **AND** `~/.codex/cockpit-model-catalog.json` SHALL declare `supports_search_tool: false`, `context_window: 1000000`, `prefer_websockets: false`, `use_responses_lite: false`, and `tool_mode: null` across all 10 OmniRoute slugs

#### Scenario: Muse Code composes visible Gemini 4 Argon catalog rows from user settings while keeping muse-spark-1.3 as default
- **WHEN** `muse` initializes its model catalog from `~/.config/muse/settings.json`
- **THEN** `model_catalog` declares `muse-spark-1.3` (`is_default: true`, `visibility: "visible"`) and `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low` (`is_default: false`, `provider_id: "meta"`, `profile_id: "tbh"`, `visibility: "visible"`, `context_limit: 1000000`, `output_limit: 65536`) with matching `model_reasoning_efforts`, top-level `"model"` remains `"muse-spark-1.3"`, and `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` outputs zero lines
