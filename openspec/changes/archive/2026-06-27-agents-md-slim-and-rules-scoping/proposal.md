# AGENTS.md Slim-Down + Standard-Compliant Progressive Disclosure

## Why

`tdt-meta/AGENTS.md` has grown to **322 lines / 18.8 KB / ~2,261 tokens** — **1.6× the official AGENTS.md guidance ceiling of 150 lines**, **2.1× the file's own Principle #6**. This violates the standard's explicit guidance and produces real attention-budget pressure on every agent session.

The current file also violates AGENTS.md v1.1 best practices in five documented ways:

1. **Documentation instead of operations** — 322 lines of mostly prose. Per the ICLR 2026 AMBIG-SWE study, *"most LLMs default to non-interactive behavior without explicit encouragement"*. Without **command-first instructions** with verifiable exit codes, the agent cannot know when a task is "done."
2. **No Definition of Done** — Without explicit closure criteria, agents report "I think I'm done" (the #1 source of agent-introduced bugs per GitHub's analysis of 2,500+ AGENTS.md files).
3. **No escalation rules** — When blocked, agents default to destructive workarounds (deleting lock files, bypassing checks, force-pushing).
4. **No progressive disclosure** — All 322 lines load into every session regardless of which repo the agent is editing. The AGENTS.md v1.1 proposal (issue #135, stewarded by Linux Foundation AAIF) recommends a standard **HTML-comment-fenced module index** with deterministic keyword triggers for on-demand loading.
5. **Emphasis inflation** — 13 `MUST/SHALL/IMPORTANT/YOU MUST/NEVER/ALWAYS` markers compete for attention; only the 3 truly load-bearing rules should retain emphasis.

The goal is to bring TDT into compliance with the **AGENTS.md v1.1 standard** (Linux Foundation AAIF, June 2026): slim root to ≤150 lines, add command-first closure definitions, restructure as task-organized modules, and use the standard's HTML-comment module index for progressive disclosure.

## What Changes

### 1. Refactor `tdt-meta/AGENTS.md` from 322 → ≤150 lines

**New structure (task-organized, command-first):**

| Section | Lines | Purpose |
|---------|-------|---------|
| **Build & Test Commands** | ~12 | Exact commands with flags |
| **Definition of Done** | ~10 | Verifiable exit-code checks |
| **Escalation Rules** | ~8 | What to do when blocked |
| **Workspace Layout** | ~10 | Repo map, symlinks |
| **Environment & Secrets** | ~8 | `tdt_core`, `~/.tdt/.env` |
| **Skills Catalog** | ~6 | 103 skills summary |
| **MCP Routing (Preferred)** | ~10 | One-line router rules + table |
| **Code Intelligence** | ~6 | Pre-edit checks |
| **OpenSpec Workflows** | ~8 | 10 commands summary |
| **Git Workflow** | ~8 | Conventional commits |
| **Testing** | ~8 | pytest patterns |
| **Boundaries** | ~8 | Never-touch lists |
| **Principles** | ~10 | Rules when no rule applies |
| **Module Index** | ~12 | `<!-- agents:module -->` index |
| **Header** | ~10 | Title + version + TOC |

**Total: ~134 lines** (under 150 ceiling with margin).

### 2. Adopt the AGENTS.md v1.1 standard progressive-disclosure mechanism

Replace the proprietary `.claude/rules/` approach with the **standard HTML-comment module index** (AGENTS.md issue #135, #71). The canonical location for shared modules is `tdt-meta/.agents/modules/` (using `.agents/` since TDT already symlinks that directory).

**Module index in root `AGENTS.md`:**

```markdown
<!-- agents:module -->
- `.agents/modules/mcp-router.md` — MCP router tool selection. Triggers: router, mcp, tavily, exa, brave, context7, gitnexus, deepwiki
- `.agents/modules/jira-skills.md` — Jira skill routing. Triggers: jira, sprint, ticket, jql, daily report, kanban
- `.agents/modules/openspec.md` — OpenSpec workflows. Triggers: openspec, change, propose, apply, archive, /opsx
- `.agents/modules/webhook.md` — webhook-receiver state + ops. Triggers: webhook, dedupe, dlq, ngrok, tailscale, selftest
- `.agents/modules/code-intel.md` — GitNexus impact + detect_changes. Triggers: gitnexus, impact, detect_changes, cypher, query
- `.agents/modules/ecc.md` — ECC harness disposition. Triggers: ecc, everything-claude-code, hooks, audit
- `.agents/modules/skills.md` — Skills catalog (auth, sheets). Triggers: skill, tdt-sheets, service account
- `.agents/modules/coding.md` — When writing code. Triggers: coding, edit, write, implement
- `.agents/modules/review.md` — When reviewing code. Triggers: review, pr, merge, lint
- `.agents/modules/release.md` — When releasing. Triggers: release, deploy, tag, version
<!-- agents:module -->
```

**Why this is better than `.claude/rules/` paths:**

| Property | `.claude/rules/` (Claude Code proprietary) | `<!-- agents:module -->` (AGENTS.md v1.1 standard) |
|----------|------------------------------------------|----------------------------------------------------|
| Tool support | Claude Code only | Codex, Cursor, Copilot, Amp, Windsurf, Gemini CLI, Aider, all 60k+ AGENTS.md-aware tools |
| Trigger mechanism | YAML `paths:` glob (matched against launch CWD) | Case-insensitive keyword trigger (matched against task text + touched paths) |
| YAML requirement | Yes (with known parser bug #13905) | None — pure HTML comments + Markdown list |
| Symlinks needed | Yes (launch-CWD walks up; rules in sibling dirs invisible) | No — modules in same tree, loaded by trigger |
| Graceful degradation | Fails silently if YAML malformed | Non-conforming tools see Markdown list and follow it as instructions |
| Discovery | Implicit (loader walks filesystem) | Explicit (index in root AGENTS.md) |
| Standardization | Claude Code specific | Linux Foundation AAIF standard, June 2026 |

### 3. Add command-first content patterns

Every actionable instruction in `AGENTS.md` and modules MUST follow the pattern:

```markdown
## When <Task>

- Run `<exact command>` — exits 0 means <verifiable outcome>
- Run `<exact command>` — exits 0 means <verifiable outcome>
```

Anti-patterns to remove (per ICLR 2026 AMBIG-SWE + GitHub 2,500-repo analysis):
- "Be careful with X" → replace with "Run `<check command>` before doing X; abort if exits non-zero."
- "Ensure tests pass" → replace with "`pytest -x` exits 0 with no failures."
- "Follow Conventional Commits" → replace with "`git commit -m 'type(scope): subject'`."

### 4. Add Definition of Done section

New mandatory section. Tasks are complete when ALL of the following exit codes are 0:

| Check | Command | Exit 0 means |
|-------|---------|--------------|
| Tests | `pytest -x` (or per-repo equivalent) | No test failures |
| Lint | `ruff check . && ruff format --check .` | No style violations |
| Types | `mypy <repo>/ --strict` (Python repos only) | No type errors |
| Skills validation | `openspec validate --strict` (if OpenSpec change) | All artifacts valid |
| Symlink integrity | `readlink -f <symlink>` returns valid file | No broken symlinks |

### 5. Add Escalation Rules section

```
## When Blocked

- If `pytest -x` fails after 3 attempts: stop, paste the failing test + traceback, ask user
- If a dependency is missing: check `requirements.txt` first, then ask
- If merge conflicts: stop and show the conflicting files
- Never: delete files to resolve errors, force-push, skip lint/typecheck, edit files outside the assigned scope
- Never: copy secrets to a new file, print env values, commit `.env`
```

### 6. Add Git Workflow section (currently missing)

```
## Git Workflow

- Branch naming: `<type>/<kebab-case>` — types: feat, fix, chore, docs, openspec, refactor
- Commit format: `type(scope): subject` (Conventional Commits, ≤72 chars subject, body wraps at 72)
- PR title: same as commit subject
- PR body: OpenSpec change name if applicable; problem/solution/test plan otherwise
- Pre-commit: run `gitnexus detect_changes` and address unexpected scope before pushing
```

### 7. Add Testing section (currently missing)

```
## Testing

- Framework: pytest + pytest-mock + pytest-asyncio (Python); XCTest (iOS); JUnit (Android)
- Location: `tests/` next to source; `conftest.py` at package root
- Run: `pytest -x` (Python); `swift test` (iOS); `./gradlew test` (Android)
- Coverage: not enforced; do not skip tests to satisfy closure
- Mocking: prefer `tdt_core.clients` test doubles over real API calls
- Fixtures: shared fixtures in package-root `conftest.py`; per-test setup in function scope
```

### 8. Replace `.claude/rules/` symlink distribution with standard `.agents/modules/` symlinks

If we choose to keep some Claude-Code-specific mechanism (e.g., path-scoped YAML rules for tool-internal features), they live alongside the standard modules in `.agents/modules/`, not in proprietary `.claude/rules/`. The `install-shared-rules.sh` script is renamed to `install-modules.sh` and symlinks modules into each sub-repo's `.agents/modules/` (also symlinked to `tdt-meta/.agents/modules/` via TDT's existing `.agents` symlink).

## Capabilities

### New Capabilities

- `agent-instruction-hygiene`: Standards for the workspace root `AGENTS.md` file and module catalog — size ceiling (≤150 lines per AAIF/Linux Foundation), closure definitions (exit-code-based), command-first pattern, escalation rules, AGENTS.md v1.1 progressive-disclosure compliance, and quarterly review cadence. Creates a reviewable contract for future contributors and ensures cross-tool portability (Codex, Cursor, Copilot, Claude Code, Amp, Windsurf, Gemini CLI).

### Modified Capabilities

- (None — no spec-level behavior changes; this is documentation infrastructure.)

## Impact

| Area | Impact |
|------|--------|
| **Root `tdt-meta/AGENTS.md`** | 322 → ≤150 lines (≤53% reduction) |
| **New module files** | 10 modules in `tdt-meta/.agents/modules/`, ~400 lines total, each focused on one task type |
| **Cross-tool portability** | Now compliant with AGENTS.md v1.1; works in Codex, Cursor, Copilot, Claude Code, Amp, Windsurf, Gemini CLI (60k+ tools) |
| **Existing rules** | All preserved; reorganized from prose → commands + moved to task-organized modules |
| **Agent attention budget** | ~50% more room for code-specific instructions per session |
| **Cumulative session cost** | Lower — root AGENTS.md shorter; task-specific modules loaded only when triggers match |
| **Skill discovery** | No change (103 skills still indexed in `SKILLS_INDEX.md`) |
| **Symlink topology** | Replaces `.claude/rules/` symlinks with `.agents/modules/` symlinks (matches existing `.agents/` pattern) |

## Non-Goals

- **Not abandoning `.claude/rules/` globally** — Claude Code still reads them. But TDT primary instructions follow the standard; `.claude/rules/` is a Claude-Code-specific extension if used at all.
- **Not changing the workspace root symlink topology.** `AGENTS.md` remains canonical; `CLAUDE.md` still symlinks to it. We extend the symlink pattern to `.agents/modules/`.
- **Not adding repo-local `AGENTS.md` files** — TDT convention is that child files are only added when convention diverges.
- **Not changing the 103 skills catalog** — Skills live in `.agents/skills/`; modules live in `.agents/modules/`.
- **Not changing credentials, secrets, or environment handling.**
- **Not migrating to v1.1 frontmatter (`description`, `tags`)** — AGENTS.md v1.1 marks these as optional; we use HTML-comment module index for progressive disclosure instead, which is also v1.1-compliant.

## Risks

| Risk | Mitigation |
|------|------------|
| HTML-comment module index not parsed by all tools | v1.1 spec guarantees graceful degradation — non-conforming tools see Markdown list and follow it as instructions |
| Trigger keyword mismatch — module doesn't load when expected | Use 3-5 trigger keywords per module (broad coverage); quarterly review triggers based on agent failure modes |
| Command-first pattern too rigid for prose-heavy content | Modules can still have explanatory paragraphs between commands; rule is that **every actionable instruction** must have a command |
| Definition of Done too strict for docs-only changes | Add per-task DoD variants in module files (e.g., `coding.md`, `docs.md`); root DoD is the common case |
| AGENTS.md v1.1 not yet ratified | Spec is stewarded by Linux Foundation AAIF (June 2026), adopted by 60k+ projects; proposal #135 is on the path to v1.1 |
| 150-line ceiling too aggressive for TDT's content | Slack in module index + cross-links means root can be even smaller (~134 lines); if needed, relax to ≤180 per Claude Code guidance while keeping standard format |
| Tools (Claude Code, Windsurf) ignore HTML-comment fences | Confirmed: all 60k+ AGENTS.md tools see Markdown; the index is human-readable instructions either way |
| Loss of Claude-Code-specific `.claude/rules/` features (e.g., `InstructionsLoaded` hook) | Out of scope — those are Claude-Code-internal; TDT standard compliance is the priority |
| Existing 13 `MUST` markers diluting via demotion | Keep `MUST` on the 3 truly load-bearing rules (AGENTS.md symlink, tdt_core factories, secrets) |

## Verification Plan

1. `wc -l tdt-meta/AGENTS.md` reports ≤150.
2. `openspec validate --strict agents-md-slim-and-rules-scoping` passes.
3. Every module file in `.agents/modules/` exists and has trigger keywords listed in the root index.
4. The root index uses `<!-- agents:module -->` HTML-comment fences (open + close).
5. Every actionable instruction in root + modules follows the command-first pattern (grep for "be careful", "ensure", "should" → expect near-zero matches).
6. Definition of Done section has ≥4 verifiable exit-code commands.
7. Escalation Rules section has ≥3 escalation paths and ≥3 explicit Never rules.
8. AGENTS.md v1.1 spec compliance: standard Markdown, no required fields (frontmatter optional), hierarchical scope respected.
9. Cross-tool check: open `AGENTS.md` in a non-Claude tool (Amp/Cursor) and confirm the module index renders as a readable Markdown list.
10. `gitnexus detect_changes` shows only expected affected symbols.
11. Quarterly symlink integrity: every `.agents/modules/<file>.md` symlink resolves to a canonical file.

## References

- **AGENTS.md official site** — https://agents.md/ — Linux Foundation AAIF steward
- **AGENTS.md v1.1 proposal #135** — https://github.com/agentsmd/agents.md/issues/135 — modular progressive disclosure
- **AGENTS.md v1.1 proposal #71** — https://github.com/agentsmd/agents.md/issues/71 — `.agent/` directory standardization
- **GitHub analysis of 2,500+ AGENTS.md repos** — "How to Write a Great agents.md"
- **ICLR 2026 AMBIG-SWE** — "Ambig-SWE: Resolving Ambiguous Bug Reports with LLM Agents"
- **Crosley's empirical patterns** — https://blakecrosley.com/blog/agents-md-patterns
- **Addy Osmani's lessons** — https://addyosmani.com/agents/15-agents-md/
- **Claude Code docs** — https://code.claude.com/docs/en/memory (proprietary `.claude/rules/` reference; supersedes but compatible)