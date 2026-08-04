# Tasks: Web Search CLI Research Skill

## P1: Skill Creation

### 1. Create SKILL.md with frontmatter and overview
- Write `~/.hermes/skills/research/web-search-clis/SKILL.md`
- Frontmatter: name, description (≤1024 chars, trigger in first 57), version, author, license, metadata
- Overview: what the skill covers and why
- **Verification:** File starts with `---`, has valid YAML frontmatter, description starts with "Use when"

### 2. Write tool profiles section
- Document bx, tvly, exa with exact binary paths, auth setup, version info
- Include env variable setup commands for each tool
- **Verification:** Each tool has: binary path, auth command, version, free-tier scope

### 3. Write command reference sections
- bx: `web`, `news`, `images`, `videos` with exact flags
- tvly: `search`, `extract`, `crawl`, `map`, `research` with exact flags
- exa: `search`, `answer`, `contents`, `find-similar` with exact flags
- Include working examples for each command
- **Verification:** Every command has at least one runnable example

### 4. Write decision matrix and pitfalls
- Task-to-tool decision matrix table
- MCP equivalents table for fallback
- Common pitfalls: rate limits, wrong plan tier, missing API keys, burst 429s
- **Verification:** Decision matrix covers 10+ task types

## P2: Verification

### 5. Validate skill format
- Check frontmatter parsing: `python3 -c "import yaml; ..."`
- Check description ≤ 1024 chars
- Check total file ≤ 100,000 chars
- **Verification:** All validation checks pass

### 6. Verify all CLI commands still work
- Run one command per tool to confirm API keys are valid
- `BRAVE_SEARCH_API_KEY=... bx web "test" --count 1`
- `tvly search "test" --max-results 1`
- `EXA_API_KEY=... exa search "test" --num-results 1 --plain`
- **Verification:** All three return results (exit 0)
