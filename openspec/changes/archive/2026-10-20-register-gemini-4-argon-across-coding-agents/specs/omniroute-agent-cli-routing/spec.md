# Spec Delta

## ADDED Requirements

### Requirement: Workstation Coding Agents and Editors SHALL Expose Tiered Gemini 4 Argon Combos Under Existing OmniRoute Providers Without Altering Startup Defaults
All configurable workstation coding agents and editor integrations SHALL register `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` (`1,000,000` context window; `65,536` max output tokens) under their existing active OmniRoute provider blocks, superseding earlier `sh/*`-only model-list restrictions while preserving every tool's pre-mutation startup default model.

#### Scenario: On-demand selection of Gemini 4 Argon tier combos across OpenAI Responses and Anthropic Messages CLIs
- **WHEN** a user invokes `pi`, `prime-agent`, `hermes`, `opencode`, `kilo`, `codex`, `kimi`, `droid`, `claude` (`omniroute-pm.json`), `qwen`, or `muse` with an explicit selector targeting `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low` under its active OmniRoute provider (`omniroute-responses`, `omniroute`, `omniroute-anthropic`, or `meta`)
- **THEN** the CLI resolves all four selectors in its local catalog parser, dispatches the request to `http://localhost:20128` (`http://127.0.0.1:20128/v1` for Muse Code) over its bound wire dialect (`/v1/responses`, `/v1/messages`, or `/v1/chat/completions`) with verified OmniRoute combo attribution (`X-OmniRoute-Combo-Trace` / zero fallback events), and leaves the tool's unflagged startup default model byte-identical to its pre-mutation snapshot

#### Scenario: Rust Serde Chat Completions clients preserve dialect invariants for Gemini 4 Argon combos
- **WHEN** `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` are registered in Block Goose (`~/.config/goose/custom_providers/custom_omniroute.json`) and Grok Build (`~/.grok/config.toml`)
- **THEN** Block Goose retains `OPENAI_BASE_PATH: chat/completions` (`context_limit: 1048576`, `supports_vision: true`) and Grok Build retains `api_backend = "chat_completions"` (`context_window = 1000000`) on `[model.omniroute-gemini-4-argon{,-high,-medium,-low}]` under `model_provider = "omniroute"`, preventing `/v1/responses` keepalive deserialization failures

#### Scenario: Hermes Agent and Claude Code expose all four Gemini 4 Argon selectors while preserving defaults
- **WHEN** `~/.hermes/config.yaml` and `~/.claude/profiles/omniroute-pm.json` are updated to expose the tiered Gemini 4 Argon combos
- **THEN** `~/.hermes/config.yaml` lists `"gemini-4-argon"`, `"gemini-4-argon-high"`, `"gemini-4-argon-medium"`, and `"gemini-4-argon-low"` in `providers.omniroute.models` while preserving `model.provider: "moa"`, and `~/.claude/profiles/omniroute-pm.json` declares all four selectors plus `"gemini-3.8-flash-high"` in `modelPicker.options` (`behavesAs: "claude-fable-5-1"`) while keeping `"model": "gemini-3.8-flash-high"`

### Requirement: Codex CLI and Muse Code Local Model Catalogs SHALL Advertise Tiered Gemini 4 Argon Selectors Without Dirtying Upstream Git
OpenAI Codex CLI (`~/.codex/cockpit-model-catalog.json`) and Meta Muse Code (`~/.config/muse/settings.json`) SHALL declare `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` in their local model catalogs so interactive `/model` and `/models` TUI pickers list all four selectors alongside existing defaults without modifying `~/.codex/config.toml` or any git-tracked file inside `/Users/androidteam/Omniroute`.

#### Scenario: Codex TUI model catalog lists Gemini 4 Argon tiers with standard tool mode and HTTP SSE transport
- **WHEN** `~/.codex/cockpit-model-catalog.json` is loaded via `model_catalog_json` in `~/.codex/config.toml`
- **THEN** the `models[]` array includes `slug` entries for `"gemini-4-argon"`, `"gemini-4-argon-high"`, `"gemini-4-argon-medium"`, and `"gemini-4-argon-low"` with `"visibility": "list"`, `"prefer_websockets": false`, `"use_responses_lite": false`, `"tool_mode": null`, `"apply_patch_tool_type": "freeform"`, `"context_window": 1000000`, and tier-matched `default_reasoning_level` (`"high"`, `"medium"`, `"low"`) while `~/.codex/config.toml` remains unchanged

#### Scenario: Muse Code composes visible Gemini 4 Argon catalog rows from user settings while keeping muse-spark-1.3 as default
- **WHEN** `muse` initializes its model catalog from `~/.config/muse/settings.json`
- **THEN** `model_catalog` declares `muse-spark-1.3` (`is_default: true`, `visibility: "visible"`) and `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low` (`is_default: false`, `provider_id: "meta"`, `profile_id: "tbh"`, `visibility: "visible"`, `context_limit: 1000000`, `output_limit: 65536`) with matching `model_reasoning_efforts`, top-level `"model"` remains `"muse-spark-1.3"`, and `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` outputs zero lines

### Requirement: External Host Config Writes, Mode Tightening, and Kimi Rotation Gates SHALL Enforce Pre-Mutation SHA-256 and Permission Boundaries
All external host configuration mutations under `/Users/androidteam/` SHALL verify pre-write SHA-256 equality against the mode-`0600` backup in `~/.omniroute/backups/register-gemini-4-argon-across-coding-agents/`, enforce mode `0600` on all provider/credential configuration files (`0644` preserved on `~/.codex/cockpit-model-catalog.json`), record named owner approval for `0644 -> 0600` mode tightening, and cite the accepted-risk rotation waiver for `~/.kimi-code/config.toml`.

#### Scenario: Atomic write verification, permission enforcement, and unconfigured CLI preservation
- **WHEN** configuration updates are applied across the coding-agent fleet
- **THEN** each target file's on-disk SHA-256 matches its pre-mutation backup immediately prior to atomic replacement, all provider/credential configs and backups verify at `0600` (`0644` for `~/.codex/cockpit-model-catalog.json`; `~/.factory/settings.json`, `~/.config/muse/settings.json`, and `~/.qwen/settings.json` tightened to `0600`) via `stat -L -f '%04Lp'`, stale `~/.prime/agent/*.bak*` files are relocated out of `~/.prime/agent/`, and unconfigured/vendor-locked CLIs (`qoder`, `cursor-agent`, `auggie`) and legacy `~/.kimi/config.toml` remain untouched
