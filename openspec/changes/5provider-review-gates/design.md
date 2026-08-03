# Design: 5-Provider Review Gates

## Architecture

Two Hermes skills that orchestrate parallel reviews across 5 AI providers:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HERMES ORCHESTRATOR                          │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ Plan Review   │    │ Code Review   │    │ Consolidate  │     │
│  │ Skill         │    │ Skill         │    │ & Report     │     │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              PARALLEL DELEGATION                        │   │
│  │                                                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │  │ Hermes  │ │ Claude  │ │ Codex   │ │ Antigravity│ │ fable-5  │ │
│  │  │ Review  │ │ Review  │ │ Review  │ │ Review    │ │ Review   │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Provider Review Lenses

### Plan Review Gate (after propose, before apply)

| Provider | Review Focus | Why This Provider |
|---|---|---|
| **Hermes** | Spec compliance, requirement testability | Host session with full context |
| **Claude Code** | Security, auth, data exposure | Strong at security analysis |
| **Codex** | Performance, N+1 queries, scaling | Strong at code quality |
| **Antigravity** | Architecture, design patterns, coupling | Google's code analysis strengths |
| **fable-5** | Product scope, edge cases, UX gaps | fable-5 reasoning capabilities |

### Code Review Gate (after apply, before verify/archive)

| Provider | Review Focus | Why This Provider |
|---|---|---|
| **Hermes** | Spec-code alignment, completeness | Host session, full context |
| **Claude Code** | Security audit, vulnerabilities | Strong at security analysis |
| **Codex** | Code quality, test coverage, error handling | Strong at code quality |
| **Antigravity** | Architecture adherence, patterns | Google's code analysis strengths |
| **fable-5** | Completeness, unhandled scenarios | fable-5 reasoning capabilities |

## Skill Implementation

### Skill 1: `openspec-plan-review`

**Location:** `~/.hermes/skills/openspec-workflow/openspec-plan-review/SKILL.md`

**Workflow:**
1. Accept change name as argument
2. Read change artifacts via `openspec show <change> --json`
3. Extract proposal, specs, design, tasks content
4. Spawn 5 parallel `delegate_task` subagents:
   - Each gets a specialized review prompt with the artifacts
   - Each returns structured feedback (CRITICAL/WARNING/SUGGESTION/APPROVED)
5. Consolidate feedback into `review-plan.md` in the change folder
6. Report summary to user: consensus items, divergent opinions, critical issues

**Review Prompt Template:**
```
You are reviewing an OpenSpec change for {LENS}.

Change: {CHANGE_NAME}
Schema: spec-driven

## Artifacts

### proposal.md
{PROPOSAL_CONTENT}

### specs (delta)
{SPECS_CONTENT}

### design.md
{DESIGN_CONTENT}

### tasks.md
{TASKS_CONTENT}

## Review Instructions

Analyze these artifacts for {LENS} concerns. Provide structured feedback:

### CRITICAL (must fix before implementation)
Issues that would cause bugs, security flaws, or spec violations.

### WARNINGS (should address)
Issues that could cause problems but aren't blocking.

### SUGGESTIONS (nice to have)
Improvements, optimizations, or best practices.

### APPROVED (no issues found)
Aspects that are correctly designed.

Be specific. Reference exact requirements, scenarios, or tasks when providing feedback.
```

### Skill 2: `openspec-code-review`

**Location:** `~/.hermes/skills/openspec-workflow/openspec-code-review/SKILL.md`

**Workflow:**
1. Accept change name as argument
2. Read change artifacts via `openspec show <change> --json`
3. Get git diff for implementation changes
4. Get task completion status from tasks.md
5. Spawn 5 parallel `delegate_task` subagents:
   - Each gets artifacts + diff + task status
   - Each returns structured feedback
6. Consolidate feedback into `review-code.md` in the change folder
7. Report summary to user

**Review Prompt Template:**
```
You are reviewing an implementation for {LENS}.

Change: {CHANGE_NAME}

## Delta Specs (what should be implemented)
{SPECS_CONTENT}

## Implementation (git diff)
{DIFF_CONTENT}

## Task Status
{TASKS_STATUS}

## Review Instructions

Verify the implementation matches the specs and review for {LENS} concerns.

### CRITICAL (bugs, security flaws, spec violations)
Issues that would cause failures or security vulnerabilities.

### WARNINGS (code quality, missing tests, edge cases)
Issues that should be addressed but aren't blocking.

### SUGGESTIONS (improvements, refactoring)
Optimizations or best practice recommendations.

### VERIFIED (correctly implemented)
Requirements that are correctly implemented with evidence.

Reference specific requirements, scenarios, or task numbers when providing feedback.
```

## Output Format

### review-plan.md

```markdown
# Plan Review: {CHANGE_NAME}

**Reviewed:** {TIMESTAMP}
**Providers:** Hermes, Claude Code, Codex, Antigravity, fable-5

## Summary

- Critical issues: {COUNT}
- Warnings: {COUNT}
- Suggestions: {COUNT}
- Approved items: {COUNT}

## Consensus Items

Issues flagged by 3+ providers:

{CONSENSUS_ITEMS}

## Divergent Opinions

Where providers disagreed:

{DIVERGENT_ITEMS}

## Detailed Feedback

### Hermes (Spec Compliance)
{HERMES_FEEDBACK}

### Claude Code (Security)
{CLAUDE_FEEDBACK}

### Codex (Performance)
{CODEX_FEEDBACK}

### Antigravity (Architecture)
{ANTIGRAVITY_FEEDBACK}

### fable-5 (Product Scope)
{FABLE5_FEEDBACK}

## Recommended Actions

{RECOMMENDED_ACTIONS}
```

### review-code.md

```markdown
# Code Review: {CHANGE_NAME}

**Reviewed:** {TIMESTAMP}
**Providers:** Hermes, Claude Code, Codex, Antigravity, fable-5

## Summary

- Critical issues: {COUNT}
- Warnings: {COUNT}
- Suggestions: {COUNT}
- Verified items: {COUNT}

## Spec-Code Alignment

Requirements correctly implemented:
{VERIFIED_REQUIREMENTS}

Requirements with gaps:
{GAP_REQUIREMENTS}

## Detailed Feedback

### Hermes (Spec-Code Alignment)
{HERMES_FEEDBACK}

### Claude Code (Security Audit)
{CLAUDE_FEEDBACK}

### Codex (Code Quality)
{CODEX_FEEDBACK}

### Antigravity (Architecture Adherence)
{ANTIGRAVITY_FEEDBACK}

### fable-5 (Completeness)
{FABLE5_FEEDBACK}

## Test Coverage

Scenarios with test coverage:
{TESTED_SCENARIOS}

Scenarios missing coverage:
{UNTESTED_SCENARIOS}

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
              Artifacts      review-plan.md    Code changes   review-code.md   Verify
```

### Usage

```bash
# After propose, before apply
/openspec-plan-review add-dark-mode

# After apply, before verify/archive
/openspec-code-review add-dark-mode
```

### Relationship to /opsx:verify

- `/opsx:verify` = single-agent, quick check (completeness, correctness, fable-5)
- `openspec-code-review` = 5-provider, deep review (security, performance, architecture)

Use `/opsx:verify` for routine changes. Use `openspec-code-review` for high-stakes changes.

## Non-Functional Requirements

- **Performance:** 5 providers run in parallel, total time ≈ slowest provider (not sum)
- **Reliability:** Each provider failure is isolated; 4/5 providers still produce useful review
- **Usability:** Skills are invoked via simple command, no configuration needed
- **Maintainability:** Review prompts are templated, easy to adjust per provider
- **Observability:** Review output is structured, machine-readable, human-friendly

## Tradeoffs

| Decision | Rationale |
|---|---|
| Two skills (plan + code) | Different contexts, different prompts, user choice |
| Parallel execution | Faster than sequential; providers are independent |
| Structured output | Machine-readable for future automation, human-readable for review |
| Manual invocation | User controls when review happens; not forced on all changes |
| No custom schema | Works with existing `spec-driven`; schema is optional enhancement |
