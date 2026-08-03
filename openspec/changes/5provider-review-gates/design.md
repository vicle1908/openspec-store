# Design: 5-Provider Review Gates (Alignment Focus)

## The Alignment Problem

```
┌─────────────────────────────────────────────────────────────────┐
│                    ALIGNMENT MATRIX                             │
│                                                                 │
│    Specs ←→ Code ←→ Docs ←→ Skills ←→ Specs                    │
│      │        │       │        │        │                       │
│      └────────┴───────┴────────┴────────┘                       │
│                    │                                            │
│         5-Provider Review checks all edges                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Four artifacts, six alignment edges:**

| Edge | What Drifts | Example |
|---|---|---|
| **Spec ↔ Code** | Requirements not implemented, code not in specs | Spec says "MUST timeout after 30min", code uses 60min |
| **Code ↔ Docs** | Implementation differs from documented patterns | AGENTS.md says "use pytest", code uses unittest |
| **Docs ↔ Skills** | Skills reference outdated commands/patterns | Skill says `openspec validate --change`, CLI uses `openspec validate <name>` |
| **Skills ↔ Specs** | Skills implement workflows not in specs | Skill has 5-step process, spec describes 3-step |
| **Spec ↔ Docs** | Documentation doesn't match spec requirements | Spec requires "SHALL log all errors", docs don't mention logging |
| **Code ↔ Skills** | Skills assume code patterns that changed | Skill imports `from agent_core.cli import app`, code moved to `agent_core.cli.app` |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HERMES ORCHESTRATOR                          │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ Plan Review   │    │ Code Review   │    │ Consolidate  │     │
│  │ (Alignment)   │    │ (Alignment)   │    │ & Report     │     │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              PARALLEL DELEGATION                        │   │
│  │                                                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │  │ Hermes  │ │ Claude  │ │ Codex   │ │ Antigravity│ │ fable-5  │ │
│  │  │ Spec    │ │ Security│ │ Quality │ │ Architecture│ │ Product  │ │
│  │  │ Context │ │ Auth    │ │ Tests   │ │ Patterns   │ │ Scope    │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Provider Review Lenses (Alignment-Focused)

### Plan Review Gate (after propose, before apply)

| Provider | Alignment Focus | What They Check |
|---|---|---|
| **Hermers** | Spec ↔ Code alignment | Do specs match existing code patterns? Are requirements testable against current implementation? |
| **Claude Code** | Security alignment | Do security specs match auth implementation? Are security docs current? |
| **Codex** | Quality alignment | Do test specs match test coverage? Are quality docs accurate? |
| **Antigravity** | Architecture alignment | Do architecture specs match code structure? Are design docs current? |
| **fable-5** | Product alignment | Do product specs match UX implementation? Are user docs accurate? |

### Code Review Gate (after apply, before verify/archive)

| Provider | Alignment Focus | What They Check |
|---|---|---|
| **Hermers** | Code ↔ Specs alignment | Does implemented code match spec requirements? Are specs updated? |
| **Claude Code** | Code ↔ Docs alignment | Does code follow documented patterns? Are AGENTS.md patterns current? |
| **Codex** | Code ↔ Tests alignment | Do tests cover spec scenarios? Are test docs accurate? |
| **Antigravity** | Code ↔ Skills alignment | Does code match skill assumptions? Are skills using current APIs? |
| **fable-5** | Code ↔ Product alignment | Does implementation match product requirements? Are user docs current? |

## Alignment Check Dimensions

### For Each Provider Review

```
1. SPEC CHECK
   - Read delta specs for this change
   - Compare against existing main specs
   - Check for conflicts, gaps, or inconsistencies

2. CODE CHECK
   - Read git diff for implementation
   - Compare against spec requirements
   - Check for unimplemented requirements or extra features

3. DOCS CHECK
   - Read AGENTS.md, README.md, skill docs
   - Compare against code patterns
   - Check for outdated instructions or missing documentation

4. SKILLS CHECK
   - Read relevant Hermes skills
   - Compare against code APIs and patterns
   - Check for broken imports, outdated commands, or missing capabilities

5. CROSS-CHECK
   - Verify all four artifacts are mutually consistent
   - Flag any alignment gaps
   - Suggest fixes for drift
```

## Skill Implementation

### Skill 1: `openspec-plan-review` (Alignment-Focused)

**Location:** `~/.hermes/skills/openspec-workflow/openspec-plan-review/SKILL.md`

**Workflow:**
1. Accept change name as argument
2. Read change artifacts via `openspec show <change> --json`
3. Read existing specs, code patterns, docs, and skills for context
4. Spawn 5 parallel `delegate_task` subagents:
   - Each checks alignment across all 4 artifacts
   - Each returns structured feedback with alignment matrix
5. Consolidate feedback into `review-plan.md`
6. Report alignment summary: aligned edges, drifted edges, recommended fixes

**Review Prompt Template:**
```
You are reviewing an OpenSpec change for {ALIGNMENT_FOCUS}.

Change: {CHANGE_NAME}
Artifacts: {ARTIFACTS_CONTENT}

Existing Context:
- Main specs: {EXISTING_SPECS}
- Code patterns: {CODE_PATTERNS}
- Documentation: {DOCS_CONTENT}
- Skills: {SKILLS_CONTENT}

## Alignment Check

### Spec ↔ Code Alignment
- Do the delta specs match existing code patterns?
- Are requirements testable against current implementation?
- Any conflicts with existing specs?

### Code ↔ Docs Alignment
- Do the proposed changes follow documented patterns?
- Will AGENTS.md need updates?
- Are there undocumented changes?

### Docs ↔ Skills Alignment
- Do skills reference patterns that will change?
- Will skills need updates for new APIs?
- Any broken skill assumptions?

### Skills ↔ Specs Alignment
- Do skills implement workflows that match spec requirements?
- Are there spec requirements not covered by skills?
- Any skill-spec mismatches?

Provide structured feedback:

### CRITICAL (alignment broken)
Issues where artifacts fundamentally disagree.

### WARNINGS (alignment drifting)
Issues where artifacts are starting to diverge.

### SUGGESTIONS (alignment improvements)
Ways to improve alignment proactively.

### ALIGNED (no issues found)
Aspects that are correctly aligned across all artifacts.
```

### Skill 2: `openspec-code-review` (Alignment-Focused)

**Location:** `~/.hermes/skills/openspec-workflow/openspec-code-review/SKILL.md`

**Workflow:**
1. Accept change name as argument
2. Read change artifacts + git diff
3. Read existing docs, skills, and specs for context
4. Spawn 5 parallel `delegate_task` subagents:
   - Each checks implementation alignment across all 4 artifacts
   - Each returns structured feedback with alignment matrix
5. Consolidate feedback into `review-code.md`
6. Report alignment summary: verified alignments, broken alignments, recommended fixes

**Review Prompt Template:**
```
You are reviewing an implementation for {ALIGNMENT_FOCUS}.

Change: {CHANGE_NAME}
Delta specs: {SPECS_CONTENT}
Git diff: {DIFF_CONTENT}
Task status: {TASKS_STATUS}

Context:
- Existing docs: {DOCS_CONTENT}
- Relevant skills: {SKILLS_CONTENT}
- Existing specs: {EXISTING_SPECS}

## Alignment Verification

### Code ↔ Specs Alignment
- Does implementation match all spec requirements?
- Are there unimplemented requirements?
- Are there extra features not in specs?

### Code ↔ Docs Alignment
- Does code follow documented patterns in AGENTS.md?
- Will documentation need updates?
- Are there undocumented behavior changes?

### Code ↔ Skills Alignment
- Does code match skill assumptions about APIs?
- Will skills break with these changes?
- Are there new capabilities skills should document?

### Skills ↔ Specs Alignment
- Do skills implement workflows that match the implementation?
- Are there spec requirements skills don't cover?
- Any skill-spec mismatches exposed by this change?

Provide structured feedback:

### CRITICAL (alignment broken)
Issues where implementation fundamentally disagrees with artifacts.

### WARNINGS (alignment drifting)
Issues where implementation is starting to diverge.

### SUGGESTIONS (alignment improvements)
Ways to improve alignment proactively.

### VERIFIED (alignment confirmed)
Aspects correctly aligned across all artifacts, with evidence.
```

## Output Format

### review-plan.md (Alignment Matrix)

```markdown
# Plan Review: {CHANGE_NAME}

**Reviewed:** {TIMESTAMP}
**Providers:** Hermes, Claude Code, Codex, Antigravity, fable-5

## Alignment Summary

| Edge | Status | Issues |
|---|---|---|
| Spec ↔ Code | ✅ Aligned / ⚠️ Drifting / ❌ Broken | {COUNT} |
| Code ↔ Docs | ✅ / ⚠️ / ❌ | {COUNT} |
| Docs ↔ Skills | ✅ / ⚠️ / ❌ | {COUNT} |
| Skills ↔ Specs | ✅ / ⚠️ / ❌ | {COUNT} |
| Spec ↔ Docs | ✅ / ⚠️ / ❌ | {COUNT} |
| Code ↔ Skills | ✅ / ⚠️ / ❌ | {COUNT} |

## Consensus Alignment Issues

Issues flagged by 3+ providers:

{CONSENSUS_ISSUES}

## Provider-Specific Alignment Findings

### Hermes (Spec ↔ Code)
{HERMES_FINDINGS}

### Claude Code (Security Alignment)
{CLAUDE_FINDINGS}

### Codex (Quality Alignment)
{CODEX_FINDINGS}

### Antigravity (Architecture Alignment)
{ANTIGRAVITY_FINDINGS}

### fable-5 (Product Alignment)
{FABLE5_FINDINGS}

## Recommended Alignment Fixes

{RECOMMENDED_FIXES}
```

### review-code.md (Alignment Matrix)

```markdown
# Code Review: {CHANGE_NAME}

**Reviewed:** {TIMESTAMP}
**Providers:** Hermes, Claude Code, Codex, Antigravity, fable-5

## Alignment Summary

| Edge | Status | Verified | Gaps |
|---|---|---|---|
| Code ↔ Specs | ✅ / ⚠️ / ❌ | {VERIFIED} | {GAPS} |
| Code ↔ Docs | ✅ / ⚠️ / ❌ | {VERIFIED} | {GAPS} |
| Code ↔ Skills | ✅ / ⚠️ / ❌ | {VERIFIED} | {GAPS} |
| Skills ↔ Specs | ✅ / ⚠️ / ❌ | {VERIFIED} | {GAPS} |

## Verified Alignments

Requirements correctly implemented with evidence:

{VERIFIED_ITEMS}

## Broken Alignments

Requirements not implemented or incorrectly implemented:

{BROKEN_ITEMS}

## Provider-Specific Findings

### Hermes (Code ↔ Specs)
{HERMES_FINDINGS}

### Claude Code (Code ↔ Docs)
{CLAUDE_FINDINGS}

### Codex (Code ↔ Tests)
{CODEX_FINDINGS}

### Antigravity (Code ↔ Skills)
{ANTIGRAVITY_FINDINGS}

### fable-5 (Code ↔ Product)
{FABLE5_FINDINGS}

## Documentation Updates Needed

{DOCS_UPDATES}

## Skill Updates Needed

{SKILLS_UPDATES}

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
                            Matrix                       Matrix
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

## Tradeoffs

| Decision | Rationale |
|---|---|
| Two skills (plan + code) | Different contexts, different prompts, user choice |
| Parallel execution | Faster than sequential; providers are independent |
| Alignment matrix output | Clear visualization of drift across 4 artifacts |
| Manual invocation | User controls when review happens; not forced on all changes |
| No auto-fix | Review reports issues, human decides how to fix |
