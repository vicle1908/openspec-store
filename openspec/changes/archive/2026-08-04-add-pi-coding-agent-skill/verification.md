# Verification Evidence

Date: 2026-08-04

## Environment

- Pi CLI: `0.83.0`
- Binary: `/opt/homebrew/bin/pi`
- Installed packages: pi-subagents, pi-web-access, pi-intercom, pi-setup-custom-providers, pi-lens, pi-mcp-adapter, pi-gitnexus
- MCP: 77 direct tools resolved via pi-mcp-adapter (imports cursor + claude-code configs + mcp-router)
- Default provider: shoapikey (local config)
- Default model: fable-5 (local config)
- Hermes skill: `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` v1.0.0

## Skill Validation

- Frontmatter valid: name=pi, desc=58 chars, file=15,923 chars
- All required sections: Overview, When to Use, Common Pitfalls, Verification Checklist
- Related skills: claude-code, codex, antigravity, hermes-agent

## Smoke Probe — No Tools

Command: `timeout 30 pi -p --no-session --no-tools "Reply with exactly: PI_VERIFY_OK"`
Result: `PI_VERIFY_OK` — exit 0

## Smoke Probe — MCP Web Search

Command: `timeout 90 pi -p --no-session "Use the brave_web_search MCP tool to search for 'Pi coding agent pi.dev features'."`
Result: 2 results returned with titles and URLs — exit 0

## Smoke Probe — MCP News Search

Command: `timeout 90 pi -p --no-session "Use the brave_news_search MCP tool to search for 'coding agent AI 2026'."`
Result: 3 results returned with titles, URLs, and publication dates — exit 0

## Smoke Probe — MCP GitNexus

Command: `timeout 90 pi -p --no-session "Use the list_repos MCP tool to list all GitNexus-indexed repositories."`
Result: 7 repos listed with node/edge/community counts — exit 0

## Smoke Probe — Core Read Tool

Command: `timeout 60 pi -p --no-session "Read the file .../README.md and tell me the title."`
Result: Correctly read file and returned title "# add-pi-coding-agent-skill" — exit 0

## Smoke Probe — Combined MCP + Core Tools

Command: `timeout 90 pi -p --no-session "Use list_repos MCP tool + brave_web_search to combine repo stats with a Go article."`
Result: Combined GitNexus repo table + web search results into a single summary — exit 0

## MCP Tool Naming

Pi resolves MCP tool names from the adapter. The format observed:
- Brave Search: `brave_web_search`, `brave_news_search`
- GitNexus: `list_repos`, `graph_stats` (via directTools mode)

Using `--tools <mcp-name>` did NOT work for MCP tools (Pi's --tools only filters built-in tools).
MCP tools are available by default when pi-mcp-adapter is installed and the model chooses to use them.

## OpenSpec Validation

- `openspec validate --strict add-pi-coding-agent-skill`: valid
- `openspec validate --strict --all`: 359 passed, 0 failed
- `openspec store doctor`: no issues
- Store committed: `0c6c5ae`

## Known Limitations

- `--tools` flag only filters Pi core/built-in tools, not MCP tools. MCP tools are available when enabled by the adapter.
- Pi v0.83.0 has no native `--max-turns`. Bounded by host timeout.
- Extension-provided flags depend on local packages.
