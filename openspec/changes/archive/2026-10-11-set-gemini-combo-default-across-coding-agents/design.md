# Design: Standardize Gemini Combo as Default Across Coding Agents

## Context

OmniRoute (running on loopback `http://localhost:20128/v1`) provides the `gemini-3.8-flash-high` combo, backed by Google Antigravity native upstream (`agy/gemini-3.8-flash-high` calling Google Cloud Code `cloudcode-pa.googleapis.com`). It features:
1. **15-Account Connection Pool**: Authenticated Google OAuth accounts with dynamic health checking and automatic HTTP 429 backoff rotation.
2. **Context Cache Protection**: Enabled (`context_cache_protection: 1`) to preserve Google Cloud prefix cache hits via session affinity.
3. **Dual Protocol Ingress**:
   - OpenAI Responses API (`/v1/responses`) natively translated to Antigravity payloads with reasoning tokens and tool calling.
   - OpenAI Chat Completions API (`/v1/chat/completions`) for tools strictly requiring classic chat completions.

Hermes and Oh My Pi (`omp`) already run this combo as default via the Responses API. This change updates the remaining coding agents (`pi`, `codex`, `opencode`, `grok`, `droid`, `prime-agent`, `goose`) to target `gemini-3.8-flash-high` as default using the most optimal protocol supported by each CLI.

## Protocol & Agent Mapping Matrix

| Agent | Config Path | Protocol / Dialect | Default Model / Provider |
| :--- | :--- | :--- | :--- |
| **Hermes** | `~/.hermes/config.yaml` | `codex_responses` (`/v1/responses`) | `omniroute:gemini-3.8-flash-high` (already set) |
| **OMP** | `~/.omp/agent/config.yml` | `openai-responses` (`/v1/responses`) | `omniroute/gemini-3.8-flash-high` (already set) |
| **Pi** | `~/.pi/agent/models.json` & `settings.json` | `openai-responses` (`/v1/responses`) | `omniroute-responses/gemini-3.8-flash-high` |
| **Codex** | `~/.codex/config.toml` | `wire_api = "responses"` | `model = "gemini-3.8-flash-high"`, `model_provider = "omniroute"` |
| **Prime Agent** | `~/.prime/agent/models.json` & `settings.json` | `openai-responses` (`/v1/responses`) | `omniroute-responses/gemini-3.8-flash-high` |
| **OpenCode** | `~/.config/opencode/opencode.json` | `@ai-sdk/openai` (`/v1/responses` / `/v1`) | `omniroute-responses/gemini-3.8-flash-high` |
| **Grok** | `~/.grok/config.toml` | `chat_completions` (`/v1`) | `omniroute-gemini-flash` (`gemini-3.8-flash-high`) |
| **Droid** | `~/.factory/settings.json` | Custom OpenAI provider (`/v1`) | `custom:OmniRoute-gemini-3-8-flash-high` |
| **Goose** | `~/.config/goose/config.yaml` | Custom OmniRoute provider (`/v1`) | `custom_omniroute:gemini-3.8-flash-high` |

## Safety & Governance Rules

1. **Pre-mutation Backups**:
   - Every file to be edited receives a timestamped `.bak` with permissions `0600`.
   - Record SHA-256 before and after mutation.
2. **Credential Indirection**:
   - References `OMNIROUTE_API_KEY` (or agent-native env indirection). No literal API keys in configurations or evidence.
3. **Rollback Strategy**:
   - If parse validation or live sentinel execution fails for any agent, restore the corresponding configuration file immediately from its backup.
4. **Live Execution Gate**:
   - Each mutated CLI must execute an isolated one-turn non-interactive query with a sentinel string (e.g. "Echo PONG") and return exit code 0.
