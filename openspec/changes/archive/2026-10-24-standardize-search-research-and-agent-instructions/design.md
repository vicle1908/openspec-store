# Design

## Context

See `proposal.md` — Why, and `specs/workstation-search-and-research-tooling/spec.md` for normative requirements.

Read-only runtime probes across `/Users/androidteam/Developer`, `/Users/androidteam/.hermes`, and `mcprouter.db` established the following facts:
1. **Hermes `web:` Backend Failure**: `/Users/androidteam/.hermes/config.yaml:252-255` currently pins `web.backend: firecrawl` and `web.extract_backend: firecrawl`. Because `/Users/androidteam/.hermes/hermes-agent/pyproject.toml:34-39` keeps `firecrawl-py` out of core dependencies and lazy installs are disabled inside `/Users/androidteam/.hermes/hermes-agent/.venv`, every `web_search_tool` call fails with `venv: not installed and lazy installs are disabled: ['firecrawl']` and triggers a degraded one-shot keyless rescue. By contrast, `TavilyWebSearchProvider` (`plugins/web/tavily/provider.py`) uses core `httpx==0.28.1` and `TAVILY_API_KEY` from `~/.zshenv`, passing both `search()` and `extract()` in-process with zero extra packages.
2. **Credential & Skill Hygiene Gaps**:
   - `/Users/androidteam/.hermes/.env` (`0600`, 34 keys) duplicates `FIRECRAWL_API_KEY` (`L531`) and `EXA_API_KEY` (`L532`) from `/Users/androidteam/.zshenv` (`# BEGIN shared-agent-secrets`). Because Hermes's dotenv loader uses `override=True`, keeping shared keys in `~/.hermes/.env` risks silent drift when `~/.zshenv` is rotated.
   - `/Users/androidteam/.hermes/skills/research/web-search-clis/SKILL.md` lines 26 and 49 contain hardcoded API keys for `BRAVE_SEARCH_API_KEY` and `EXA_API_KEY` and cite `~/.zshrc` (`L25, L599`), `~/.tavily/config.json` (`L38, L599`), and Zed config (`L48, L599`) instead of `~/.zshenv`.
3. **Instruction & Command Drift**:
   - `~/Developer/AGENTS.md:270-360` and `web-search-clis/SKILL.md` list only 6 CLIs (omitting `browser-use`), give the wrong binary path for `exa` (`~/.local/bin/exa` instead of `~/.npm-global/bin/exa`) and a space typo on `web-search-clis/SKILL.md:71` (`/opt/homebrew/bin ctx7`), use the removed `@brightdata/cli@0.4.0` command `brightdata pipelines list` (replaced by `brightdata pipelines search <query>`), label browser automation as `brightdata only`, and state that `ctx7` and `deepwiki` have no MCP fallbacks despite active `context7`, `docfork`, `deepwiki`, `grep-mcp`, and `brightdata` servers in `mcprouter.db`.
   - `/Users/androidteam/AGENTS.md` (307 bytes) references a non-existent `~/.Codex/skills/graphify/SKILL.md` path (`L3`) instead of `~/.agents/skills/graphify/SKILL.md`, while `/Users/androidteam/.claude/CLAUDE.md` (228 bytes) omits the `package.json` npm dependency rule present on line 1 of `/Users/androidteam/AGENTS.md`. Note that `@../AGENTS.md` on line 153 of `/Users/androidteam/Developer/.claude/CLAUDE.md` resolves relative to `/Users/androidteam/Developer/.claude/` (targeting `/Users/androidteam/Developer/AGENTS.md`) and must be preserved.

## Goals / Non-Goals

**Goals:**
- Make Hermes's built-in `web_search` and `web_extract` tools succeed on the first attempt without missing-package errors or rescue fallbacks.
- Eliminate duplicate shared keys in `~/.hermes/.env` and scrub hardcoded API key literals from `~/.hermes/skills/research/web-search-clis/SKILL.md`.
- Align `~/Developer/AGENTS.md`, `~/Developer/.claude/CLAUDE.md`, `/Users/androidteam/AGENTS.md`, and `web-search-clis/SKILL.md` around the 7-CLI roster (`bx`, `tvly`, `exa`, `brightdata`, `ctx7`, `deepwiki`, `browser-use`), accurate paths/commands, active MCP fallbacks, and a 6-tier tool selection precedence contract.

**Non-Goals:**
- Modifying any upstream skill file in `~/Developer/.agents/skills/` (which would break `sync-workspace-agent-skills.py --check` snapshot integrity).
- Modifying Claude Code, Codex, or OMP hook scripts (`~/.claude/settings.json`, `~/.codex/hooks.json`, `~/.omp/agent/extensions/`).

## Decisions

### Decision 1: Switch Hermes `web.backend` and `web.extract_backend` to `tavily`

```
+-----------------------------------------------------------------------------------+
|               HERMES WEB SEARCH & EXTRACT PROVIDER RESOLUTION                     |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  ~/.zshenv (0600, # BEGIN shared-agent-secrets)                                   |
|  export TAVILY_API_KEY='...'                                                      |
|         |                                                                         |
|         v                                                                         |
|  ~/.hermes/config.yaml (0600)                                                     |
|  web:                                                                             |
|    backend: tavily                                                                |
|    extract_backend: tavily                                                        |
|    use_gateway: false                                                             |
|         |                                                                         |
|         v                                                                         |
|  plugins/web/tavily/provider.py (TavilyWebSearchProvider over core httpx==0.28.1) |
|  - web_search_tool(...)               --> POST https://api.tavily.com/search  (200 OK) |
|  - asyncio.run(web_extract_tool(...)) --> POST https://api.tavily.com/extract (200 OK) |
+-----------------------------------------------------------------------------------+
```

- **Choice**: Configure `web.backend: tavily` and `web.extract_backend: tavily` (`use_gateway: false`) in `/Users/androidteam/.hermes/config.yaml`.
- **Rationale**: `TavilyWebSearchProvider` uses `httpx` (a pinned core dependency in `~/.hermes/hermes-agent/pyproject.toml:51`), supports both `search` and `extract` (`EXTRACT = True`), and reads `TAVILY_API_KEY` from `~/.zshenv`.
- **Alternatives Considered**:
  - *Install `firecrawl-py` into `~/.hermes/hermes-agent/.venv`*: Rejected because Hermes `pyproject.toml:20-39` enforces strict minimal core dependencies and overwrites manual venv additions during `hermes` updates.
  - *Use `brave-free` as `web.backend`*: Rejected because `brave-free` does not implement `extract` (`is_extract_available=None`) and has a strict 1 req/s rate limit.

### Decision 2: Governs Tool Precedence in `~/Developer/AGENTS.md` & `CLAUDE.md` Without Editing `.agents/skills/`

- **Choice**: Document the 6-tier precedence rule directly in `/Users/androidteam/Developer/AGENTS.md` and `/Users/androidteam/Developer/.claude/CLAUDE.md` (plus `~/.hermes/skills/research/web-search-clis/SKILL.md`, which is a Hermes-local skill outside `~/Developer/.agents/skills/`), while leaving third-party skills in `~/Developer/.agents/skills/` (`bright-data-mcp`, `bx`, `tavily-*`) byte-identical.
- **Rationale**: Workspace root `AGENTS.md` and `.claude/CLAUDE.md` are loaded as top-level system/repo rules in every session and take authority over individual skill descriptions, while preserving `sync-workspace-agent-skills.py --check` (`snapshot_check=ok`) and idempotent `/opt/homebrew/bin/skills update`.

## Risks / Trade-offs

- **[Risk] Removing `FIRECRAWL_API_KEY` and `EXA_API_KEY` from `~/.hermes/.env` if a non-login daemon does not source `~/.zshenv`** → **Mitigation**: All zsh processes automatically source `~/.zshenv`, and `hermes_cli.config.get_env_value()` falls back to `os.getenv()` when a key is absent from `~/.hermes/.env` (`tools/web_tools.py:35-48`). Verify in-process that `wt._env_value("TAVILY_API_KEY")` and `wt._env_value("EXA_API_KEY")` resolve from `~/.zshenv` after deduplication.
- **[Risk] Bare `bx "query"` Invocations Failing with HTTP 422 (`OPTION_NOT_IN_PLAN`)** → **Mitigation**: Explicitly document in `~/Developer/AGENTS.md`, `~/Developer/.claude/CLAUDE.md`, and `web-search-clis/SKILL.md` that bare `bx "query"` invokes the paid `bx context` endpoint and agents must always pass the subcommand (`bx web "query"`, `bx news`, `bx images`, `bx videos`).
