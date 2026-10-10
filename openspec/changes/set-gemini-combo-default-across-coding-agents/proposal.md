# Proposal

## Why

The shared `gemini-3.8-flash-high` combo in OmniRoute is backed by native Antigravity upstream (`providerId: "agy"`, Google Cloud Code `cloudcode-pa.googleapis.com`) with a 15-account Google OAuth connection pool, dynamic load balancing with automatic HTTP 429 rotation, and context cache protection (`context_cache_protection: 1`). Hermes and Oh My Pi (`omp`) already leverage this combo via the OpenAI Responses API (`/v1/responses`) as their default model. However, other coding agents in the workspace (`pi`, `codex`, `grok`, `opencode`, `goose`, `droid`, `prime-agent`) remain defaulted to fragmented endpoints (`Claude-Fable`, `gpt-5.6-sol`, or `codex-x`), missing out on high-speed inference, thinking token emissions, and pool distribution. This change standardizes `gemini-3.8-flash-high` as the default model across all supported coding agents using the OpenAI Responses API / OmniRoute endpoint, with strict pre-mutation backups and live sentinel verification.

## What Changes

1. **Pi Coding Agent (`~/.pi/agent/`)**:
   - Register `gemini-3.8-flash-high` under the `omniroute-responses` provider in `models.json` with `api: "openai-responses"` and `contextWindow: 1000000`.
   - Update `settings.json` default model to `omniroute-responses/gemini-3.8-flash-high`.

2. **Codex CLI (`~/.codex/`)**:
   - Register the `omniroute` provider in `config.toml` targeting `http://localhost:20128/v1` with `wire_api = "responses"`.
   - Set default `model = "gemini-3.8-flash-high"` and `model_provider = "omniroute"`.

3. **Prime Agent (`~/.prime/agent/`)**:
   - Register `gemini-3.8-flash-high` under `omniroute-responses` in `models.json` with `api: "openai-responses"`.
   - Update `settings.json` to default provider `omniroute-responses` and model `gemini-3.8-flash-high`.

4. **OpenCode (`~/.config/opencode/`)**:
   - Register model `gemini-3.8-flash-high` under `omniroute-responses` provider in `opencode.json`.
   - Set primary `model` and subagent models to `omniroute-responses/gemini-3.8-flash-high`.

5. **Grok Build CLI (`~/.grok/`)**:
   - Configure model alias for `gemini-3.8-flash-high` under `omniroute` provider in `config.toml`.
   - Set `[models] default = "omniroute-gemini-flash"`.

6. **Factory Droid (`~/.factory/`)**:
   - Add custom model entry for `gemini-3.8-flash-high` pointing to OmniRoute in `settings.json`.
   - Set `sessionDefaultSettings.model` to the registered model ID.

7. **Block Goose (`~/.config/goose/`)**:
   - Add/update OmniRoute custom provider with model `gemini-3.8-flash-high` and set as active provider.

8. **Verification & Evidence**:
   - Ensure mode-600 backups before any file edit.
   - Execute real non-interactive sentinel calls for each agent to confirm live 200 OK responses with the configured default model.

## Capabilities

### Modified Capabilities

- `omniroute-agent-cli-routing`: Update requirements to approve and mandate `gemini-3.8-flash-high` as the default model via Responses API across the coding agent suite.

## Impact

- Affects local agent configurations in `~/.pi/`, `~/.codex/`, `~/.prime/`, `~/.config/opencode/`, `~/.grok/`, `~/.factory/`, and `~/.config/goose/`.
- Preserves all pre-existing providers for fallback.
- No secrets or credentials committed; all use environment variable indirection (`OMNIROUTE_API_KEY`).
