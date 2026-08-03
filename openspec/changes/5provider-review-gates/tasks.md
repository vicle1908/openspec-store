# Tasks

## 1. Create Review Scope Template

- [ ] 1.1 Create `review-scope.yaml` template with all required fields
- [ ] 1.2 Define schema: change_name, repositories, specs, docs, skills, excluded
- [ ] 1.3 Add validation logic for scope file
- [ ] 1.4 Document how to create scope for each change

## 2. Create Plan Review Skill (Revised)

- [ ] 2.1 Create skill directory structure at `~/.hermes/skills/openspec-workflow/openspec-plan-review/`
- [ ] 2.2 Write SKILL.md with frontmatter, purpose, and trust boundary requirements
- [ ] 2.3 Implement scope reading from `review-scope.yaml`
- [ ] 2.4 Implement artifact reading via `openspec status --change <name> --json`
- [ ] 2.5 Implement context reading via `openspec instructions apply --json`
- [ ] 2.6 Implement context bundle collection (allowlisted, redacted)
- [ ] 2.7 Create reviewer prompt template for Hermes (spec compliance)
- [ ] 2.8 Create reviewer prompt template for Claude Code (security)
- [ ] 2.9 Create reviewer prompt template for Codex (quality & tests)
- [ ] 2.10 Create reviewer prompt template for Antigravity (architecture)
- [ ] 2.11 Create reviewer prompt template for fable-5 (product scope)
- [ ] 2.12 Implement parallel delegation with read-only constraints
- [ ] 2.13 Implement feedback consolidation with status semantics
- [ ] 2.14 Create `review-plan.md` output template with 8-edge matrix
- [ ] 2.15 Add error handling for provider failures (UNKNOWN/NOT_REVIEWED)
- [ ] 2.16 Test with existing change (e.g., optimize-hermes-agent-configuration)

## 3. Create Code Review Skill (Revised)

- [ ] 3.1 Create skill directory structure at `~/.hermes/skills/openspec-workflow/openspec-code-review/`
- [ ] 3.2 Write SKILL.md with frontmatter, purpose, and trust boundary requirements
- [ ] 3.3 Implement scope reading from `review-scope.yaml`
- [ ] 3.4 Implement artifact reading via `openspec status --change <name> --json`
- [ ] 3.5 Implement git diff extraction
- [ ] 3.6 Implement task status extraction from tasks.md
- [ ] 3.7 Implement context bundle collection (allowlisted, redacted)
- [ ] 3.8 Create reviewer prompt template for Hermes (spec compliance)
- [ ] 3.9 Create reviewer prompt template for Claude Code (security audit)
- [ ] 3.10 Create reviewer prompt template for Codex (quality & tests)
- [ ] 3.11 Create reviewer prompt template for Antigravity (architecture)
- [ ] 3.12 Create reviewer prompt template for fable-5 (product scope)
- [ ] 3.13 Implement parallel delegation with read-only constraints
- [ ] 3.14 Implement feedback consolidation with status semantics
- [ ] 3.15 Create `review-code.md` output template with 8-edge matrix
- [ ] 3.16 Add error handling for provider failures (UNKNOWN/NOT_REVIEWED)
- [ ] 3.17 Test with existing implemented change

## 4. Create Alignment Templates

- [ ] 4.1 Create alignment matrix template (8 edges × status × evidence)
- [ ] 4.2 Create `review-plan.md` template with alignment matrix sections
- [ ] 4.3 Create `review-code.md` template with alignment matrix sections
- [ ] 4.4 Create provider-specific finding sections
- [ ] 4.5 Create recommended fixes format
- [ ] 4.6 Create documentation/skills update tracking format

## 5. Documentation

- [ ] 5.1 Write usage guide for openspec-plan-review skill (revised)
- [ ] 5.2 Write usage guide for openspec-code-review skill (revised)
- [ ] 5.3 Document trust boundary and reviewer constraints
- [ ] 5.4 Document alignment check dimensions and what each provider checks
- [ ] 5.5 Document workflow integration points
- [ ] 5.6 Document relationship to /opsx:verify
- [ ] 5.7 Document how to interpret alignment matrix and status semantics

## 6. Validation

- [ ] 6.1 Test plan review skill with a real change
- [ ] 6.2 Test code review skill with a real implemented change
- [ ] 6.3 Verify parallel execution works (5 providers run concurrently)
- [ ] 6.4 Verify error handling (one provider fails, others continue)
- [ ] 6.5 Verify alignment matrix output is correct and readable
- [ ] 6.6 Verify trust boundary is enforced (reviewers are read-only)
- [ ] 6.7 Verify evidence collection works (file paths, line numbers)
- [ ] 6.8 Verify status semantics are applied correctly
- [ ] 6.9 Update SPEC_INDEX.md if delta specs are created

## 7. Integration

- [ ] 7.1 Add skills to openspec-workflow skill category
- [ ] 7.2 Update openspec-workflow SKILL.md to reference new skills
- [ ] 7.3 Commit all changes to openspec-store
- [ ] 7.4 Archive change after validation
