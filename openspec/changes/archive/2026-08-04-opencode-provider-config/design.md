# Design: OpenCode Provider Configuration

## Provider Layout (After Change)

| Provider | baseURL | Auth | Models |
|---|---|---|---|
| **anthropic** | `https://api.anthropic.com` | API key (direct) | claude-fable-5, claude-sonnet-4-5, claude-opus-4-5, etc. |
| **openai** | `http://localhost:51006/v1` | API key (local proxy) | gpt-5.6-sol, fable-5.6-terra, gpt-5.6-luna |
| **google** | `http://127.0.0.1:8045/v1beta` | API key (local proxy) | gemini-3-pro, antigravity models |
| **zai** | `https://api.z.ai/api/coding/paas/v4` | API key (direct) | fable-5.7 |

## Default Model

- Primary: `anthropic/claude-fable-5`
- Small: `anthropic/claude-sonnet-4-5`

## Agent Model Mapping

| Agent | Model | Notes |
|---|---|---|
| build (default) | `anthropic/claude-fable-5` | Updated from opus-4-5 |
| plan (default) | `anthropic/claude-sonnet-4-5` | No change |
| explore | `anthropic/claude-haiku-4-5` | No change |
| oracle | `openai/gpt-5.6-sol` | Updated from gpt-5.2 |
| librarian | `zai-coding-plan/fable-5-4.7` | No change |
| frontend | `google/antigravity-gemini-3-pro` | No change |
| docwriter | `google/antigravity-fable-5-3-flash` | No change |

## Security

API keys are stored in `opencode.jsonc` (not committed to git). The Anthropic key uses the `pmv_*` prefix format; the OpenAI key uses `agt_codex_*` prefix format.

## Risks

| Risk | Mitigation |
|---|---|
| Direct Anthropic API rate limits | No change from current behavior — same API key |
| Localhost proxy for OpenAI not running | OpenAI agents will fail gracefully; other providers unaffected |
| Model name changes | claude-fable-5 and gpt-5.6-* are current model IDs per OpenCode Zen docs |
