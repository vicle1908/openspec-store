# Design: 5-Provider Review Gates (Alignment Focus) — REVISED v2

## The Alignment Problem

```
┌─────────────────────────────────────────────────────────────────┐
│                    ALIGNMENT MATRIX (8 EDGES)                   │
│                                                                 │
│    Specs ←→ Code ←→ Docs ←→ Skills ←→ Specs                    │
│      │        │       │        │        │                       │
│      └────────┴───────┴────────┴────────┘                       │
│                    │                                            │
│    Tests ←───────┘──────┘                                       │
│                                                                 │
│         5-Provider Review checks all edges                      │
│         Security is a LENS (Claude Code), not an edge           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Four artifacts, eight alignment edges:**

| Edge | What Drifts | Example |
|---|---|---|
| **Spec ↔ Code** | Requirements not implemented | Spec says "MUST timeout after 30min", code uses 60min |
| **Code ↔ Docs** | Implementation differs from docs | AGENTS.md says "use pytest", code uses unittest |
| **Docs ↔ Skills** | Skills reference outdated patterns | Skill says `openspec validate --change`, CLI uses `openspec validate <name>` |
| **Skills ↔ Specs** | Skills implement workflows not in specs | Skill has 5-step process, spec describes 3-step |
| **Spec ↔ Docs** | Documentation doesn't match specs | Spec requires "SHALL log all errors", docs don't mention logging |
| **Code ↔ Skills** | Skills assume code patterns that changed | Skill imports from old module path |
| **Spec ↔ Tests** | Requirements not tested | Spec says "MUST handle timeout", no test for timeout |
| **Code ↔ Tests** | Implementation not tested | Code has error handling but no test for error path |

**Security is a review LENS applied across all edges, not a separate edge.**

## Trust Boundary (Enforced, Not Just Prompted)

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRUST BOUNDARY                               │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ Orchestrator  │    │ Sanitized    │    │ Reviewers    │     │
│  │ (Hermes)      │───▶│ Context      │───▶│ (Capability- │     │
│  │               │    │ Bundle       │    │  Enforced)   │     │
│  │ - Reads files │    │              │    │              │     │
│  │ - Writes report│   │ - Allowlisted│    │ - No write   │     │
│  │ - Runs tests  │    │ - Redacted   │    │ - No shell   │     │
│  │               │    │ - Immutable  │    │ - No network │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                 │
│  Enforcement Mechanisms:                                       │
│  1. delegate_task with read-only constraints                   │
│  2. Context bundle is pre-collected (not live filesystem)      │
│  3. Reviewers receive string data, not file paths              │
│  4. Orchestrator validates outputs before writing              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Enforcement Mechanisms

| Constraint | How Enforced |
|---|---|
| **Read-only** | `delegate_task` with no write tools; reviewers receive string data |
| **No shell** | Orchestrator runs tests; reviewers only see results |
| **No network** | Reviewers receive pre-collected context, no API access |
| **No nested agents** | `delegate_task` depth limit; reviewers cannot spawn |
| **No credentials** | Context bundle excludes `.env`, keychains, API keys |
| **Scoped data** | Only allowlisted files included in context bundle |

### Context Bundle (Pre-Collected by Orchestrator)

```yaml
# review-scope.yaml (per change)
change_name: add-dark-mode
repositories:
  - path: ~/Developer/agent-core
    base: origin/main
    head: HEAD
    test_command: "uv run pytest --cov"
specs:
  - hermes-skills/spec.md
  - ui/spec.md
docs:
  - AGENTS.md
  - README.md
skills:
  - openspec-workflow
  - claude-code
excluded:
  - .env
  - .git/
  - __pycache__/
coverage_threshold: 80
```

**Orchestrator collects:**
1. Read change artifacts via `openspec status --change <name> --json`
2. Read context files from `openspec instructions apply --json`
3. Run tests and collect coverage: `uv run pytest --cov` or `make check-coverage`
4. Run linting: `uv run ruff check` or `gofmt`
5. Bundle all results as string data (not file paths)
6. Validate no secrets in bundle
7. Spawn reviewers with string data only

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HERMES ORCHESTRATOR                          │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ 1. Read      │    │ 2. Collect   │    │ 3. Run Tests │     │
│  │ Scope &      │───▶│ Context      │───▶│ & Lint       │     │
│  │ Artifacts    │    │ Bundle       │    │              │     │
│  └──────────────┘    └──────────────┘    └──────┬───────┘     │
│                                                 │              │
│                                                 ▼              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ 4. Validate  │    │ 5. Spawn     │    │ 6. Write     │     │
│  │ Bundle       │───▶│ Reviewers    │───▶│ Report       │     │
│  │ (no secrets) │    │ (5 parallel) │    │              │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Provider Review Lenses (Consistent Across Gates)

| Provider | Lens | Plan Review Focus | Code Review Focus |
|---|---|---|---|
| **Hermes** | Spec compliance | Spec ↔ Code, Spec ↔ Docs, Spec ↔ Tests | Spec ↔ Code, Spec ↔ Tests |
| **Claude Code** | Security | Security checks across all edges | Security audit across all edges |
| **Codex** | Quality & tests | Spec ↔ Tests, Code ↔ Tests | Code ↔ Tests, Code ↔ Docs |
| **Antigravity** | Architecture | Code ↔ Skills, Docs ↔ Skills | Code ↔ Skills, Architecture adherence |
| **fable-5** | Product scope | Skills ↔ Specs, scope check | Skills ↔ Specs, completeness |

### Security Lens (Applied Across All Edges)

Claude Code's security lens is NOT a separate edge. It is applied to every edge:

| Edge | Security Check |
|---|---|
| Spec ↔ Code | Are security requirements implemented? |
| Code ↔ Docs | Are security patterns documented? |
| Docs ↔ Skills | Do skills follow security practices? |
| Skills ↔ Specs | Do skills implement security requirements? |
| Spec ↔ Docs | Are security requirements documented? |
| Code ↔ Skills | Do skills use secure APIs? |
| Spec ↔ Tests | Are security scenarios tested? |
| Code ↔ Tests | Are security controls tested? |

## Status Semantics

| Status | Meaning | When to Use |
|---|---|---|
| `PASS` | Evidence confirms alignment | All checks pass with evidence |
| `PARTIAL` | Some evidence, gaps remain | Some checks pass, some missing |
| `FAIL` | Evidence shows misalignment | Direct conflict found |
| `N/A` | Edge not applicable | Change doesn't touch this edge |
| `UNKNOWN` | Could not verify | Insufficient data or provider failure |
| `NOT_REVIEWED` | Provider did not cover | Edge outside provider's scope |

### Consensus Rules

- **Critical finding**: One provider finding = CRITICAL until disproved
- **Majority**: 3+ providers agree = consensus
- **Minority**: 1-2 providers = minority report
- **Conflict**: Providers disagree = flag for human review

### Summary Rules

Workflow summaries MUST include all possible statuses:

```
PASS: X
PARTIAL: X
FAIL: X
N/A: X
UNKNOWN: X
NOT_REVIEWED: X
```

Never collapse UNKNOWN or NOT_REVIEWED into other statuses.

## Evidence Collection

### Orchestrator Responsibilities

The orchestrator (Hermes) is responsible for evidence collection:

```bash
# Python repos
uv run pytest --cov --cov-report=term-missing
uv run ruff check src/ tests/
uv run mypy src/ --strict

# Go repos
make verify-pr
make check-coverage

# OpenSpec
openspec validate --strict
openspec status --change <name> --json
```

### Evidence Record Format

Each evidence record includes:

```yaml
evidence:
  type: test_run | lint | spec_check | manual
  repository: ~/Developer/agent-core
  command: "uv run pytest --cov"
  working_directory: ~/Developer/agent-core
  base_revision: abc1234
  head_revision: def5678
  exit_code: 0
  timestamp: 2026-08-04T06:50:00+07:00
  tool_version: "pytest-8.3.0"
  output_artifact: /tmp/coverage-report.txt
  status: collected | skipped | blocked | unavailable
```

### Status Determination

| Condition | Status |
|---|---|
| Test passes, coverage ≥ threshold | `PASS` |
| Test passes, coverage < threshold | `PARTIAL` |
| Test fails | `FAIL` |
| Test command not available | `UNKNOWN` |
| Test skipped by scope | `N/A` |
| Provider timeout | `NOT_REVIEWED` |

## Skill Implementation

### Skill 1: `openspec-plan-review` (Alignment-Focused, Revised v2)

**Location:** `~/.hermes/skills/openspec-workflow/openspec-plan-review/SKILL.md`

**Workflow:**
1. Accept change name as argument
2. Read `review-scope.yaml` for scope definition
3. Validate scope (reject escapes, symlinks, malformed files)
4. Read change artifacts via `openspec status --change <name> --json`
5. Read context files from `openspec instructions apply --json`
6. Run tests and collect coverage (orchestrator responsibility)
7. Run linting (orchestrator responsibility)
8. Bundle all results as string data
9. Validate no secrets in bundle
10. Spawn 5 parallel `delegate_task` subagents with string data
11. Each subagent checks assigned alignment edges
12. Consolidate feedback with all statuses (PASS/PARTIAL/FAIL/N/A/UNKNOWN/NOT_REVIEWED)
13. Write `review-plan.md` with evidence records
14. Report summary with all status counts

### Skill 2: `openspec-code-review` (Alignment-Focused, Revised v2)

**Location:** `~/.hermes/skills/openspec-workflow/openspec-code-review/SKILL.md`

**Workflow:**
1. Accept change name as argument
2. Read `review-scope.yaml` for scope definition
3. Validate scope (reject escapes, symlinks, malformed files)
4. Read change artifacts and git diff
5. Read existing docs, skills, and specs for context
6. Run tests and collect coverage (orchestrator responsibility)
7. Run linting (orchestrator responsibility)
8. Bundle all results as string data
9. Validate no secrets in bundle
10. Spawn 5 parallel `delegate_task` subagents with string data
11. Each subagent checks assigned alignment edges
12. Consolidate feedback with all statuses (PASS/PARTIAL/FAIL/N/A/UNKNOWN/NOT_REVIEWED)
13. Write `review-code.md` with evidence records
14. Report summary with all status counts

## Output Format

### review-plan.md (Alignment Matrix, Revised v2)

```markdown
# Plan Review: {CHANGE_NAME}

**Reviewed:** {TIMESTAMP}
**Providers:** Hermes, Claude Code, Codex, Antigravity, fable-5
**Scope:** {REVIEW_SCOPE}

## Alignment Summary

| Edge | Status | Provider | Evidence |
|---|---|---|---|
| Spec ↔ Code | {STATUS} | Hermes | {EVIDENCE} |
| Code ↔ Docs | {STATUS} | Codex | {EVIDENCE} |
| Docs ↔ Skills | {STATUS} | Antigravity | {EVIDENCE} |
| Skills ↔ Specs | {STATUS} | fable-5 | {EVIDENCE} |
| Spec ↔ Docs | {STATUS} | Hermes | {EVIDENCE} |
| Code ↔ Skills | {STATUS} | Antigravity | {EVIDENCE} |
| Spec ↔ Tests | {STATUS} | Codex | {EVIDENCE} |
| Code ↔ Tests | {STATUS} | Codex | {EVIDENCE} |

### Security Lens (Applied Across All Edges)

| Edge | Security Status | Provider | Evidence |
|---|---|---|---|
| Spec ↔ Code | {STATUS} | Claude Code | {EVIDENCE} |
| Code ↔ Docs | {STATUS} | Claude Code | {EVIDENCE} |
| ... | ... | ... | ... |

## Status Counts

- PASS: {X}
- PARTIAL: {X}
- FAIL: {X}
- N/A: {X}
- UNKNOWN: {X}
- NOT_REVIEWED: {X}

## Evidence Records

{EVIDENCE_RECORDS}
```

## Integration Points

### Workflow Position

```
/opsx:explore → /opsx:propose → PLAN_REVIEW → /opsx:apply → CODE_REVIEW → /opsx:verify → /opsx:archive
                   │                │              │              │              │
                   │                │              │              │              │
                   ▼                ▼              ▼              ▼              ▼
              Artifacts      Alignment      Code changes   Alignment      Verify
                            Matrix (8 edges)             Matrix (8 edges)
```

### Usage

```bash
# After propose, before apply
/openspec-plan-review add-dark-mode

# After apply, before verify/archive
/openspec-code-review add-dark-mode
```

### Relationship to /opsx:verify

- `/opsx:verify` = single-agent, quick alignment check
- `openspec-code-review` = 5-provider, deep alignment analysis

Use `/opsx:verify` for routine changes. Use `openspec-code-review` for changes that touch multiple repos or have complex alignment requirements.

## Non-Functional Requirements

- **Performance:** 5 providers run in parallel, total time ≈ slowest provider
- **Reliability:** Each provider failure is isolated; 4/5 providers still produce useful review
- **Usability:** Skills are invoked via simple command, no configuration needed
- **Maintainability:** Review prompts are templated, easy to adjust per provider
- **Observability:** Alignment matrix is structured, machine-readable, human-friendly
- **Security:** Reviewers are capability-enforced read-only, context is sanitized, credentials are excluded

## Tradeoffs

| Decision | Rationale |
|---|---|
| Two skills (plan + code) | Different contexts, different prompts, user choice |
| Parallel execution | Faster than sequential; providers are independent |
| Alignment matrix output | Clear visualization of drift across 4 artifacts |
| Manual invocation | User controls when review happens; not forced on all changes |
| No auto-fix | Review reports issues, human decides how to fix |
| Capability-enforced trust boundary | Not just prompt-enforced; actual constraints |
| Orchestrator evidence collection | Tests/lint run by orchestrator, not reviewers |
| All statuses in summary | Never collapse UNKNOWN/NOT_REVIEWED |
| Security as lens, not edge | Applied across all edges, not separate |
