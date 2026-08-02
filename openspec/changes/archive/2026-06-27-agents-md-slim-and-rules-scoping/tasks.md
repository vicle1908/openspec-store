# AGENTS.md Slim-Down + Standard-Compliant Modules — Tasks

Total estimate: **~8 hours**, fits in a single session.

## 1. Setup (~15 min)

= [x] 1.1 Confirm current `wc -l tdt-meta/AGENTS.md` baseline (expected: 322). ~2 min
= [x] 1.2 Verify `claude --version` ≥ 2.1.59 (auto-memory support). ~1 min
= [x] 1.3 Verify AGENTS.md v1.1 spec is current (check Linux Foundation AAIF site). ~2 min
= [x] 1.4 Create `tdt-meta/.agents/modules/` directory. ~2 min
= [x] 1.5 Run `gitnexus status -r tdt-meta` to confirm clean index. ~5 min
= [x] 1.6 List target sub-repos for module distribution: webhook-receiver, ai-review, tdt-core, poems-mobile3-ios, poems-mobile3-android, agent-core, qi-bridge, mcp-router, jira-skill, tdt-sheets, code-daily-scan. ~3 min

## 2. Create modules directory + README (~20 min)

= [x] 2.1 Create `tdt-meta/.agents/modules/`. ~1 min
= [x] 2.2 Write `tdt-meta/.agents/modules/README.md` with:
  - Purpose: task-organized modules distributed via symlinks.
  - AGENTS.md v1.1 module index format.
  - Command-first pattern requirement.
  - Trigger keyword guidelines (3-5 per module, case-insensitive).
  - How to add a new module (edit file + add index entry + run install script). ~15 min
= [x] 2.3 Verify all module files have valid YAML frontmatter if present (Python `yaml.safe_load`). ~4 min

## 3. Write task-organized modules (~3 hours)

### 3.1 Module: `coding.md` (~30 min)

= [x] Write `.agents/modules/coding.md` — "When writing code".
  - **Triggers**: coding, edit, write, implement, refactor.
  - Content: pre-edit checks (`gitnexus_impact`), commit conventions, linter/typecheck commands.
  - Apply command-first pattern to every instruction.
= [x] Verify YAML frontmatter (optional) parses.
= [x] Confirm module size ≤80 lines.

### 3.2 Module: `review.md` (~25 min)

= [x] Write `.agents/modules/review.md` — "When reviewing code".
  - **Triggers**: review, pr, merge, lint.
  - Content: review checklist, lint/typecheck commands, security scan.
= [x] Confirm module size ≤60 lines.

### 3.3 Module: `release.md` (~25 min)

= [x] Write `.agents/modules/release.md` — "When releasing".
  - **Triggers**: release, deploy, tag, version.
  - Content: version bump, deploy script invocation, smoke test commands.
= [x] Confirm module size ≤60 lines.

### 3.4 Module: `mcp-router.md` (~30 min)

= [x] Write `.agents/modules/mcp-router.md` — MCP router tool selection.
  - **Triggers**: router, mcp, tavily, exa, brave, context7, gitnexus, deepwiki.
  - Content: capability matrix, fallback rules, auth invariants (preserve verbatim from current AGENTS.md).
= [x] Confirm module size ≤80 lines.

### 3.5 Module: `jira-skills.md` (~25 min)

= [x] Write `.agents/modules/jira-skills.md` — Jira skill routing.
  - **Triggers**: jira, sprint, ticket, jql, kanban, daily report.
  - Content: skill catalog table + Jira URL shortcut (preserve verbatim).
= [x] Confirm module size ≤70 lines.

### 3.6 Module: `openspec.md` (~30 min)

= [x] Write `.agents/modules/openspec.md` — OpenSpec workflows.
  - **Triggers**: openspec, change, propose, apply, archive, /opsx.
  - Content: 10-workflow list, when-to-use, conventions (preserve verbatim).
= [x] Confirm module size ≤80 lines.

### 3.7 Module: `webhook.md` (~25 min)

= [x] Write `.agents/modules/webhook.md` — webhook-receiver state + ops.
  - **Triggers**: webhook, dedupe, dlq, ngrok, tailscale, selftest.
  - Content: state file table, deploy command, failover runbook reference (preserve verbatim).
= [x] Confirm module size ≤70 lines.

### 3.8 Module: `code-intel.md` (~30 min)

= [x] Write `.agents/modules/code-intel.md` — GitNexus impact + detect_changes.
  - **Triggers**: gitnexus, impact, detect_changes, cypher, query.
  - Content: Always Do / Never Do block (preserve `<!-- gitnexus:start/end -->` markers verbatim).
= [x] Confirm module size ≤80 lines.

### 3.9 Module: `ecc.md` (~25 min)

= [x] Write `.agents/modules/ecc.md` — ECC harness disposition.
  - **Triggers**: ecc, everything-claude-code, hooks, audit.
  - Content: ECC_DISABLED_HOOKS reference, audit paths, marketplace baseline.
= [x] Confirm module size ≤60 lines.

### 3.10 Module: `skills.md` (~20 min)

= [x] Write `.agents/modules/skills.md` — Skills catalog (auth, sheets).
  - **Triggers**: skill, tdt-sheets, service account.
  - Content: auth invariants, SheetsClient pattern, skill count + index reference.
= [x] Confirm module size ≤40 lines.

## 4. Rewrite root AGENTS.md (~60 min)

= [x] 4.1 Write new root `tdt-meta/AGENTS.md` from scratch (~134 lines).
  - Header: `# TDT — Agent Instructions`, version, last-updated date. ~6 lines
  - `## Definition of Done` (table of ≥4 exit-code checks). ~10 lines
  - `## Escalation Rules` (When Blocked + Never list). ~12 lines
  - `## Workspace Layout` (repos, symlinks). ~10 lines
  - `## Environment & Secrets` (tdt_core, ~/.tdt/.env). ~8 lines
  - `## Build & Test Commands` (per-repo commands with flags). ~12 lines
  - `## Git Workflow` (branch, commit, PR). ~10 lines
  - `## Testing` (pytest, locations). ~8 lines
  - `## Skills Catalog` (103 skills, 1-line pointer to SKILLS_INDEX.md). ~6 lines
  - `## MCP Routing (Preferred)` (1-line summary + cross-link). ~6 lines
  - `## Code Intelligence` (1-line summary + cross-link). ~5 lines
  - `## OpenSpec Workflows` (1-line summary + cross-link). ~5 lines
  - `## Boundaries` (never-touch lists). ~10 lines
  - `## Principles` (numbered with rationale). ~14 lines
  - `## Module Index` (with `<!-- agents:module -->` fences). ~14 lines
= [x] 4.2 Verify `wc -l` reports ≤150. ~2 min
= [x] 4.3 Verify `MUST` count ≤5. ~2 min
= [x] 4.4 Verify no anti-patterns remain: grep "be careful", "where possible", "gracefully" → expect 0 matches. ~2 min
= [x] 4.5 Verify module index uses balanced HTML-comment fences. ~2 min

## 5. Demote emphasis (~15 min)

= [x] 5.1 Reduce `MUST` markers to 3 (AGENTS.md symlink, tdt_core factories, secrets). ~10 min
= [x] 5.2 Replace remaining MUST/SHALL/IMPORTANT with imperative phrasing. ~5 min

## 6. Create install-modules.sh (~25 min)

= [x] 6.1 Write `tdt-meta/scripts/install-modules.sh`:
  ```bash
  #!/usr/bin/env bash
  # Symlink shared AGENTS.md v1.1 modules into each sub-repo's .agents/modules/.
  set -euo pipefail

  SHARED="$HOME/Developer/tdt/tdt-meta/.agents/modules"
  REPOS=(webhook-receiver ai-review tdt-core poems-mobile3-ios poems-mobile3-android
         agent-core qi-bridge mcp-router jira-skill tdt-sheets code-daily-scan)

  for repo in "${REPOS[@]}"; do
      REPO_DIR="$HOME/Developer/tdt/$repo"
      TARGET="$REPO_DIR/.agents/modules"
      if [ ! -d "$REPO_DIR" ]; then
          echo "SKIP: $repo (not present)"
          continue
      fi
      mkdir -p "$TARGET"
      for module in "$SHARED"/*.md; do
          ln -sf "$module" "$TARGET/$(basename "$module")"
      done
      echo "OK: $repo -> $(ls -1 "$TARGET" | wc -l | tr -d ' ') modules"
  done
  ```
= [x] 6.2 Make executable: `chmod +x tdt-meta/scripts/install-modules.sh`. ~1 min
= [x] 6.3 Run the script and verify all sub-repos get the modules. ~4 min

## 7. Verify symlinks + end-to-end (~60 min)

= [x] 7.1 For each sub-repo, verify `.agents/modules/` exists and symlinks resolve. ~10 min
  ```bash
  for repo in webhook-receiver ai-review tdt-core poems-mobile3-ios poems-mobile3-android; do
      for link in "$HOME/Developer/tdt/$repo/.agents/modules/"*.md; do
          [ -L "$link" ] && readlink -f "$link" || echo "BROKEN: $link"
      done
  done
  ```
= [x] 7.2 Open root `tdt-meta/AGENTS.md` in a non-Claude tool (Amp/Cursor/Codex) and confirm the module index renders as a readable Markdown list (graceful degradation). ~15 min
= [x] 7.3 Run representative tasks: ~30 min
  - **Coding task**: "Add a new state file for X" → verify `coding.md` and `webhook.md` modules load (trigger match).
  - **OpenSpec task**: "Create a new change for Y" → verify `openspec.md` module loads.
  - **Jira task**: "Create a Jira ticket for Z" → verify `jira-skills.md` module loads.
  - **Release task**: "Tag version 1.2.3" → verify `release.md` module loads.
  - For each: confirm Definition of Done commands run and report exit codes.

## 8. Commit + Archive (~20 min)

= [x] 8.1 Run `gitnexus detect_changes` from `tdt-meta`. ~5 min
= [x] 8.2 Commit in `tdt-meta` (NOT from `tdt/`):
  - Commit message: `chore(agents-md): adopt AGENTS.md v1.1 standard with module index (#N)`
  - Files: AGENTS.md, .agents/modules/*, scripts/install-modules.sh
= [x] 8.3 In each sub-repo, commit the new `.agents/modules/` symlinks. ~5 min
= [x] 8.4 Run `/opsx:verify agents-md-slim-and-rules-scoping`. ~3 min
= [x] 8.5 Run `/opsx:archive agents-md-slim-and-rules-scoping`. ~2 min

## Definition of Done

= [x] Root `tdt-meta/AGENTS.md` is ≤150 lines.
= [x] `MUST` count outside code blocks is ≤5.
= [x] Root AGENTS.md follows AGENTS.md v1.1 standard (Linux Foundation AAIF).
= [x] `## Definition of Done` has ≥4 verifiable exit-code commands.
= [x] `## Escalation Rules` has ≥3 escalation paths and ≥4 explicit Never rules.
= [x] `## Module Index` uses balanced `<!-- agents:module -->` HTML-comment fences.
= [x] 10 module files exist in `tdt-meta/.agents/modules/`, each ≤80 lines, each with 3-5 trigger keywords.
= [x] `tdt-meta/scripts/install-modules.sh` exists, is executable, and runs successfully.
= [x] Every sub-repo has `.agents/modules/` with working symlinks to canonical files.
= [x] Every actionable instruction follows the command-first pattern (no anti-patterns).
= [x] 4 representative end-to-end tasks pass (coding, OpenSpec, Jira, release).
= [x] Cross-tool check passes (Amp/Cursor/Codex renders module index as readable Markdown).
= [x] Change is verified and archived.