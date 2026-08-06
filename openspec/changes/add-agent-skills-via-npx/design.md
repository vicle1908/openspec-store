# Design: Add Agent Skills via `npx skills`

## Architecture

```
npx skills add <owner/repo> -g -y
        │
        ▼
~/.agents/skills/<skill-name>/SKILL.md    ← global install
        │
        ├── symlink → ~/.hermes/skills/<skill-name>/
        ├── symlink → ~/.claude/skills/<skill-name>/
        ├── symlink → ~/.fable-5kills/<skill-name>/
        ├── symlink → ~/.cursor/skills/<skill-name>/
        └── symlink → ... (17+ agents)
```

## Skill Format (agentskills.io)

```yaml
---
name: skill-name              # lowercase, hyphens, matches folder
description: Use when <trigger>. <behavior>.  # ≤1024 chars
license: MIT
metadata:
  author: <owner>
---
# Skill Title
Instructions body...
```

## Installation Strategy

### Global Skills (shared across all projects)

```bash
npx skills add <owner/repo> -g -y        # install all skills from repo
npx skills add <owner/repo@skill> -g -y  # install specific skill
```

Global skills live at `~/.agents/skills/` and are symlinked into each
agent's skill directory. Hermes picks them up automatically.

### Project-Level Skills (per-repo)

```bash
cd ~/Developer/<repo>
npx skills add <owner/repo> -y           # creates .agents/skills/ + skills-lock.json
```

Project skills are tracked in `skills-lock.json` for reproducibility.

### CLI Tool Installation

Some skills reference CLI tools. Install globally for permanent access:

```bash
npm install -g @firecrawl/anydoc    # permanent anydoc command
```

Without global install, `npx -y @firecrawl/anydoc` downloads on each run
(cached after first use, but adds ~2s startup).

## Naming Conventions (agentskills.io spec)

| Rule | Detail |
|------|--------|
| Folder name | Lowercase, hyphens, ≤64 chars |
| `name` field | Must match folder name |
| `description` | ≤1024 chars, trigger phrase in first 57 chars |
| Body | Concise instructions, not exhaustive docs |
| Scripts | `scripts/` subdir, executable |
| References | `references/` subdir, loaded on demand |

## Trade-offs

| Choice | Pros | Cons |
|--------|------|------|
| Global install | All agents benefit, one update path | Skills available even when not relevant |
| `npx -y` (no global CLI) | No npm global pollution | ~2s startup per invocation |
| Global CLI install | Fast execution | Must manage npm globals |

**Decision:** Install `@firecrawl/anydoc` globally (frequent use). Other skills
are instruction-only (no CLI dependency).

## Verification

After installation:
1. `npx skills ls -g` — confirms all skills listed
2. `ls ~/.hermes/skills/` — confirms Hermes symlinks
3. Test each skill with a sample prompt in Hermes
4. Verify `anydoc --help` works for the CLI tool
