# Design: Enhance Agent Instructions

## Context

The repository has 6 validated AGENTS.md files (root + 5 subdirectories) that
all pass agentguide validation (60 checks, 0 violations). Word limits are
200–550 for root and 120–550 for sub-guides. Current usage: root 423 words.

Modern AGENTS.md best practices (agentsmd/agents.md spec, Airflow, GitHub
Copilot docs, Claude Code memory docs) recommend these sections that our
files currently lack.

## Current → Proposed

### Root AGENTS.md (Section 1: Add Project Overview)

**Current:** File opens with "Repository Guidelines" heading and "Scope and
Instruction Precedence" — no indication of what the repository IS.

**Proposed:** Add a 2-line project summary after the H1:
```
# Repository Guidelines

Go microservices monorepo: 8 independently deployable services, shared platform
module, PostgreSQL, Kafka, Debezium CDC, Temporal, Redis, OTLP observability.
```

**Why:** The agents.md spec, Airflow, and GitHub's recommended template all
start with project purpose. An agent seeing this file for the first time needs
to know the tech stack to make correct decisions.

### Root AGENTS.md (Section 2: Add Prerequisites)

**Current:** No mention of required tools. Agents must guess from Make targets.

**Proposed:** Add a compact prerequisites list:
```
## Prerequisites
Go 1.26.5 (arm64 Mac, Homebrew), Docker Desktop, kind v0.32.0, `openspec` CLI,
graphify v0.9.26. Docker credsStore: osxkeychain.
```

**Why:** Airflow's AGENTS.md lists `uv tool install prek` and `prek install`.
Without prerequisites, agents may attempt builds before tools are available.

### Root AGENTS.md (Section 3: Replace Stale Commit Text)

**Current:** "The outer repository has no commit history yet. Until a convention
is established, use short imperative subjects..."

**Proposed:** Replace with established convention and format:
```
## Commits and Pull Requests

Use Conventional Commits: `<type>(<scope>): <description>`.
Types: feat, fix, refactor, test, docs, chore, ci.
Scope: service name or module (e.g., `order`, `platform/kafka`, `deploy`).
```

**Why:** 6 PRs have been merged. The "no history" text is misleading.

### Root AGENTS.md (Section 4: Add Navigation Table)

**Current:** Sub-directory guides are mentioned generically but not listed.

**Proposed:** Add a compact navigation table:
```
## Agent Instruction Files
| Path | Governs |
|---|---|
| `platform/` | Shared Go module, API contracts |
| `services/` | Service architecture, testing |
| `deploy/` | Compose, kind, Kubernetes, Argo CD |
| `openspec/` | Spec-driven workflow |
| `scripts/` | Shell safety, validation |
```

**Why:** Modern practice (Airflow, agents.md spec) recommends explicit
navigation for monorepo instruction files.

### Root AGENTS.md (Section 5: Add Pitfalls)

**Current:** Known gotchas are in memory but not in any AGENTS.md.

**Proposed:** Add a compact pitfalls section with the highest-impact items:
```
## Common Pitfalls
- Integration tests require `-tags integration` build tag
- Docker compose targeted builds fail — use `docker build` directly
- Redis cluster: CONFIG is disabled; verify via YAML/SLOWLOG/ACL, not CONFIG GET
- Run `make preflight` before any deployment work
```

**Why:** Airflow and GitHub Copilot templates recommend explicit anti-pattern
lists. These 4 items are the most frequently encountered.

### Root CLAUDE.md (Reconcile for Portability)

**Current:** Contains only graphify instructions (772 bytes). Diverges from
AGENTS.md. Claude Code loads CLAUDE.md (cwd-only), not AGENTS.md.

**Proposed:** Add `@AGENTS.md` import at the top, keep graphify below:
```
@AGENTS.md

## graphify
[existing content]
```

**Why:** Claude Code supports `@path` imports. This ensures Claude Code reads
the same core instructions as Hermes/Codex/Cursor without duplicating content.

### tools/agentguide/mcp-router.AGENTS.md (Remove Orphan)

**Current:** 3.5KB guide in `tools/agentguide/` but the actual mcp-router
repo at `~/Developer/mcp-router/` has no AGENTS.md.

**Proposed:** Remove the orphaned file. The mcp-router repo should have its
own AGENTS.md if needed, but that's a separate concern.

**Why:** Dead content that no agent will ever load. The mcp-router is a
separate git repository, not part of this monorepo.

## Verification

1. `make validate-agent-guidance` — all 6 guides must pass (0 violations)
2. Word count check: root must stay within 200–550 words
3. `openspec validate enhance-agent-instructions --store openspec-store`
4. Manual review of CLAUDE.md import syntax
