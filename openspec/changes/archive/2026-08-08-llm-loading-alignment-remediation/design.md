# Design: LLM Loading and CLI-Agent Alignment Remediation

## Model Resolution

`create_model()` and `create_fallback_model()` continue to delegate model-class and endpoint selection to `pydantic_ai.models.infer_model()`.

Provider selection follows this order:

1. Exact provider `model_names` entries from `~/.tdt/config.yaml`.
2. The model-kind prefix mapping (`anthropic`, `openai-chat`, `openai-responses`).
3. The legacy single-provider model configuration.
4. Native pydantic-ai environment resolution.

The model-kind prefix remains authoritative for the endpoint:

- `anthropic:*` → Anthropic Messages
- `openai-chat:*` → Chat Completions
- `openai-responses:*` → Responses API

`api_mode` selects the compatible pydantic-ai provider class. A configured `anthropic_messages` mode is valid only for `anthropic:*`; an OpenAI mode is valid for OpenAI model kinds. Incompatible combinations fail before `infer_model()` constructs a mismatched model/provider pair.

Provider-specific model routing uses an optional `model_names` list. This lets `openai-responses:gpt-5.6-sol` route to cockpit while `openai-responses:fable-5` routes to shopapikey, without inventing an unsupported pydantic-ai prefix or treating `fable-5` as a prefix.

## Runtime Fallback Loading

The CLI prompt path chooses:

- `create_model(settings.model.primary)` when no fallback models are configured.
- `create_fallback_model(settings.model.primary, settings.model.fallback)` when the fallback list is non-empty.

The native `FallbackModel` exception policy remains centralized in `_ai/models.py`.

## Documentation and Specification Alignment

The example YAML uses the current `model:` and `providers:` sections, contains valid YAML, and does not include removed gateway/resilience settings. Documentation describes `api_mode` as provider-class selection and documents `model_names` for cockpit routing.

The canonical spec is updated to remove unsupported generic Google routing claims, describe mismatch rejection, and specify fallback consumption by the CLI runtime.

## CLI-Agent Verification

External CLI smoke/review runs are invoked through their documented headless commands, with one owner per process and explicit bounded timeouts. Each process is verified by exit status plus structured output where available.

- Claude: `claude -p` with `--tools Read`.
- Antigravity: `agy -p` with the prompt immediately after `-p` and `--dangerously-skip-permissions`.
- Codex: `codex exec` with `approval_policy=never`, `danger-full-access` when authorized, and stdin redirected from `/dev/null`.
- Goose: `goose run -t ... --no-session -q --max-turns N` with JSON status inspection.
- Kimi: `kimi -p` with defensive stream-JSON parsing; exact sentinel text is not a success criterion.
- OpenCode/Pi: use bounded runs; treat MCP discovery stalls, provider stalls, and inherited sessions as failures, terminate them, and preserve diagnostics.

Stale CLI processes and blocked terminal sessions are cleaned up before retrying; no user application process is terminated.
