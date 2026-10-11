# omniroute-agent-cli-routing Delta Specification

## ADDED Requirements

### Requirement: Gemini combo SHALL be configured as default across supported coding agents

Supported coding-agent CLIs (`pi`, `codex`, `opencode`, `grok`, `droid`, `prime-agent`, `goose`) SHALL configure the live `gemini-3.8-flash-high` combo as their active default model via OmniRoute using the OpenAI Responses API (`/v1/responses` or `api: openai-responses` / `wire_api: responses`) where supported by the client, or via OmniRoute's OpenAI-compatible ingress for strict Chat Completions clients. Pre-existing providers SHALL remain preserved.

#### Scenario: Supported CLIs default to Gemini combo

- **WHEN** coding agents are invoked with default model selection
- **THEN** requests SHALL route through OmniRoute's `gemini-3.8-flash-high` combo
- **AND** clients supporting the Responses API SHALL use `/v1/responses`
- **AND** all existing alternative providers SHALL remain preserved
- **AND** credentials SHALL resolve via environment indirection (`OMNIROUTE_API_KEY`) with zero literal secrets committed
