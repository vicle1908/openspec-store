# Spec Delta: omniroute-agent-cli-routing

## MODIFIED Requirements

### Requirement: Muse Code CLI SHALL route default inference through OmniRoute combo `muse-spark-1.3` with sanctioned bearer transport pinning
Meta Muse Code (`muse`) SHALL target local OmniRoute (`http://127.0.0.1:20128/v1`) using explicit `endpoint_transport` bearer pinning (`"auth": "bearer"`) and default model `"muse-spark-1.3"`, while OmniRoute SHALL define a combo named `muse-spark-1.3` backed by the `gemini-3.8-flash-high` pool so `POST /v1/responses` requests are intercepted ahead of the unauthenticated static `muse-code` provider.

#### Scenario: Sanctioned front-door bearer transport prevents CLI auth withholding
- **WHEN** `~/.config/muse/settings.json` is loaded by Muse Code CLI (`v1.0.1+`)
- **THEN** `schema_version` SHALL equal `1`
- **AND** `endpoint_transport.base_url` SHALL equal `"http://127.0.0.1:20128/v1"` with `endpoint_transport.auth` set to `"bearer"`
- **AND** `provider` SHALL equal `"meta"` with `model` set to `"muse-spark-1.3"`
- **AND** Muse Code SHALL transmit the `Authorization: Bearer <OMNIROUTE_API_KEY>` header to `127.0.0.1:20128` without triggering front-door bearer withholding

#### Scenario: OmniRoute combo `muse-spark-1.3` intercepts bare model requests and preserves namespace tools
- **WHEN** Muse Code sends a streaming `POST /v1/responses` request with `"model": "muse-spark-1.3"` and `"type": "namespace"` tool definitions (such as `namespace: "muse"`)
- **THEN** OmniRoute's combo resolver SHALL match the `muse-spark-1.3` combo (`context_length: 1000000`, `context_cache_protection: false`) before static provider lookup and route inference to the `gemini-3.8-flash-high` Antigravity pool (with `agy/gemini-3.8-flash-medium` fallback)
- **AND** OmniRoute SHALL flatten incoming `namespace` tool groups for upstream execution and restore `{"namespace": "muse", "name": "<tool>"}` on returned `function_call` SSE items
- **AND** `GET /v1/muse-code/models` SHALL return HTTP 200 advertising `muse-spark-1.3`

#### Scenario: Unpinned `--base-url` override or missing combo fails closed
- **WHEN** a custom `--base-url` is invoked without matching `endpoint_transport` bearer configuration or when `OMNIROUTE_API_KEY` is absent from `~/.config/muse/auth.json`
- **THEN** the request SHALL be rejected with an explicit authentication error (`401`) or front-door withholding warning rather than falling back to unauthenticated external endpoints

#### Scenario: Pre-flight Responses keepalive and catalog compatibility with Rust SSE decoder
- **WHEN** `muse exec --disable-approval --no-session-log` executes prompt and tool-calling turns against `http://127.0.0.1:20128/v1`
- **THEN** the SSE stream and `/v1/muse-code/models` payload delivered to Muse Code SHALL NOT cause a Rust `serde` deserialization failure on synthetic `response.in_progress` frames or catalog metadata
