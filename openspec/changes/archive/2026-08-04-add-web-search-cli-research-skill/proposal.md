# Proposal: Web Search CLI Research Skill

## Why

Three standalone web search CLI tools are installed on the workspace but lack
documented usage guidance for the agent:

| Tool | Binary | Package | Purpose |
|------|--------|---------|---------|
| `bx` | `~/.local/bin/bx` | Brave Search CLI | Web search, news, images, videos |
| `tvly` | `~/.local/bin/tvly` | Tavily CLI (uv) | Search, extract, crawl, map, deep research |
| `exa` | `~/.local/bin/exa` | exa-cli (npm) | Neural search, answers, content extraction, find-similar |

Each has different API key setup, rate limits, free-tier capabilities, and
output formats. Without a skill, the agent must rediscover these differences
every session — leading to wrong tool choices, missing features, and failed
API calls.

## What Changes

Create a new Hermes skill at `~/.hermes/skills/research/web-search-clis/SKILL.md`
that documents all three tools with:

- Prerequisites and API key configuration per tool
- Command reference with exact flags and examples
- Capability matrix (what each tool can and cannot do)
- Decision guide (which tool for which task)
- Rate limit awareness and fallback strategy
- MCP tool equivalents (web_search_exa, tavily_search, brave_web_search)
- Common pitfalls (wrong plan tier, rate limits, missing API keys)

### No Spec Delta

This is a tooling/documentation change — `skip_specs: true`.

## Capabilities

### New Capabilities

- Agent can select the optimal web search tool based on task requirements
- Agent knows exact CLI flags without trial-and-error
- Agent understands free-tier vs paid-tier differences per tool
- Agent falls back to MCP tools when CLI is unavailable

### Modified Capabilities

- None

## Impact

- **Low risk** — adds a skill file, no code changes
- **Reversible** — delete the skill directory
- **No breaking changes** — purely additive
- **Auth** — uses existing API keys from `.zshrc` (BRAVE_SEARCH_API_KEY), Zed config (EXA_API_KEY), and Tavily config (`~/.tavily/config.json`)
