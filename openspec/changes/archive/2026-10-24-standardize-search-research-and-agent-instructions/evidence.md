# Verification Evidence: `standardize-search-research-and-agent-instructions`

## 1. Tasks 1.1 & 1.2: Hermes Web Search & Extract Backend (`tavily`) and `.env` Credential Deduplication

- **`/Users/androidteam/.hermes/config.yaml`**:
  - Mode: `0600` (`stat -L -f '%04Lp'`)
  - SHA-256: `ddc8060928afe79636e70487b4df063a5cd48064410265edd73e536e75d55810`
  - Configured: `web.backend: tavily`, `web.extract_backend: tavily`, `web.use_gateway: false`
- **`/Users/androidteam/.hermes/.env`**:
  - Mode: `0600` (`stat -L -f '%04Lp'`)
  - SHA-256: `fc9777cef50e918a9ef436647a9cf9ab83a3e67dddbd6547098226347890d537`
  - Value-Blind Audit:
    - `env_key_absent_FIRECRAWL_API_KEY`: `True`
    - `env_key_absent_EXA_API_KEY`: `True`
    - `env_key_absent_TAVILY_API_KEY`: `True`
    - `env_key_absent_BRAVE_SEARCH_API_KEY`: `True`
    - `env_key_absent_BROWSER_USE_API_KEY`: `True`
    - `env_key_present_BROWSERBASE_API_KEY`: `True`
    - `env_key_present_WEB_TOOLS_DEBUG`: `True`
    - `env_key_present_VISION_TOOLS_DEBUG`: `True`
- **Live Hermes `web_search_tool` & `web_extract_tool` Execution (`/Users/androidteam/.hermes/hermes-agent/.venv/bin/python`)**:
  - `wt._get_search_backend() == "tavily"` → `True`
  - `wt._get_extract_backend() == "tavily"` → `True`
  - `json.loads(wt.web_search_tool("example domain", limit=1))`:
    - `search_tool_success`: `True`
    - `search_tool_rescued_absent` (`"rescued_from" not in data`): `True`
    - `search_tool_web_results_count`: `1`
  - `json.loads(asyncio.run(wt.web_extract_tool(["https://example.com"])))`:
    - `extract_tool_results_count`: `1`
    - `extract_tool_has_content`: `True`
    - `extract_tool_error_is_none`: `True`

## 2. Tasks 2.1 & 2.2: Sanitize & Upgrade `~/.hermes/skills/research/web-search-clis/SKILL.md`

- **File Updated**: `/Users/androidteam/.hermes/skills/research/web-search-clis/SKILL.md`
  - Mode: `0600`
  - Lines: `695`
  - SHA-256: `748e04e6e7dd809a34a6a9eeb6604def15bd9925840059e25a856650406f9cd1`
- **Secret & Drift Regex Audit**:
  - UUID patterns: `0` found
  - Hardcoded API key assignments (`(?:API_KEY|api-key)\s*[=:]\s*["']?[^"'\s#]+`): `0` found
  - Stale paths/commands (`~/.local/bin/exa`, `/opt/homebrew/bin ctx7`, `brightdata pipelines list`, `tvly auth`, `bx --status`): `0` found
  - Upgraded to 7 CLI tools (`bx`, `tvly`, `exa`, `brightdata`, `ctx7`, `deepwiki`, `browser-use`) across Frontmatter, Prerequisites, Decision Matrix, Parallel Search, Decision Tree, Cost/Quality/Speed, Command Reference, MCP Equivalents (`context7`, `docfork`, `deepwiki`, `grep-mcp`, `brightdata`, `chrome-devtools`), Cost Tracking, Pitfalls, and Verification.

## 3. Tasks 3.1, 3.2 & 3.3: Align `~/Developer/AGENTS.md`, `~/Developer/.claude/CLAUDE.md`, `~/AGENTS.md`, and `~/.claude/CLAUDE.md`

- **Updated Instruction Files & SHA-256 Digests**:
  - `/Users/androidteam/Developer/AGENTS.md`: `d35ef1ac2ea8b9bebb3312f9a7e9263eb559effaf9ef3dad62a50ed8b325f81c` (7-CLI roster, 6-tier precedence rule, `~/.npm-global/bin/exa`, `brightdata pipelines search`, `browser-use` primary + `brightdata browser` fallback, `BROWSER_USE_API_KEY` + `ctx7` auth entries, expanded MCP Fallbacks).
  - `/Users/androidteam/Developer/.claude/CLAUDE.md`: `0d226f85ded899948793ff53f55385879a7dfadd377218cdaf8f6aa4105f250e` (added `deepwiki`, `browser-use`, `brightdata`, 6-tier precedence note, `Context7 / Docfork`, `Chrome DevTools`, preserved `@../AGENTS.md` on `L159`).
  - `/Users/androidteam/AGENTS.md`: `8487c2b03341ac41729f4494bb2e36667bb8fbef0b48b80dde88ccf175ca53b7` (`~/.agents/skills/graphify/SKILL.md` + preserved `package.json` npm CLI rule).
  - `/Users/androidteam/.claude/CLAUDE.md`: `1c10ff7dad2c8007b643b888cf9d9403b4a90e765cf8e2c6cd1421cb3e44ce47` (aligned `package.json` npm CLI rule + `# graphify`).
- **Upstream Skills Snapshot Verification**:
  ```text
  canonical_direct_roots=115 containers=2 codex_selected=70 claude_selected=29 hermes_selected=10 openspec_targets=12 claude_commands=12 check=True
  malformed_entries=0
  snapshot_check=ok
  # Exit code: 0
  ```

## 4. End-to-End 7-CLI & Hermes Web Tools Smoke Suite

```text
E2E CLI [bx web                     ]: PASS (exit 0, len=8470)
E2E CLI [tvly --status              ]: PASS (exit 0, len=54)
E2E CLI [tvly search                ]: PASS (exit 0, len=455)
E2E CLI [exa search                 ]: PASS (exit 0, len=60)
E2E CLI [brightdata zones           ]: PASS (exit 0, len=162)
E2E CLI [brightdata pipelines search]: PASS (exit 0, len=875)
E2E CLI [ctx7 whoami                ]: PASS (exit 0, len=10)
E2E CLI [ctx7 library               ]: PASS (exit 0, len=1643)
E2E CLI [deepwiki toc               ]: PASS (exit 0, len=1935)
E2E CLI [browser-use --version      ]: PASS (exit 0, len=7)
E2E CLI [browser-use auth status    ]: PASS (exit 0, len=117)
E2E Hermes [web_search_tool + web_extract_tool (tavily)]: PASS
```
