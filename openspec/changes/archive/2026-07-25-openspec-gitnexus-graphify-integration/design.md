## Context

OpenSpec workflows manage the lifecycle of changes. Currently, they operate without code intelligence tools.

**Current guardrails in openspec-apply-change:**
```
- Keep going through tasks until done or blocked
- Always read context files before starting
- If task is ambiguous, pause and ask before implementing
- Keep code changes minimal and scoped to each task
- Update task checkbox immediately after completing each task
```

**What's missing:** No impact analysis, no change detection, no architecture exploration.

## Goals / Non-Goals

**Goals:**
- Add GitNexus impact analysis BEFORE code changes
- Add GitNexus detect_changes AFTER code changes
- Add GitNexus/Graphify exploration in explore workflow
- Add blast radius assessment in propose workflow
- Add scope verification in verify workflow

**Non-Goals:**
- Modify GitNexus or Graphify tools
- Change OpenSpec workflow structure
- Add new OpenSpec skills

## Decisions

### Decision 1: Add guardrails to openspec-apply-change

**Choice:** Add mandatory GitNexus checks before and after each code change.

**Implementation location:** After existing guardrails section

**New guardrails to add:**
```markdown
## Code Intelligence Guardrails

**MANDATORY before ANY code change:**
- MUST run impact analysis before editing any function, class, or method
- MUST warn user if impact returns HIGH or CRITICAL risk
- MUST NOT proceed with edit until user confirms

**MANDATORY after each code change:**
- MUST run detect_changes() to verify scope
- MUST verify affected symbols match design artifacts
- MUST report any scope creep to user
```

### Decision 2: Add exploration to openspec-explore

**Choice:** Add GitNexus and Graphify integration.

**Implementation location:** New section after existing exploration workflow

**New content to add:**
```markdown
## Code Intelligence Integration

### For code understanding:
1. READ gitnexus://repo/{name}/context → Check index freshness
2. query({search_query: "concept"}) → Find execution flows
3. context({name: "symbol"}) → Deep dive on specific symbol

### For architecture exploration:
1. graphify query "concept" → Find related modules
2. graphify path "A" "B" → Find dependencies
3. graphify explain "Component" → Understand relationships
```

### Decision 3: Add impact analysis to openspec-propose

**Choice:** Add blast radius assessment.

**Implementation location:** New section before proposal generation

**New content to add:**
```markdown
## Pre-Proposal Analysis

Before proposing changes:
1. Run GitNexus impact analysis on affected symbols
2. Include blast radius in proposal document
3. Assess risk level (LOW/MEDIUM/HIGH/CRITICAL)
```

### Decision 4: Add scope verification to openspec-verify-change

**Choice:** Add detect_changes for scope verification.

**Implementation location:** New section in verification checklist

**New content to add:**
```markdown
## Scope Verification

1. Run detect_changes() to verify implementation scope
2. Compare affected symbols with design artifacts
3. Verify no scope creep
```

## Risks / Trade-offs

**[Risk] GitNexus index freshness** → Impact analysis requires fresh index. Mitigation: Check index status before running.
**[Risk] Performance** → Running impact analysis adds time. Mitigation: Only run for code symbols, not docs/config.
