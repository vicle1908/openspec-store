# Agent Instruction Hygiene (AGENTS.md v1.1 Compliant)

## ADDED Requirements

### Requirement: Root AGENTS.md size ceiling

The workspace root `AGENTS.md` file (canonical at `tdt-meta/AGENTS.md`, symlinked from `$HOME/Developer/tdt/AGENTS.md` and `$HOME/Developer/tdt/CLAUDE.md`) MUST NOT exceed **150 lines** when measured by `wc -l`, per the Linux Foundation AAIF AGENTS.md standard (June 2026).

#### Scenario: File grows past 150 lines
- **WHEN** a contributor adds new content to `tdt-meta/AGENTS.md` that would push the line count above 150
- **THEN** the contributor SHALL extract verbose sub-content to `tdt-meta/.agents/modules/<file>.md` and add an entry to the root module index (using the `<!-- agents:module -->` fence per Requirement 3 below)

#### Scenario: Quarterly review detects bloat
- **WHEN** the quarterly review detects `tdt-meta/AGENTS.md` has grown past 150 lines
- **THEN** the reviewer SHALL open an OpenSpec change to extract the offending content

### Requirement: Mandatory sections in root AGENTS.md

The workspace root `tdt-meta/AGENTS.md` MUST contain at least these section headings, in this order:

1. `# TDT — Agent Instructions`
2. `## Definition of Done`  *(new — required by AMBIG-SWE 2026 closure pattern)*
3. `## Escalation Rules`  *(new — required to prevent destructive workarounds)*
4. `## Workspace Layout`
5. `## Environment & Secrets`
6. `## Build & Test Commands`
7. `## Git Workflow`  *(new — was missing)*
8. `## Testing`  *(new — was missing)*
9. `## Skills Catalog`
10. `## MCP Routing (Preferred)`
11. `## Code Intelligence`
12. `## OpenSpec Workflows`
13. `## Boundaries`
14. `## Principles`
15. `## Module Index`  *(new — AGENTS.md v1.1 progressive disclosure)*

Each section SHALL be ≤20 lines. Sections that exceed 20 lines SHALL be extracted to a module per Requirement 3.

#### Scenario: New mandatory section is added
- **WHEN** the workspace adopts a new area requiring agent attention
- **THEN** the contributor SHALL add the section to the mandatory list above (in the appropriate position) and update `tdt-meta/AGENTS.md`

#### Scenario: Existing section is consolidated
- **WHEN** two adjacent sections can be merged without losing clarity
- **THEN** the contributor SHALL update the mandatory list to reflect the merge

### Requirement: AGENTS.md v1.1 progressive-disclosure module index

The workspace root `tdt-meta/AGENTS.md` SHALL include a `## Module Index` section using the **AGENTS.md v1.1 standard HTML-comment module index format** (Linux Foundation AAIF, issue #135). The format uses HTML-comment fences (`<!-- agents:module -->` open + close) wrapping a Markdown list of module references with path, description, and trigger keywords.

Format: each line MUST be `\`.<relative-path>\` — <description>. Triggers: <kw1>, <kw2>, <kw3>`. Lines are wrapped between the open and close HTML-comment fences.

#### Scenario: Contributor adds a new module
- **WHEN** a contributor creates a new module file in `tdt-meta/.agents/modules/`
- **THEN** the contributor SHALL add a corresponding entry to the root `## Module Index` between the `<!-- agents:module -->` and `<!-- agents:module -->` fences, with:
  - Relative path from repo root (e.g., `.agents/modules/<file>.md`)
  - One-sentence description
  - 3-5 trigger keywords (case-insensitive substring match per v1.1 spec)

#### Scenario: Module trigger keywords are missing or too few
- **WHEN** the quarterly review finds a module index entry with <3 trigger keywords or no description
- **THEN** the reviewer SHALL add the missing fields; modules with <2 trigger keywords SHALL be flagged as low-discoverability and merged into adjacent modules

#### Scenario: Non-conforming tool reads AGENTS.md
- **WHEN** an AI agent tool that does not implement the v1.1 module index parser reads `tdt-meta/AGENTS.md`
- **THEN** the tool SHALL see a human-readable Markdown list with full paths and trigger keywords; per v1.1 spec, graceful degradation guarantees the list reads as natural-language instructions

#### Scenario: Module index fences are unbalanced
- **WHEN** the pre-commit lint detects an unbalanced `<!-- agents:module -->` fence (open without close, or close without open)
- **THEN** the lint SHALL reject the change with: *"Module index fences must be balanced (open + close)."*

#### Scenario: Module file path in index is wrong
- **WHEN** the root module index references a path that does not exist in `tdt-meta/.agents/modules/`
- **THEN** the pre-commit lint SHALL reject the change with: *"Module index references non-existent file: <path>"*

### Requirement: Command-first instruction pattern

Every actionable instruction in `tdt-meta/AGENTS.md` and all module files SHALL follow the **command-first pattern**: each instruction must have a verifiable shell command the agent can run to confirm completion.

#### Scenario: Contributor writes a prose-only instruction
- **WHEN** a contributor adds an instruction without a verifiable command (e.g., "be careful with database migrations", "ensure tests pass")
- **THEN** the pre-commit lint SHALL reject the change with: *"Actionable instructions must include a verifiable command. See AGENTS.md v1.1 command-first pattern. Example: 'Run `pytest -x` — exits 0 means no test failures.'"*

#### Scenario: Command has no exit-code semantics
- **WHEN** a contributor writes a command without specifying what exit code 0 means (e.g., "run `pytest`")
- **THEN** the pre-commit lint SHALL flag the command as ambiguous and require a closure statement: "exits 0 means ..."

#### Scenario: Anti-patterns detected
- **WHEN** the pre-commit lint detects any of these anti-patterns in `AGENTS.md` or modules:
  - "be careful"
  - "where possible"
  - "gracefully"
  - "ensure" without a following command
  - "should" used as a directive (vs. as a description)
- **THEN** the lint SHALL emit a warning (non-blocking) recommending the command-first replacement

### Requirement: Definition of Done — verifiable closure criteria

The `## Definition of Done` section in `tdt-meta/AGENTS.md` SHALL list **at least 4 verifiable closure checks**, each expressed as a shell command whose exit code 0 indicates success.

The mandatory minimum checks (when applicable):

| Check | Command | When applicable |
|-------|---------|-----------------|
| Tests | `pytest -x` (Python); `swift test` (iOS); `./gradlew test` (Android) | All code changes |
| Lint | `ruff check . && ruff format --check .` | All Python repos |
| Types | `mypy <repo>/ --strict` | Python repos with type hints |
| Spec validation | `openspec validate --strict` | All OpenSpec changes |
| Symlink integrity | All `.agents/modules/<file>.md` symlinks resolve via `readlink -f` | All cross-repo changes |

#### Scenario: Task is reported complete without closure verification
- **WHEN** an agent reports a task as "done" without running the Definition of Done commands
- **THEN** the user SHALL prompt the agent to run each command and report exit codes; per ICLR 2026 AMBIG-SWE, *"most LLMs default to non-interactive behavior without explicit encouragement"* — explicit closure checks are the fix

#### Scenario: Closure check command is non-applicable
- **WHEN** a Definition of Done check does not apply to a particular task type (e.g., `pytest -x` for a docs-only change)
- **THEN** the agent SHALL skip the check and explicitly state which checks were skipped and why

### Requirement: Escalation Rules — what to do when blocked

The `## Escalation Rules` section SHALL contain:
- **At least 3 escalation paths** for common block scenarios.
- **At least 4 explicit Never rules** banning destructive recovery patterns.

#### Scenario: Agent hits blocked condition
- **WHEN** an agent encounters a block matching an Escalation Rule (e.g., `pytest -x` fails after 3 attempts, dependency missing, merge conflict)
- **THEN** the agent SHALL follow the specified escalation path: stop, surface context, ask the user

#### Scenario: Agent considers destructive recovery
- **WHEN** an agent considers any action on the Never list (delete files to resolve errors, force-push to main, skip lint/typecheck, edit files outside assigned scope, copy secrets to new files, print env values, commit `.env`)
- **THEN** the agent SHALL refuse and surface the conflict to the user

#### Scenario: Escalation Rules section is missing Never list
- **WHEN** the quarterly review finds the Escalation Rules section lacks explicit Never rules
- **THEN** the reviewer SHALL add the missing rules, drawing from the canonical Never list above

### Requirement: AGENTS.md v1.1 frontmatter discipline

Files in `tdt-meta/AGENTS.md` and `tdt-meta/.agents/modules/*.md` MAY include YAML frontmatter with optional fields per the AGENTS.md v1.1 spec. When frontmatter is present, the system SHALL enforce:

| Field | Type | Purpose | Enforcement |
|-------|------|---------|-------------|
| `description` | string (≤200 chars) | Concise summary of file contents | MUST be ≤200 chars if present |
| `tags` | list of strings | Keywords for discovery | MUST be a YAML list |
| `ignore` | list of globs | Files the agent SHOULD NOT read | MUST contain valid globs |
| `read_only` | list of globs | Files the agent MAY read but MUST NOT modify | MUST contain valid globs |

Frontmatter is **optional**; absence is conformant. Unrecognized fields SHALL be ignored for forward compatibility per v1.1 spec.

#### Scenario: Frontmatter contains YAML errors
- **WHEN** a file in `tdt-meta/.agents/` or `tdt-meta/AGENTS.md` contains YAML frontmatter that fails to parse
- **THEN** the pre-commit lint SHALL reject the change with the YAML error message

#### Scenario: `ignore` glob is malformed
- **WHEN** a `ignore:` or `read_only:` entry contains a non-glob string (e.g., absolute path with shell characters)
- **THEN** the pre-commit lint SHALL flag the entry and suggest a corrected glob

### Requirement: Cross-tool portability

`tdt-meta/AGENTS.md` SHALL be parseable by all major AI coding agent tools that read AGENTS.md:
- Codex CLI, Amp, Cursor, GitHub Copilot, Windsurf, Gemini CLI, Claude Code (via symlink).

#### Scenario: New tool is added to the supported list
- **WHEN** a new AI agent tool gains native AGENTS.md support (e.g., a future tool from a Linux Foundation AAIF member)
- **THEN** the contributor SHALL verify `tdt-meta/AGENTS.md` parses correctly in the new tool (per v1.1 graceful-degradation guarantee)

#### Scenario: Tool reports parse failure
- **WHEN** an AI agent tool reports a parse failure on `tdt-meta/AGENTS.md`
- **THEN** the contributor SHALL:
  1. Check that no tool-specific extensions (e.g., `.claude/rules/` paths) leak into the standard file
  2. Verify HTML-comment fences (`<!-- agents:module -->` open + close) are balanced
  3. Confirm no non-standard Markdown extensions (e.g., custom directives) are used

### Requirement: Symlink topology is preserved

The workspace symlinks — `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.agents`, `docs`, `openspec`, `tools` — SHALL all resolve to their canonical counterparts in `tdt-meta/`. Adding new instruction files MUST NOT introduce a new symlink or break an existing one.

#### Scenario: New instruction file is added
- **WHEN** a contributor adds a new top-level instruction file (e.g., `.cursorrules`, `.aider.conf.yml`)
- **THEN** the contributor SHALL either (a) symlink it to the canonical file in `tdt-meta/`, or (b) document in the file why it must be a standalone file

#### Scenario: Symlink breaks
- **WHEN** a sub-repo's `.agents/modules/<file>.md` symlink target is moved or deleted in `tdt-meta/.agents/modules/`
- **THEN** all broken symlinks SHALL be detected by `readlink -f` returning non-zero, and the install-modules.sh script SHALL be re-run to repair

### Requirement: Emphasis budget

The root `tdt-meta/AGENTS.md` file MUST NOT contain more than **5 `MUST` markers** (case-insensitive) outside code blocks and tables.

#### Scenario: New MUST marker is added
- **WHEN** a contributor adds a new rule they consider non-negotiable
- **THEN** the contributor SHALL first check whether an existing `MUST` already covers it; if not, they SHALL use imperative phrasing (`Use X` / `Do not X`) unless the rule is one of the canonical non-negotiables (AGENTS.md symlink, tdt_core factories, secrets in `~/.tdt/.env`)

#### Scenario: Emphasis audit
- **WHEN** the quarterly review detects >5 `MUST` markers
- **THEN** the reviewer SHALL demote the least load-bearing markers to imperative phrasing

### Requirement: Quarterly review cadence

A review of `tdt-meta/AGENTS.md` and `tdt-meta/.agents/modules/` SHALL be conducted at least once per calendar quarter. The review SHALL check:

1. Line count of root AGENTS.md (target: ≤150).
2. Emphasis budget (target: ≤5 `MUST` markers outside code blocks).
3. Stale references (links that no longer resolve).
4. Module trigger keyword coverage (each module has 3-5 keywords).
5. Definition of Done commands still exit 0 on a clean tree.
6. Escalation Rules Never list matches current ops policy.
7. Symlink integrity (`readlink -f` returns valid file in every sub-repo).
8. YAML frontmatter validity (every file with frontmatter parses).
9. Anti-patterns (grep for "be careful", "where possible", "gracefully" → expect near-zero).

#### Scenario: Review identifies bloat
- **WHEN** the quarterly review finds `tdt-meta/AGENTS.md` exceeds 150 lines
- **THEN** the reviewer SHALL open an OpenSpec change to slim it

#### Scenario: Review identifies broken symlinks
- **WHEN** the quarterly review finds any symlink in a sub-repo's `.agents/modules/` is broken
- **THEN** the reviewer SHALL either fix the symlink target or remove the symlink

## Verification

- `wc -l tdt-meta/AGENTS.md` reports ≤150.
- `grep -ic 'MUST' tdt-meta/AGENTS.md` reports ≤5 (outside code blocks).
- `ls -la $HOME/Developer/tdt/AGENTS.md` shows symlink to `tdt-meta/AGENTS.md`.
- `ls -la $HOME/Developer/tdt/CLAUDE.md` shows symlink to `tdt-meta/AGENTS.md`.
- Every section in the mandatory list is present in `tdt-meta/AGENTS.md`.
- Every module file in `tdt-meta/.agents/modules/` is referenced in the root module index.
- The root module index uses balanced `<!-- agents:module -->` fences.
- Every module entry has 3-5 trigger keywords and a description.
- `## Definition of Done` has ≥4 verifiable exit-code commands.
- `## Escalation Rules` has ≥3 escalation paths and ≥4 explicit Never rules.
- Every actionable instruction in root + modules follows the command-first pattern.
- For every sub-repo in `tdt-meta/scripts/install-modules.sh`, `ls -la <repo>/.agents/modules/` shows symlinks resolving to canonical files.
- `openspec validate --strict agents-md-slim-and-rules-scoping` passes.
- A representative task in Codex CLI, Cursor, or Amp renders the module index as a readable Markdown list (graceful degradation works).