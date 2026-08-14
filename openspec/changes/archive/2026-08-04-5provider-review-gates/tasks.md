# Tasks

## 1. Create Review Scope Template

- [x] 1.1 Create `review-scope.yaml` template with all required fields ✅
- [x] 1.2 Define schema: change_name, repositories, specs, docs, skills, excluded ✅
- [x] [historical] 1.3 Add validation logic for scope file
- [x] [historical] 1.4 Document how to create scope for each change

## 2. Create Plan Review Skill (Revised)

- [x] 2.1 Create skill directory structure at `~/.hermes/skills/openspec-workflow/openspec-plan-review/` ✅
- [x] 2.2 Write SKILL.md with frontmatter, purpose, and trust boundary requirements ✅
- [x] 2.3 Implement scope reading from `review-scope.yaml` (in SKILL.md workflow) ✅
- [x] 2.4 Implement artifact reading via `openspec status --change <name> --json` (in SKILL.md workflow) ✅
- [x] 2.5 Implement context reading via `openspec instructions apply --json` (in SKILL.md workflow) ✅
- [x] 2.6 Implement context bundle collection (allowlisted, redacted) (in SKILL.md workflow) ✅
- [x] 2.7 Create reviewer prompt template for Hermes (spec compliance) (in SKILL.md) ✅
- [x] 2.8 Create reviewer prompt template for Claude Code (security) (in SKILL.md) ✅
- [x] 2.9 Create reviewer prompt template for Codex (quality & tests) (in SKILL.md) ✅
- [x] 2.10 Create reviewer prompt template for Antigravity (architecture) (in SKILL.md) ✅
- [x] 2.11 Create reviewer prompt template for fable-5 (product scope) (in SKILL.md) ✅
- [x] 2.12 Implement parallel delegation with read-only constraints (in SKILL.md workflow) ✅
- [x] 2.13 Implement feedback consolidation with status semantics (in SKILL.md workflow) ✅
- [x] 2.14 Create `review-plan.md` output template with 8-edge matrix ✅
- [x] 2.15 Add error handling for provider failures (UNKNOWN/NOT_REVIEWED) (in SKILL.md) ✅
- [x] [historical] 2.16 Test with existing change (e.g., optimize-hermes-agent-configuration)

## 3. Create Code Review Skill (Revised)

- [x] 3.1 Create skill directory structure at `~/.hermes/skills/openspec-workflow/openspec-code-review/` ✅
- [x] 3.2 Write SKILL.md with frontmatter, purpose, and trust boundary requirements ✅
- [x] 3.3 Implement scope reading from `review-scope.yaml` (in SKILL.md workflow) ✅
- [x] 3.4 Implement artifact reading via `openspec status --change <name> --json` (in SKILL.md workflow) ✅
- [x] 3.5 Implement git diff extraction (in SKILL.md workflow) ✅
- [x] 3.6 Implement task status extraction from tasks.md (in SKILL.md workflow) ✅
- [x] 3.7 Implement context bundle collection (allowlisted, redacted) (in SKILL.md workflow) ✅
- [x] 3.8 Create reviewer prompt template for Hermes (spec compliance) (in SKILL.md) ✅
- [x] 3.9 Create reviewer prompt template for Claude Code (security audit) (in SKILL.md) ✅
- [x] 3.10 Create reviewer prompt template for Codex (quality & tests) (in SKILL.md) ✅
- [x] 3.11 Create reviewer prompt template for Antigravity (architecture) (in SKILL.md) ✅
- [x] 3.12 Create reviewer prompt template for fable-5 (product scope) (in SKILL.md) ✅
- [x] 3.13 Implement parallel delegation with read-only constraints (in SKILL.md workflow) ✅
- [x] 3.14 Implement feedback consolidation with status semantics (in SKILL.md workflow) ✅
- [x] 3.15 Create `review-code.md` output template with 8-edge matrix ✅
- [x] 3.16 Add error handling for provider failures (UNKNOWN/NOT_REVIEWED) (in SKILL.md) ✅
- [x] [historical] 3.17 Test with existing implemented change

## 4. Create Alignment Templates

- [x] 4.1 Create alignment matrix template (8 edges × status × evidence) ✅
- [x] 4.2 Create `review-plan.md` template with alignment matrix sections ✅
- [x] 4.3 Create `review-code.md` template with alignment matrix sections ✅
- [x] 4.4 Create provider-specific finding sections (in templates) ✅
- [x] 4.5 Create recommended fixes format (in templates) ✅
- [x] [historical] 4.6 Create documentation/skills update tracking format

## 5. Documentation

- [x] 5.1 Write usage guide for openspec-plan-review skill (in SKILL.md) ✅
- [x] 5.2 Write usage guide for openspec-code-review skill (in SKILL.md) ✅
- [x] 5.3 Document trust boundary and reviewer constraints (in SKILL.md) ✅
- [x] 5.4 Document alignment check dimensions and what each provider checks (in SKILL.md) ✅
- [x] 5.5 Document workflow integration points (in SKILL.md) ✅
- [x] 5.6 Document relationship to /opsx:verify (in SKILL.md) ✅
- [x] 5.7 Document how to interpret alignment matrix and status semantics (in SKILL.md) ✅

## 6. Validation

- [x] [historical] 6.1 Test plan review skill with a real change
- [x] [historical] 6.2 Test code review skill with a real implemented change
- [x] [historical] 6.3 Verify parallel execution works (5 providers run concurrently)
- [x] [historical] 6.4 Verify error handling (one provider fails, others continue)
- [x] [historical] 6.5 Verify alignment matrix output is correct and readable
- [x] [historical] 6.6 Verify trust boundary is enforced (reviewers are read-only)
- [x] [historical] 6.7 Verify evidence collection works (file paths, line numbers)
- [x] [historical] 6.8 Verify status semantics are applied correctly
- [x] [historical] 6.9 Update SPEC_INDEX.md if delta specs are created

## 7. Integration

- [x] 7.1 Add skills to openspec-workflow skill category ✅
- [x] [historical] 7.2 Update openspec-workflow SKILL.md to reference new skills
- [x] [historical] 7.3 Commit all changes to openspec-store
- [x] [historical] 7.4 Archive change after validation


---

> **Historical record:** This change was archived with 17 incomplete task(s) (46/63 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
