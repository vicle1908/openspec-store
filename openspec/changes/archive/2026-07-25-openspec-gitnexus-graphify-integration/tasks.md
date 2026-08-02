## 1. Update openspec-apply-change

- [x] 1.1 Add "## Code Intelligence Guardrails" section after existing guardrails
- [x] 1.2 Add "MANDATORY before ANY code change" instruction with impact analysis
- [x] 1.3 Add "MANDATORY after each code change" instruction with detect_changes
- [x] 1.4 Add risk level handling: if HIGH/CRITICAL, pause and report to user
- [x] 1.5 Add reference to gitnexus-impact-analysis skill

## 2. Update openspec-explore

- [x] 2.1 Add "## Code Intelligence Integration" section
- [x] 2.2 Add GitNexus code exploration subsection (query, context)
- [x] 2.3 Add Graphify architecture exploration subsection (query, path, explain)
- [x] 2.4 Add reference to gitnexus-exploring and graphify skills

## 3. Update openspec-propose

- [x] 3.1 Add "## Pre-Proposal Analysis" section before proposal generation
- [x] 3.2 Add blast radius assessment using GitNexus impact
- [x] 3.3 Add risk level documentation (LOW/MEDIUM/HIGH/CRITICAL)

## 4. Update openspec-verify-change

- [x] 4.1 Add "## Scope Verification" section with detect_changes
- [x] 4.2 Add architecture verification with Graphify explain
- [x] 4.3 Add comparison of affected symbols with design artifacts
