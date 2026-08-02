# AGENTS.md Refactor — Design

## Context

Current state: `tdt-meta/AGENTS.md` is **322 lines / 18.8 KB / ~2,261 tokens**. The AGENTS.md official standard (Linux Foundation AAIF, June 2026) recommends ≤150 lines. GitHub's analysis of 2,500+ repositories found *"Most agent files fail because they're too vague, not because of technical limitations."*

Five documented failure modes (per ICLR 2026 AMBIG-SWE + Crosley's empirical patterns):

1. **Prose paragraphs without commands** — agents skip them; represent as vague preference, proceed without verification.
2. **Ambiguous directives** — "be careful", "where possible", "gracefully" have no trigger conditions or thresholds.
3. **Contradictory priorities without ordering** — agents skip verification, rush to code generation. AMBIG-SWE measured 42% drop in resolve rates when agents skip clarification.
4. **No Definition of Done** — agents report "I think I'm done"; the #1 source of agent-introduced bugs.
5. **No escalation rules** — when blocked, agents default to destructive workarounds (deleting lock files, force-pushing).

The TDT file has all five. The fix is structural: rewrite as **command-first, task-organized, closure-defined** instructions with a **standard AGENTS.md v1.1 module index** for progressive disclosure.

## Goals / Non-Goals

**Goals:**
- Reduce root `tdt-meta/AGENTS.md` from 322 → ≤150 lines.
- Adopt **AGENTS.md v1.1 standard** (Linux Foundation AAIF, June 2026): module index with `<!-- agents:module -->` fences, deterministic keyword triggers, graceful degradation.
- All actionable instructions follow the **command-first pattern**: every instruction has a verifiable exit-code command.
- Add **Definition of Done** section with exit-code-based closure criteria.
- Add **Escalation Rules** section with explicit Never rules.
- Add **Git Workflow** + **Testing** sections (currently missing).
- Restructure as **task-organized** modules: `coding`, `review`, `release` + topical modules.
- Preserve every current rule — relocate and rewrite, don't delete.
- Keep `MUST` markers only on the 3 truly non-negotiable invariants.

**Non-Goals:**
- Don't change the workspace root symlink topology (AGENTS.md → tdt-meta/AGENTS.md).
- Don't add repo-local `AGENTS.md` files.
- Don't change the 103-skill catalog in `.agents/skills/`.
- Don't change credentials, secrets, or environment handling.
- Don't migrate to AGENTS.md v1.1 frontmatter (`description`, `tags`) — module index suffices for progressive disclosure.

## Critical Research Findings

### Finding 1: AGENTS.md v1.1 progressive-disclosure mechanism (June 2026)

Per Linux Foundation AAIF (issue #135), the standard module index is:

```markdown
<!-- agents:module -->
- `.agents/modules/<file>.md` — description. Triggers: keyword1, keyword2, ...
<!-- agents:module -->
```

- **Conforming tools** parse the fences and inject matching modules when triggers match (case-insensitive substring on task text + touched paths).
- **Non-conforming tools** see a Markdown list and follow it as natural-language instructions. Graceful degradation built into the spec.

### Finding 2: Trigger-based selection > path-based selection

Claude Code's `.claude/rules/` uses **path globs** matched against launch CWD. The AGENTS.md v1.1 standard uses **keyword triggers** matched against task context.

| Mechanism | Pros | Cons |
|-----------|------|------|
| Path glob (`.claude/rules/`) | Precise file-type targeting | Symlink topology issues, YAML bug, Claude-Code-only |
| Keyword trigger (AGENTS.md v1.1) | Tool-agnostic, no YAML, matches intent | May over-trigger on ambiguous tasks |

TDT should adopt the standard for portability. Keyword triggers are case-insensitive substring matches — "deliberately primitive, deliberately deterministic" per the v1.1 proposal.

### Finding 3: ICLR 2026 AMBIG-SWE — agents default to non-interactive behavior

> *"Most LLMs default to non-interactive behavior without explicit encouragement, proceeding silently rather than asking clarifying questions, which dropped resolve rates from 48.8% to 28%."*

Fix: **Definition of Done** with explicit closure criteria, plus **Escalation Rules** that force interaction when blocked.

### Finding 4: GitHub's analysis of 2,500+ AGENTS.md repos

> *"Most agent files fail because they're too vague, not because of technical limitations."*

Fix: **command-first pattern** — every instruction has a verifiable exit-code command. Examples:

- "Be careful with database migrations" → "Run `alembic check` before applying migrations; abort if exits non-zero."
- "Ensure tests pass" → "`pytest -x` exits 0."
- "Follow Conventional Commits" → "`git commit -m 'type(scope): subject'`."

### Finding 5: 60k+ projects adopt AGENTS.md; 7 tools have native support

Per Linux Foundation announcement (June 2026):

| Tool | Native File | Reads AGENTS.md |
|------|-------------|-----------------|
| Codex CLI | `AGENTS.md` | Yes (native) |
| Cursor | `.cursor/rules` | Yes (auto-discovered) |
| GitHub Copilot | `.github/copilot-instructions.md` | Yes |
| Amp | `AGENTS.md` | Yes (native) |
| Windsurf | `.windsurfrules` | Yes |
| Gemini CLI | `GEMINI.md` | Configurable |
| Claude Code | `CLAUDE.md` | Symlink / `@AGENTS.md` |

By following AGENTS.md v1.1 instead of Claude Code's proprietary `.claude/rules/`, TDT gets **cross-tool portability** for free.

## Decisions

### Decision 1: Module index, not `.claude/rules/`

**Choice:** Adopt AGENTS.md v1.1 HTML-comment module index. Symlink modules from canonical `tdt-meta/.agents/modules/` to each sub-repo's `.agents/modules/` (which TDT already symlinks via the existing `.agents` symlink at `$HOME/Developer/tdt/.agents`).

**Rationale:**
- Standard (Linux Foundation AAIF).
- Cross-tool (7+ tools read it; 60k+ projects adopt it).
- No YAML parsing bugs (no frontmatter required).
- No symlink topology surprises (modules live in same tree as root AGENTS.md).
- Graceful degradation built in (non-conforming tools see Markdown list).

**Trade-off:** Keyword triggers may over-fire on ambiguous tasks. Mitigation: use 3-5 specific keywords per module, audit quarterly.

### Decision 2: Task-organized module structure

| Module | Task triggers | Purpose |
|--------|---------------|---------|
| `coding.md` | coding, edit, write, implement, refactor | When writing code |
| `review.md` | review, pr, merge, lint | When reviewing code |
| `release.md` | release, deploy, tag, version | When releasing |
| `mcp-router.md` | router, mcp, tavily, exa, brave, context7, gitnexus, deepwiki | MCP tool selection |
| `jira-skills.md` | jira, sprint, ticket, jql, kanban, daily report | Jira routing |
| `openspec.md` | openspec, change, propose, apply, archive, /opsx | OpenSpec workflows |
| `webhook.md` | webhook, dedupe, dlq, ngrok, tailscale, selftest | webhook-receiver state |
| `code-intel.md` | gitnexus, impact, detect_changes, cypher, query | Pre-edit checks |
| `ecc.md` | ecc, everything-claude-code, hooks, audit | ECC disposition |
| `skills.md` | skill, tdt-sheets, service account | Skills catalog |

### Decision 3: Definition of Done format

```
## Definition of Done

A task is complete when ALL of the following return exit code 0:

| Check | Command |
|-------|---------|
| Tests | `pytest -x` (Python) / `swift test` (iOS) / `./gradlew test` (Android) |
| Lint | `ruff check . && ruff format --check .` |
| Types | `mypy <repo>/ --strict` (Python only) |
| Spec validation | `openspec validate --strict` (if OpenSpec change) |
| Module symlinks | All `.agents/modules/<file>.md` resolve via `readlink -f` |
```

### Decision 4: Escalation Rules format

```
## Escalation Rules

### When Blocked

- If `pytest -x` fails after 3 attempts: stop, paste failing test + traceback, ask user
- If a dependency is missing: check `requirements.txt` first, then ask
- If merge conflicts: stop, show conflicting files, ask user
- If `openspec validate` reports blocker: read the report, fix issues, re-run

### Never

- Delete files to resolve errors
- Force-push to main/master
- Skip lint/typecheck via `--no-verify` or similar
- Edit files outside the assigned scope
- Copy secrets to a new file, print env values, commit `.env`
```

### Decision 5: Cross-link architecture

Root `AGENTS.md` sections that have a module end with:

```markdown
Full content: `.agents/modules/<file>.md` — triggers: <keyword list>
```

This is the module index entry, kept short in-line and full content in the module.

### Decision 6: Symlink distribution

```bash
# install-modules.sh
SHARED="$HOME/Developer/tdt/tdt-meta/.agents/modules"
REPOS=(webhook-receiver ai-review tdt-core poems-mobile3-ios ...)

for repo in "${REPOS[@]}"; do
    REPO_DIR="$HOME/Developer/tdt/$repo"
    TARGET="$REPO_DIR/.agents/modules"
    [ -d "$REPO_DIR" ] || continue
    mkdir -p "$TARGET"
    for module in "$SHARED"/*.md; do
        ln -sf "$module" "$TARGET/$(basename "$module")"
    done
done
```

Replaces the previous `.claude/rules/` distribution strategy.

### Decision 7: Demote 10 of 13 MUST markers

Keep `MUST` only on:
- AGENTS.md symlink (canonical source)
- tdt_core factories (no raw SDK clients)
- Secrets in `~/.tdt/.env`

All other rules become imperative phrasing or commands.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Module triggers over-fire on ambiguous tasks | Use 3-5 specific keywords; quarterly review triggers based on agent failure modes |
| Command-first pattern too rigid for prose-heavy sections | Modules can have explanatory paragraphs between commands; only actionable instructions need commands |
| Definition of Done too strict for docs-only changes | Add per-task DoD variants in module files (`coding.md`, `docs.md`); root DoD is the common case |
| AGENTS.md v1.1 not yet ratified | Spec stewarded by Linux Foundation AAIF (June 2026); 60k+ projects already adopt; graceful degradation guarantees |
| Loss of Claude-Code-specific features | Acceptable trade-off — cross-tool portability is the priority |
| Symlink cascade risk | Git tracks symlinks; deletion of canonical file cascades; caught in PR review |
| 150-line ceiling too aggressive | Slack in module index + cross-links means root can be ≤134 lines; if needed, relax to ≤180 per Claude Code guidance while keeping standard format |

## Implementation order

1. Create `tdt-meta/.agents/modules/` and write 10 module files (each task-focused, command-first).
2. Write the new slim root `tdt-meta/AGENTS.md` (≤150 lines, with module index using `<!-- agents:module -->` fences).
3. Create `tdt-meta/scripts/install-modules.sh` to symlink modules to each sub-repo's `.agents/modules/`.
4. Run the script and verify symlink integrity.
5. Run `openspec validate` and representative end-to-end tasks.

## References

- AGENTS.md official site — https://agents.md/
- AGENTS.md v1.1 proposal #135 — modular progressive disclosure
- AGENTS.md v1.1 proposal #71 — `.agent/` directory standardization
- ICLR 2026 AMBIG-SWE — agents default to non-interactive behavior
- Crosley's empirical AGENTS.md patterns — https://blakecrosley.com/blog/agents-md-patterns
- Addy Osmani's AGENTS.md lessons — https://addyosmani.com/agents/15-agents-md/
- GitHub analysis of 2,500+ AGENTS.md repos