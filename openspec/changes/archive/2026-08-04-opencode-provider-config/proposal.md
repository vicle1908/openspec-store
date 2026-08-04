# Proposal: OpenCode Provider Configuration Update

## Why

The current Anthropic provider routes through a local proxy (`127.0.0.1:8045/v1`), which adds unnecessary indirection and has been unreliable (proxy not always running). We need to:

1. Point Anthropic directly to `https://api.anthropic.com` for reliability
2. Add an OpenAI provider via localhost proxy for GPT-5.6 family models
3. Set the default model to `claude-fable-5` (the latest Anthropic model)

## What Changes

### Provider Updates
- **Anthropic**: `http://127.0.0.1:8045/v1` → `https://api.anthropic.com` with direct API key
- **OpenAI**: New provider added at `http://localhost:51006/v1` with 3 models
- **Google**: Kept as-is (local proxy still useful for fable-5 models)
- **Z.ai**: Kept as-is (direct API already configured)

### Model Updates
- Default model: `anthropic/fable-5-4-5` → `anthropic/claude-fable-5`
- Small model: kept as `anthropic/claude-sonnet-4-5`
- New OpenAI models available: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`

## Skip Specs

Config-only change — no spec delta required.
