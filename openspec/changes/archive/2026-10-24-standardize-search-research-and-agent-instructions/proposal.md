# Proposal

## Why

Workstation search, extraction, and browser automation suffer from a broken Hermes web backend (`web.backend: firecrawl` failing on every call because `firecrawl-py` is absent from Hermes `.venv`), plaintext credential literals in `~/.hermes/skills/research/web-search-clis/SKILL.md` plus duplicate shared keys in `~/.hermes/.env`, and outdated agent instructions (`~/Developer/AGENTS.md`, `~/Developer/.claude/CLAUDE.md`, `web-search-clis/SKILL.md`) that omit `browser-use`, reference nonexistent paths/commands (`~/.local/bin/exa`, `brightdata pipelines list`), misstate MCP fallbacks (`ctx7`, `deepwiki`), and leave conflicting "use me for all searches" mandates unresolved across skills. Standardizing Hermes's web backend on `tavily`, sanitizing secret leaks/duplicates, and aligning all agent instructions around the 7-CLI roster and a deterministic tiered precedence rule makes search, research, and browser selection reliable and cost-safe across all coding agents.

## What Changes

- **Hermes Native `tavily` Web Search & Extract Backend (`~/.hermes/config.yaml`)**: Switch `web.backend` and `web.extract_backend` in `/Users/androidteam/.hermes/config.yaml` (`0600`) from `firecrawl` to `tavily` (retaining `web.use_gateway: false`), eliminating the `venv: not installed and lazy installs are disabled: ['firecrawl']` error on every Hermes `web_search` and `web_extract` call by using `TavilyWebSearchProvider` over core `httpx` and `TAVILY_API_KEY` from `~/.zshenv`.
- **Credential Hygiene & Skill Secret Sanitization (`~/.hermes/.env` & `web-search-clis/SKILL.md`)**:
  - Remove duplicate shared-tier keys `FIRECRAWL_API_KEY` and `EXA_API_KEY` from `/Users/androidteam/.hermes/.env` (`0600`) so `/Users/androidteam/.zshenv` (`# BEGIN shared-agent-secrets`) is the sole authority, preserving service-private `BROWSERBASE_*`, `WEB_TOOLS_DEBUG`, and `VISION_TOOLS_DEBUG` entries.
  - Scrub hardcoded API key literals on lines 26 (`BRAVE_SEARCH_API_KEY`) and 49 (`EXA_API_KEY`) of `/Users/androidteam/.hermes/skills/research/web-search-clis/SKILL.md`, replacing them with value-blind `~/.zshenv` references.
- **7-CLI Roster, Path/Command Fixes & MCP Fallback Alignment (`~/Developer/AGENTS.md`, `~/Developer/.claude/CLAUDE.md`, `web-search-clis/SKILL.md`)**:
  - Upgrade the workstation CLI roster from 6 to **7 CLI tools** (`bx`, `tvly`, `exa`, `brightdata`, `ctx7`, `deepwiki`, `browser-use`).
  - Correct `exa` binary path from `~/.local/bin/exa` to `~/.npm-global/bin/exa` and replace removed `brightdata pipelines list` (`@brightdata/cli@0.4.0`) with `brightdata pipelines search <query>`.
  - Replace `# Browser automation (brightdata only)` / `Only brightdata has this` with `browser-use` (`~/.local/bin/browser-use` + Cloud V4 `start_remote_daemon` / `stop_remote_daemon`) as primary interactive browser automation and `brightdata browser` as bot-bypass scraping browser fallback.
  - Add `browser-use` (`BROWSER_USE_API_KEY` in `~/.zshenv`) and `ctx7` (`~/.config/context7/credentials.json` OAuth) to the Auth Keys documentation, and update the MCP Fallback tables to document active `context7` (`resolve_library_id`, `query_docs`), `docfork` (`docfork_search_docs`, `docfork_read_url`), `deepwiki` (`read_wiki_structure`, `read_wiki_contents`, `ask_wiki_question`), `grep-mcp` (`searchgithub`), and `brightdata` MCP servers.
- **Tiered Search, Docs & Browser Precedence Contract (`~/Developer/AGENTS.md` & `~/Developer/.claude/CLAUDE.md`)**: Establish an explicit 6-tier precedence order (`ctx7`/`docfork` for library docs -> `deepwiki` for public GitHub repo architecture -> `bx web`/`news`/`images`/`videos` for fast search, never bare `bx` -> `tvly`/`exa` for page extraction, crawling, and deep research -> `browser-use` for interactive CDP/Cloud browser & QA -> `brightdata` reserved for bot-protected scraping & structured platform feeds) that supersedes conflicting "replaces all web tools" claims in third-party skill files.
- **User-Home `/Users/androidteam/AGENTS.md` & `/Users/androidteam/.claude/CLAUDE.md` Alignment**: Fix the non-existent `~/.Codex/skills/graphify/SKILL.md` path in `/Users/androidteam/AGENTS.md` (`L3`) to canonical `~/.agents/skills/graphify/SKILL.md` while preserving its `package.json` npm dependency rule (`L1`), and add that same `package.json` npm dependency rule to `/Users/androidteam/.claude/CLAUDE.md` (`L1`) so both user-home instruction files carry identical top-level directives.

### Non-Goals

- **No Local Edits to Third-Party Managed Skills in `~/Developer/.agents/skills/`**: Upstream skills installed via `/opt/homebrew/bin/skills` (`bright-data-mcp`, `bx`, `tavily-*`, `browser-use`, `cloud`, `open-source`, `qa`) must remain byte-identical to their upstream lockfile snapshots so `sync-workspace-agent-skills.py --check` (`snapshot_check=ok`) and `/opt/homebrew/bin/skills update` continue passing without hash drift; precedence is governed in `~/Developer/AGENTS.md` and `~/Developer/.claude/CLAUDE.md`.
- **No Changes to Claude Code, Codex, or OMP Hook Scripts**: Existing AgentMemory, Orca, and Herdr lifecycle hooks across `~/.claude/settings.json`, `~/.codex/hooks.json`, and `~/.omp/agent/extensions/` are verified healthy and remain untouched.
- **No Installation of `firecrawl-py` into Hermes `.venv`**: Hermes `pyproject.toml` intentionally excludes vendor-specific SDKs (`firecrawl-py`, `exa-py`) from core dependencies to minimize supply-chain surface; switching `web.backend` and `web.extract_backend` to `tavily` uses core `httpx` natively.

## Capabilities

### New Capabilities
- `workstation-search-and-research-tooling`: Governs Hermes `tavily` web search/extract backend configuration, `~/.zshenv` vs. `~/.hermes/.env` search credential deduplication and `web-search-clis/SKILL.md` secret sanitization, the 7-CLI research/browser documentation and MCP fallback contract in `~/Developer/AGENTS.md` and `~/Developer/.claude/CLAUDE.md`, and the tiered search/research/browser precedence rules.

### Modified Capabilities
<!-- None: existing specs remain canonically preserved without mutating existing requirement blocks. -->

## Impact

- **Planning & Governance Store (`~/Developer/platform/openspec-store` — central store root)**:
  - `openspec/changes/standardize-search-research-and-agent-instructions/*`
- **External Workstation & Workspace Surfaces (require operator-authorized apply phase)**:
  - `/Users/androidteam/.hermes/config.yaml` (`0600`, `web.backend: tavily`, `web.extract_backend: tavily`)
  - `/Users/androidteam/.hermes/.env` (`0600`, remove duplicate `FIRECRAWL_API_KEY` and `EXA_API_KEY`)
  - `/Users/androidteam/.hermes/skills/research/web-search-clis/SKILL.md` (scrub hardcoded keys on lines 26 & 49, fix `exa` path and `brightdata pipelines search`, add `browser-use` 7th CLI and MCP fallbacks)
  - `/Users/androidteam/Developer/AGENTS.md` & `/Users/androidteam/Developer/.claude/CLAUDE.md` (7-CLI table, `browser-use` quickstart, `~/.npm-global/bin/exa`, `brightdata pipelines search`, MCP fallback table, tiered tool precedence contract)
  - `/Users/androidteam/AGENTS.md` & `/Users/androidteam/.claude/CLAUDE.md` (align user-home `package.json` npm rule and canonical `~/.agents/skills/graphify/SKILL.md` path)
