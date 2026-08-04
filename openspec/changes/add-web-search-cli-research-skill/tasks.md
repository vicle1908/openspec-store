# Tasks: Web Search CLI Research Skill

## P1: Skill Creation

### 1. Create SKILL.md with frontmatter and overview ✅
- Written to `~/.hermes/skills/research/web-search-clis/SKILL.md`
- Frontmatter: name, description (≤60 chars, trigger first), version, author, license, metadata
- **Verification:** File starts with `---`, valid YAML frontmatter ✓

### 2. Write tool profiles section ✅
- Documented bx, tvly, exa with exact binary paths, auth setup, version info
- Included env variable setup commands for each tool
- **Verification:** Each tool has: binary path, auth command, version, free-tier scope ✓

### 3. Write command reference sections ✅
- bx: `web`, `news`, `images`, `videos` with exact flags
- tvly: `search`, `extract`, `crawl`, `map`, `research` with exact flags
- exa: `search`, `answer`, `contents`, `find-similar` with exact flags
- Included working examples for each command
- **Verification:** Every command has at least one runnable example ✓

### 4. Write decision matrix and pitfalls ✅
- 13-row task-to-tool decision matrix
- MCP equivalents table (11 CLI→MCP mappings)
- 7 common pitfalls documented
- **Verification:** Decision matrix covers 13 task types ✓

## P2: Verification

### 5. Validate skill format ✅
- `skill_view(name='web-search-clis')` returns full content
- Description fits 60-char system prompt budget
- **Verification:** All validation checks pass ✓

### 6. Verify all CLI commands still work ✅
- `bx web "test" --count 1` → results returned (exit 0) ✓
- `tvly search "test" --max-results 1` → results returned (exit 0) ✓
- `exa search "test" --num-results 1 --plain` → results returned (exit 0) ✓
- **Verification:** All three return results ✓
