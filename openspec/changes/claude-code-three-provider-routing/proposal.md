# Proposal: claude-code-three-provider-routing

## Why

Claude Code v2.1.226 runs with a single provider (shopapikey) hardcoded in `settings.json`. The user wants shell launcher functions to switch between three providers — shopapikey, giaoduc, and cockpit — without modifying settings.json per session.

## Provider Ground Truth

### Provider compatibility findings

| Provider | Base URL | Configured `api_mode` | Observed wire behavior | Model | Adapter |
|---|---|---|---|---|---|
| shopapikey | `https://api.phanmemvip.shop` | `codex_responses` | Accepts Anthropic Messages at `/v1/messages` | `fable-5` | None |
| giaoduc | `https://api.giaoduc.online` | `anthropic_messages` | Serves Anthropic Messages natively at `/v1/messages` | `Advance` | None |
| cockpit | `http://localhost:51006/v1` | `codex_responses` | Serves OpenAI Responses at `/v1/responses` | `gpt-5.6-luna` | Workspace repo |

Claude Code is an Anthropic Messages client. It sends requests to `/v1/messages` with the `anthropic-version: 2023-06-01` header. Both shopapikey and giaoduc accept this format. cockpit serves OpenAI Responses and requires a translation adapter.

### Workspace adapter repository

The cockpit adapter lives at `~/Developer/claude-code-provider-adapter/` as a proper Python workspace repository:

- `uv` for dependency management (pyproject.toml + uv.lock)
- `src/` layout with `claude_code_provider_adapter` package
- Python `>=3.14,<3.15` (matching workspace convention)
- Latest stable dependencies resolved via `uv lock`
- Runtime entry point: `uv run claude-code-provider-adapter`

## Verified Evidence Matrix

| Evidence Gate | giaoduc | shopapikey | cockpit |
|---|---|---|---|
| `POST /v1/messages` text | **PASS** | **PASS** | N/A |
| `POST /v1/messages` streaming | **PASS** | **PASS** | N/A |
| `POST /v1/messages` tool_use | **PASS** | **PASS** | N/A |
| `POST /v1/responses` text | N/A | N/A | **PASS** |
| `POST /v1/responses` streaming | N/A | N/A | **PASS** |
| `POST /v1/responses` tool_use | N/A | N/A | **PASS** (body not inspected) |
| Adapter needed | No | No | Yes (Claude Code is Messages-only) |

## What Changes

### Phase 1: Provider Profile Launchers

Shell functions in `~/.zshrc`. No embedded secrets — env-var names only.

- `shopapikey()` — `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop`, model `fable-5`
- `giaoduc()` — `ANTHROPIC_BASE_URL=https://api.giaoduc.online`, model `Advance`
- `cockpit()` — `ANTHROPIC_BASE_URL=http://localhost:8787`, model `gpt-5.6-luna` (starts adapter)
- `claude_reset()` — Unset all provider env vars, launch default

### Phase 2: Settings Isolation

Back up `~/.claude/settings.json`. Remove provider-specific env vars. Preserve all unrelated settings.

### Phase 3: Workspace Adapter Repository

Create `~/Developer/claude-code-provider-adapter/` with `uv`, `pyproject.toml`, `src/` layout. Implement Anthropic Messages → OpenAI Responses translation. See design.md for architecture and translation contracts.

### Phase 4: Final Acceptance

Bounded `claude --print` smoke tests through each launcher against isolated settings.

## Security

- Credentials referenced by env-var names only; never embedded in source
- Adapter does not log request/response bodies
- No credential values in OpenSpec artifacts
- Existing credentials retained; rotation intentionally out of scope

## Risks

- **Medium**: Adapter correctness — streaming and tool_use mapping must be precise
- **Low**: giaoduc and shopapikey launchers are env-var configuration

## Rollback

Remove shell functions from `~/.zshrc`. Restore `settings.json` from backup. Stop adapter process if running.
