# Proposal: Add Agent Skills via `npx skills`

## Why

The workspace has 16 Python repos, 1 Go monorepo, and multiple coding agents
(Claude Code, Codex, OpenCode, Pi, Hermes). Skills are currently managed
independently per agent — Hermes uses `~/.hermes/skills/`, Claude uses
`~/.claude/skills/`, etc. This creates duplication and drift.

The **Agent Skills** standard (agentskills.io) provides a cross-agent skill
format: a `SKILL.md` with YAML frontmatter that works across 20+ agent
products. The `npx skills` CLI manages installation, symlinking, and updates.

Adding skills via `npx skills` gives:
- **One skill, all agents** — install once, symlinked to all compatible agents
- **Discoverable** — `npx skills find` searches the ecosystem registry
- **Updatable** — `npx skills update` pulls latest versions
- **Portable** — `skills-lock.json` makes project-level skills reproducible

## What Changes

### Skills to Install (Global)

| Skill | Source | Purpose | CLI Tool |
|-------|--------|---------|----------|
| `convert-documents-to-markdown` | firecrawl/anydoc | Doc/Excel/PDF → Markdown | `npx -y @firecrawl/anydoc` |
| `python-testing-patterns` | wshobson/agents | pytest/unittest patterns | — |
| `python-design-patterns` | wshobson/agents | Python code quality | — |
| `python-performance-optimization` | wshobson/agents | Perf tuning | — |
| `golang-documentation` | samber/cc-skills-golang | Go doc patterns | — |
| `multi-stage-dockerfile` | github/awesome-copilot | Docker optimization | — |
| `docker-patterns` | affaan-m/everything-claude-code | Docker best practices | — |

### CLI Tools to Install

| Tool | Install | Purpose |
|------|---------|---------|
| `@firecrawl/anydoc` | `npm install -g @firecrawl/anydoc` | Permanent `anydoc` command (vs npx each time) |

### Agent Wiring

- Global skills install to `~/.agents/skills/` with symlinks to each agent's
  skill directory
- Hermes discovers them via `~/.hermes/skills/` symlink
- No MCP registration needed (these are CLI-instruction skills, not MCP tools)

### Naming Convention (per agentskills.io spec)

- Skill folder name = `name` field in frontmatter (lowercase, hyphens)
- Description ≤ 1024 chars, trigger phrase in first 57 chars
- Body: concise instructions, not exhaustive docs
- Scripts in `scripts/` subdir, references in `references/`

## Scope

- Config/infrastructure change only — no spec deltas (`skip_specs: true`)
- Affects: `~/.agents/skills/`, `~/.hermes/skills/`, global npm
- Does NOT affect: application source code, existing specs, MCP registrations
