# workstation-search-and-research-tooling Specification

## Purpose

Defines the workstation-wide contract for Hermes Agent's built-in web search and extraction backend, single-source-of-truth search credential hygiene, the 7-CLI research and browser tool documentation (`bx`, `tvly`, `exa`, `brightdata`, `ctx7`, `deepwiki`, `browser-use`), MCP Router fallback mappings, and tiered tool selection precedence across `/Users/androidteam/Developer`.

## Requirements

### Requirement: Hermes Native Tavily Web Search and Extraction Backend

Hermes Agent (`/Users/androidteam/.hermes/config.yaml`) SHALL configure `web.backend: tavily` and `web.extract_backend: tavily` with `web.use_gateway: false` so built-in `web_search` and `web_extract` calls execute over core `httpx` using `TAVILY_API_KEY` from `~/.zshenv` without requiring uninstalled vendor SDKs in Hermes `.venv`.

#### Scenario: Hermes web_search and web_extract succeed via Tavily without rescue fallback
- **WHEN** `web_search_tool` or `asyncio.run(web_extract_tool(...))` is invoked in Hermes with `TAVILY_API_KEY` present in `~/.zshenv`
- **THEN** `_get_search_backend()` and `_get_extract_backend()` SHALL both return `"tavily"`
- **AND** both tools SHALL return valid JSON results directly via `TavilyWebSearchProvider` without emitting a `rescued_from` error

#### Scenario: Missing Tavily key fails closed with actionable setup message
- **WHEN** `TAVILY_API_KEY` is absent and keyless mode is not forced
- **THEN** `TavilyWebSearchProvider` SHALL return a structured failure stating `TAVILY_API_KEY is not set` without exposing secret values

### Requirement: Single-Source-of-Truth Search Credentials and Skill Secret Sanitization

Shared search credentials (`BRAVE_SEARCH_API_KEY`, `TAVILY_API_KEY`, `EXA_API_KEY`, `FIRECRAWL_API_KEY`, `BROWSER_USE_API_KEY`) SHALL reside exclusively in `/Users/androidteam/.zshenv` (`0600`) and MUST NOT be duplicated in `~/.hermes/.env` or embedded as plaintext literals in skill files.

#### Scenario: Duplicate shared search keys are absent from Hermes .env
- **WHEN** `/Users/androidteam/.hermes/.env` (`0600`) is audited using a value-blind check
- **THEN** `FIRECRAWL_API_KEY`, `EXA_API_KEY`, `TAVILY_API_KEY`, `BRAVE_SEARCH_API_KEY`, and `BROWSER_USE_API_KEY` SHALL be absent from `~/.hermes/.env`
- **AND** service-private `BROWSERBASE_*`, `WEB_TOOLS_DEBUG`, and `VISION_TOOLS_DEBUG` entries in `~/.hermes/.env` SHALL remain preserved

#### Scenario: Hermes web-search-clis skill contains zero hardcoded API keys
- **WHEN** `/Users/androidteam/.hermes/skills/research/web-search-clis/SKILL.md` is inspected
- **THEN** the file SHALL contain zero literal API keys or UUID tokens for `BRAVE_SEARCH_API_KEY` or `EXA_API_KEY`
- **AND** its prerequisites and pitfalls sections SHALL reference `~/.zshenv` (`# BEGIN shared-agent-secrets`) as the shared credential source

### Requirement: Seven-CLI Research and Browser Roster and Accurate Command Contracts

Workstation instruction files (`/Users/androidteam/Developer/AGENTS.md`, `/Users/androidteam/Developer/.claude/CLAUDE.md`, and `/Users/androidteam/.hermes/skills/research/web-search-clis/SKILL.md`) SHALL document all seven CLI tools (`bx`, `tvly`, `exa`, `brightdata`, `ctx7`, `deepwiki`, `browser-use`) with verified binary paths, current subcommands, and active MCP Router fallbacks.

#### Scenario: Binary paths and CLI subcommands match installed versions
- **WHEN** `~/Developer/AGENTS.md` and `~/.hermes/skills/research/web-search-clis/SKILL.md` document CLI paths and commands
- **THEN** `exa` SHALL be documented at `~/.npm-global/bin/exa`, `ctx7` at `/opt/homebrew/bin/ctx7`, and `browser-use` at `~/.local/bin/browser-use`
- **AND** Bright Data pipeline discovery SHALL use `brightdata pipelines search <query>` instead of the removed `brightdata pipelines list` command

#### Scenario: MCP fallback tables include Context7, Docfork, DeepWiki, and Bright Data
- **WHEN** the MCP fallback tables in `~/Developer/AGENTS.md` and `web-search-clis/SKILL.md` are inspected
- **THEN** they SHALL map `ctx7` to `mcp__mcp_router__resolve_library_id` / `query_docs` (plus `docfork`), `deepwiki` to `read_wiki_structure` / `read_wiki_contents` / `ask_wiki_question`, and `brightdata` to the `brightdata` MCP server

#### Scenario: User-home AGENTS.md and CLAUDE.md are aligned without stale skill paths
- **WHEN** `/Users/androidteam/AGENTS.md` and `/Users/androidteam/.claude/CLAUDE.md` are read on disk
- **THEN** both files SHALL include the user `package.json` npm dependency rule and `/graphify` trigger
- **AND** `/Users/androidteam/AGENTS.md` SHALL reference `~/.agents/skills/graphify/SKILL.md` instead of the non-existent `~/.Codex/skills/graphify/SKILL.md` path

### Requirement: Deterministic Tiered Search, Documentation, and Browser Precedence

`/Users/androidteam/Developer/AGENTS.md` and `/Users/androidteam/Developer/.claude/CLAUDE.md` SHALL define a six-tier tool selection precedence rule that supersedes conflicting exclusive mandates in third-party skill files while keeping upstream `.agents/skills/` files unmodified.

#### Scenario: Six-tier tool selection order resolves conflicting skill mandates
- **WHEN** an agent selects a search, documentation, extraction, or browser tool in `/Users/androidteam/Developer`
- **THEN** instructions SHALL mandate: (1) `ctx7`/`docfork` for library docs, (2) `deepwiki` for public repo wikis, (3) `bx web`/`news`/`images`/`videos` (never bare `bx`) for fast search, (4) `tvly`/`exa` for extraction, crawling, and deep research, (5) `browser-use` for interactive CDP/Cloud browser & QA, and (6) `brightdata` for bot-protected scraping and platform feeds

#### Scenario: Upstream skills under .agents/skills remain unmodified
- **WHEN** `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` is executed
- **THEN** upstream skills under `~/Developer/.agents/skills/` SHALL remain byte-identical to their lockfile snapshots
- **AND** the check script SHALL exit `0` with `snapshot_check=ok`
