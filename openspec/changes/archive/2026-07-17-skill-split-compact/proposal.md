# Proposal: Split Oversized SKILL.md Files

## Problem

6 skill files in `.agents/skills/` exceeded the 500-line Agent Skills spec recommendation for SKILL.md bodies:

| Skill | Lines | Excess |
|-------|-------|--------|
| kanban-board-from-spreadsheet | 1,446 | +946 |
| jira-integration | 743 | +243 |
| gitnexus-cli-usage | 736 | +236 |
| scraper-builder | 708 | +208 |
| gitlab-glab | 704 | +204 |
| acli | 621 | +121 |

This makes SKILL.md files hard to scan, increases token consumption on every skill load, and violates the progressive disclosure pattern.

## Solution

Apply the **progressive disclosure pattern**:
1. Keep SKILL.md under 500 lines with: overview, critical rules, quick reference tables, decision trees, and links
2. Move detailed commands, full examples, and troubleshooting to `references/*.md` files
3. Maintain valid YAML frontmatter on all files
4. Preserve all cross-skill references

## Impact

- **Token savings**: ~75% reduction in SKILL.md body size (4,958 -> 1,241 lines)
- **Scannability**: Each skill overview fits in under 2 minutes of reading
- **Maintainability**: Reference files organized by topic for easy updates
- **No behavior change**: All existing functionality preserved
