# Exploration Report: Local GitHub Actions Validation CLI, Agent Skills, and Pre-Flight Prevention

**Date:** 2026-10-04  
**Workspace:** `~/Developer/platform/go-microservices`  
**OpenSpec Store:** `~/Developer/platform/openspec-store`  
**Current Baseline Commit on `main`:** `0b58aed` (PR #51)  

---

## 1. Executive Summary & Root-Cause Problem Statement

Over PRs #43 through #51, the `go-microservices` CI/CD infrastructure achieved high execution speed (reducing monolithic runtime from 23m down to ~8m via a 4-tier parallel matrix DAG), toolchain single-source-of-truth (`.go-version`), and automated coverage documentation synchronization.

However, an operational gap remains in the **developer and autonomous agent feedback loop**:
- The local developer pre-push gate (`make pre-push` / `.githooks/pre-push`) currently executes:
  1. `git diff --check` (whitespace and conflict markers)
  2. `make validate-agent-guidance` (layered `AGENTS.md` word bounds)
  3. `python3 scripts/sync-coverage-docs.py --check` (coverage documentation drift)
  4. `make validate-documentation` (doccheck inventories and link integrity)
- **The Gap:** `make pre-push` **does not validate GitHub Actions workflow modifications**.
  - If an engineer or agent modifies `.github/workflows/*.yml`—introducing syntax errors, unpinned actions, retention day deviations, malformed expression contexts, invalid trigger events, or accidentally renaming the branch protection anchor `PR gate (verify-pr)`—`make pre-push` passes cleanly locally.
  - The error is only discovered after pushing to GitHub and waiting for the remote runner, triggering unnecessary back-and-forth PR fix cycles (as experienced during earlier iterations with retention array matching and doccheck arguments).

To establish a zero-drift, first-time-green delivery protocol, the workspace requires:
1. A unified, deterministic **local workflow validation CLI tool** (`scripts/validate-workflows.py`) wired directly into `Makefile` and `make pre-push`.
2. A formal **Agent Skill** (`github-actions-validation`) providing autonomous coding agents with clear procedural rules, CLI commands, and pre-flight validation checklists.

---

## 2. Technical Evaluation of GitHub Actions Validation Tooling

Our research across the modern GitHub Actions ecosystem evaluated three distinct validation strategies:

### A. Static AST Linting (`actionlint` + `shellcheck`)
- **Mechanism:** Parses workflow YAML into an Abstract Syntax Tree (AST), checking `${{ ... }}` expression syntax, context types (`matrix`, `steps`, `needs`, `env`), runner matrix validity, and parameter schemas for popular actions.
- **Embedded Shellcheck:** Extracts inline `run:` bash blocks and runs `shellcheck` against them.
- **Performance:** Sub-second execution (< 0.5s for all 13 monorepo workflows).
- **Workstation Status:** Installed at `/opt/homebrew/bin/actionlint` (v1.7.12) with `/opt/homebrew/bin/shellcheck`.

### B. Security & Supply Chain Auditing (`zizmor` + `tools/actionpin`)
- **`tools/actionpin`:** Repository-internal Python tool enforcing that every third-party remote action is pinned to an immutable 40-character commit SHA matching `verification/github-actions-lock.json`.
- **`zizmor`:** Specialized security scanner auditing workflows for secrets exfiltration, unpinned actions, and credential persistence (`artipacked`).
- **Performance:** ~0.3s for `actionpin`; ~0.5s for `zizmor` in offline mode.
- **Workstation Status:** Both tools verified and functional.

### C. Structural & Monorepo Contract Auditing (`scripts/verify-retention.py` + Invariants)
- **`verify-retention.py`:** Enforces that artifact retention periods are not silently lowered or corrupted against `origin/main`.
- **Branch Protection Invariants:** Enforces that the required status check context `PR gate (verify-pr)` remains intact in `verify.yml`.
- **Concurrency & Trigger Invariants:** Enforces standard PR concurrency (`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`) and explicit trigger types (`[opened, synchronize, reopened]`).

---

## 3. Architecture of the Unified Local CLI (`scripts/validate-workflows.py`)

Rather than expecting developers or autonomous agents to remember to execute 5 separate scripts with varying arguments, we propose creating a unified Python CLI tool `scripts/validate-workflows.py` that executes an 8-point check suite:

```
[Developer or Pre-Push Hook]
             │
             ▼
   make validate-workflows
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ scripts/validate-workflows.py                               │
├─────────────────────────────────────────────────────────────┤
│ 1. Structural YAML Parsing & Duplicate Key Check            │
│ 2. actionlint AST & Shellcheck Linting                      │
│ 3. tools/actionpin Commit SHA Lockfile Verification         │
│ 4. scripts/verify-retention.py Baseline Enforcement         │
│ 5. Branch Protection Check Name Invariant Check             │
│    (Ensures "PR gate (verify-pr)" anchor is present)        │
│ 6. PR-Scoped Concurrency Configuration Verification         │
│ 7. Explicit PR Trigger Lifecycle Verification               │
│ 8. Optional zizmor Security Audit (offline mode)            │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points
- **Makefile:** Add `validate-workflows` target and integrate it into `pre-push`:
  ```makefile
  .PHONY: pre-push
  pre-push:
  	git diff --check
  	$(MAKE) validate-agent-guidance
  	$(MAKE) validate-workflows
  	python3 scripts/sync-coverage-docs.py --check
  	$(MAKE) validate-documentation
  ```
- **Local Hook:** `.githooks/pre-push` immediately inherits this gate, guaranteeing that no developer or agent can push a broken workflow file to GitHub.

---

## 4. Reusable Agent Skill Design (`github-actions-validation`)

To make this capability discoverable and executable across autonomous agents (Hermes, Claude Code, Codex, Pi, Goose):
- Standardized skill structure under `.agents/skills/github-actions-validation/SKILL.md`.
- Symlinked into `~/.agents/skills/` and `~/.hermes/skills/` via `sync-workspace-agent-skills.py`.
- Encodes:
  - 5-stage pre-flight checklist.
  - Command reference (`make validate-workflows`, `actionlint`, `tools/actionpin`).
  - Known failure modes & root causes (read-only module tar permissions, loopback endpoints in Newman CI, retention list matching, doccheck evidence flags).

---

## 5. Recommendation & Roadmap

Initiate OpenSpec change:
- **Change Name:** `implement-github-actions-local-validation-cli-and-skill`
- **Scope:**
  1. Author `scripts/validate-workflows.py` in `go-microservices`.
  2. Wire `validate-workflows` into `Makefile` and `make pre-push`.
  3. Author `.agents/skills/github-actions-validation/SKILL.md` and synchronize.
  4. Update `docs/runbooks/ci-cd-operations.md` and `docs/README.md`.
  5. Validate via `make pre-push` and land via GitHub Pull Request.
