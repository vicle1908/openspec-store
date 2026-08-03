# Design: 5-Provider Review Gates (Alignment Focus) — REVISED

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

## Trust Boundary

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRUST BOUNDARY                               │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ Orchestrator  │    │ Sanitized    │    │ Reviewers    │     │
│  │ (Hermes)      │───▶│ Context      │───▶│ (Read-Only)  │     │
│  │               │    │ Bundle       │    │              │     │
│  │ - Reads files │    │              │    │ - No write   │     │
│  │ - Writes report│   │ - Allowlisted│    │ - No shell   │     │
│  │               │    │ - Redacted   │    │ - No network │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Reviewer Constraints

| Constraint | Implementation |
|---|---|
| **Read-only** | No write tools, no file creation |
| **No shell** | No bash, no command execution |
| **No network** | No HTTP, no API calls except provider |
| **No nested agents** | No delegate_task, no spawning |
| **No credentials** | No env vars, no keychains |
| **Scoped filesystem** | Only review bundle, not full repo |

### Context Bundle

The orchestrator pre-collects a sanitized context bundle:

```yaml
# review-scope.yaml (per change)
change_name: add-dark-mode
repositories:
  - path: ~/Developer/agent-core
    base: origin/main
    head: HEAD
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
  - node_modules/
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HERMES ORCHESTRATOR                          │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ Read Scope   │    │ Collect      │    │ Spawn        │     │
│  │ & Artifacts  │───▶│ Context      │───▶│ Reviewers    │     │
│  │              │    │ Bundle       │    │ (5 parallel) │     │
│  └──────────────┘    └──────────────┘    └──────┬───────┘     │
│                                                 │              │
│                                                 ▼              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              REVIEWERS (Read-Only)                      │   │
│  │                                                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │  │ Hermes  │ │ Claude  │ │ Codex   │ │ Antigravity│ │ fable-5  │ │
│  │  │ Spec    │ │ Security│ │ Quality │ │ Architecture│ │ Product  │ │
│  │  │ Comp.   │ │ Audit   │ │ Tests   │ │ Patterns   │ │ Scope    │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                 │              │
│                                                 ▼              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              CONSOLIDATE & WRITE                        │   │
│  │              review-plan.md / review-code.md            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Provider Review Lenses (Consistent Across Gates)

| Provider | Lens | Plan Review Focus | Code Review Focus |
|---|---|---|---|
| **Hermes** | Spec compliance | Spec ↔ Code, Spec ↔ Docs, Spec ↔ Tests | Spec ↔ Code, Spec ↔ Tests |
| **Claude Code** | Security | Security alignment (both gates) | Security audit (both gates) |
| **Codex** | Quality & tests | Spec ↔ Tests, Code ↔ Tests | Code ↔ Tests, Code ↔ Docs |
| **Antigravity** | Architecture | Code ↔ Skills, Docs ↔ Skills | Code ↔ Skills, Architecture adherence |
| **fable-5** | Product scope | Skills ↔ Specs, scope check | Skills ↔ Specs, completeness |

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

## Evidence Collection

### For Each Edge

```
1. SPEC CHECK
   - Read delta specs for this change
   - Compare against existing main specs
   - Check for conflicts, gaps, or inconsistencies
   - Evidence: spec IDs, requirement text, scenario text

2. CODE CHECK
   - Read git diff for implementation
   - Compare against spec requirements
   - Check for unimplemented requirements or extra features
   - Evidence: file paths, line numbers, code snippets

3. DOCS CHECK
   - Read AGENTS.md, README.md, skill docs
   - Compare against code patterns
   - Check for outdated instructions or missing documentation
   - Evidence: doc paths, section references, command examples

4. SKILLS CHECK
   - Read relevant Hermes skills
   - Compare against code APIs and patterns
   - Check for broken imports, outdated commands, or missing capabilities
   - Evidence: skill paths, command references, API mappings

5. TESTS CHECK
   - Run `uv run pytest --cov` for Python repos
   - Run `make check-coverage` for Go repos
   - Compare against spec scenarios
   - Check for untested scenarios
   - Evidence: test output, coverage reports, scenario mappings

6. CROSS-CHECK
   - Verify all artifacts are mutually consistent
   - Flag any alignment gaps
   - Suggest fixes for drift
   - Evidence: alignment matrix with status per edge
```

## Skill Implementation

### Skill 1: `openspec-plan-review` (Alignment-Focused, Revised)

**Location:** `~/.hermes/skills/openspec-workflow/openspec-plan-review/SKILL.md`

**Workflow:**
1. Accept change name as argument
2. Read `review-scope.yaml` for scope definition
3. Read change artifacts via `openspec status --change <name> --json`
4. Read context files returned by `openspec instructions apply --json`
5. Collect sanitized context bundle (allowlisted, redacted)
6. Spawn 5 parallel `delegate_task` subagents:
   - Each gets read-only context bundle
   - Each checks assigned alignment edges
   - Each returns structured feedback with status per edge
7. Consolidate feedback into `review-plan.md`
8. Report alignment summary: PASS/PARTIAL/FAIL per edge

**Reviewer Prompt Template:**
```
You are reviewing an OpenSpec change for {LENS}.

IMPORTANT: You are READ-ONLY. Do not write files, execute commands, or spawn agents.

Change: {CHANGE_NAME}
Scope: {REVIEW_SCOPE}

Context Bundle:
{SANITIZED_CONTEXT}

## Alignment Check

### Your Assigned Edges:
{ASSIGNED_EDGES}

### For Each Edge:
1. Read the provided context
2. Check alignment
3. Provide status: PASS, PARTIAL, FAIL, N/A, UNKNOWN, NOT_REVIEWED
4. Provide evidence: file paths, line numbers, specific findings

### Output Format:
For each edge:
- Edge: {EDGE_NAME}
- Status: {STATUS}
- Evidence: {EVIDENCE}
- Findings: {FINDINGS}
```

### Skill 2: `openspec-code-review` (Alignment-Focused, Revised)

**Location:** `~/.hermes/skills/openspec-workflow/openspec-code-review/SKILL.md`

**Workflow:**
1. Accept change name as argument
2. Read `review-scope.yaml` for scope definition
3. Read change artifacts + git diff
4. Read existing docs, skills, and specs for context
5. Collect sanitized context bundle (allowlisted, redacted)
6. Spawn 5 parallel `delegate_task` subagents:
   - Each gets read-only context bundle
   - Each checks assigned alignment edges
   - Each returns structured feedback with status per edge
7. Consolidate feedback into `review-code.md`
8. Report alignment summary: PASS/PARTIAL/FAIL per edge

**Reviewer Prompt Template:**
```
You are reviewing an implementation for {LENS}.

IMPORTANT: You are READ-ONLY. Do not write files, execute commands, or spawn agents.

Change: {CHANGE_NAME}
Scope: {REVIEW_SCOPE}

Context Bundle:
{SANITIZED_CONTEXT}

Git Diff: {DIFF_CONTENT}
Task Status: {TASKS_STATUS}

## Alignment Verification

### Your Assigned Edges:
{ASSIGNED_EDGES}

### For Each Edge:
1. Read the provided context
2. Check alignment
3. Provide status: PASS, PARTIAL, FAIL, N/A, UNKNOWN, NOT_REVIEWED
4. Provide evidence: file paths, line numbers, specific findings

### Output Format:
For each edge:
- Edge: {EDGE_NAME}
- Status: {STATUS}
- Evidence: {EVIDENCE}
- Findings: {FINDINGS}
```

## Output Format

### review-plan.md (Alignment Matrix, Revised)

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
| Security | {STATUS} | Claude Code | {EVIDENCE} |

## Consensus Issues

Issues flagged by 3+ providers:

{CONSENSUS_ISSUES}

## Provider-Specific Findings

### Hermes (Spec Compliance)
{HERMES_FINDINGS}

### Claude Code (Security)
{CLAUDE_FINDINGS}

### Codex (Quality & Tests)
{CODEX_FINDINGS}

### Antigravity (Architecture)
{ANTIGRAVITY_FINDINGS}

### fable-5 (Product Scope)
{FABLE5_FINDINGS}

## Recommended Actions

{RECOMMENDED_ACTIONS}
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
- **Security:** Reviewers are read-only, context is sanitized, credentials are excluded

## Tradeoffs

| Decision | Rationale |
|---|---|
| Two skills (plan + code) | Different contexts, different prompts, user choice |
| Parallel execution | Faster than sequential; providers are independent |
| Alignment matrix output | Clear visualization of drift across 4 artifacts |
| Manual invocation | User controls when review happens; not forced on all changes |
| No auto-fix | Review reports issues, human decides how to fix |
| Trust boundary | Prevents prompt injection and credential exposure |
| Evidence collection | Reviews are data-driven, not opinion-based |
| Status semantics | Clear, actionable findings with evidence |
