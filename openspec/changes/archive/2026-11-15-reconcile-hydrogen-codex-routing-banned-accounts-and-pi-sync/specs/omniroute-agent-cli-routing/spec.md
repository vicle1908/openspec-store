# Spec Delta

## MODIFIED Requirements

### Requirement: Codex Catalog Tier Clamping and Fleet Fallback Selector Retention
Codex CLI (`~/.codex/{config.toml,omniroute.config.toml,cockpit-model-catalog.json}`) SHALL default to `gemini-4-hydrogen` at `"high"` reasoning effort, omit unsupported `service_tier` values such as `"ultrafast"` per `openai/codex` config schema, clamp tiered Hydrogen slugs to their matching effort level, and retain `gemini-3.8-flash-high` in its catalog, while protocol-level `/v1/responses` inference against `quota-weighted` `gemini-4-hydrogen` SHALL return `HTTP 200` / `"pong"` (with zero `unsupported_service_tier_warning` diagnostics when `codex exec` runs).

#### Scenario: Selecting a tiered Codex Hydrogen slug respects its tier instead of global xhigh override
- **WHEN** `~/.codex/cockpit-model-catalog.json` (`mode 0644`, `ensure_ascii=False`), `~/.codex/omniroute.config.toml` (`mode 0600`), and `~/.codex/config.toml` (`mode 0600`) are inspected
- **THEN** `~/.codex/config.toml` and `~/.codex/omniroute.config.toml` SHALL both set `model = "gemini-4-hydrogen"` and `model_reasoning_effort = "high"`, and `~/.codex/config.toml` SHALL omit `service_tier = "ultrafast"` so Codex emits zero `unsupported_service_tier_warning` diagnostics
- **AND** `cockpit-model-catalog.json` SHALL set `default_reasoning_level: "high"` on `gemini-4-hydrogen` and object-array `supported_reasoning_levels` entries (`[{"effort": "xhigh", "description": "Extra high"}]` on `gemini-4-hydrogen-xhigh`, `[{"effort": "high", "description": "High"}]` on `gemini-4-hydrogen-high`, `[{"effort": "medium", "description": "Medium"}]` on `gemini-4-hydrogen-medium`, and `[{"effort": "low", "description": "Low"}]` on `gemini-4-hydrogen-low`, each matching `default_reasoning_level`)
- **AND** `"gemini-3.8-flash-high"` SHALL remain present in `cockpit-model-catalog.json` (`models[]`) as fallback

#### Scenario: Isolated Codex CLI probe succeeds against quota-weighted gemini-4-hydrogen /v1/responses
- **WHEN** `codex exec --skip-git-repo-check --ephemeral -c mcp_servers.mcp_router.enabled=false -c features.memories=false -c features.hooks=false "reply only: pong"` initializes against `~/.codex/config.toml` and protocol-level `POST http://127.0.0.1:20128/v1/responses` probes target `gemini-4-hydrogen` (without Google Antigravity's competing-identity content refusal phrase `You are Codex, an agent based on GPT-5.`)
- **THEN** `codex exec` SHALL emit zero `unsupported_service_tier_warning` diagnostics, and `POST /v1/responses` SHALL return `HTTP 200` with `"pong"` and `status: 200` `response.completed` traces in OmniRoute `call_logs`
