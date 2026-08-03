# Tasks

## 1. Create Plan Review Skill (Alignment)

- [ ] 1.1 Create skill directory structure at `~/.hermes/skills/openspec-workflow/openspec-plan-review/`
- [ ] 1.2 Write SKILL.md with frontmatter, purpose, and alignment-focused workflow
- [ ] 1.3 Define alignment check dimensions (spec-code, code-docs, docs-skills, skills-specs)
- [ ] 1.4 Create review prompt template for Hermes (spec ↔ code alignment)
- [ ] 1.5 Create review prompt template for Claude Code (security alignment)
- [ ] 1.6 Create review prompt template for Codex (quality alignment)
- [ ] 1.7 Create review prompt template for Antigravity (architecture alignment)
- [ ] 1.8 Create review prompt template for fable-5 (product alignment)
- [ ] 1.9 Implement artifact reading logic (openspec show --json)
- [ ] 1.10 Implement context reading (existing specs, code patterns, docs, skills)
- [ ] 1.11 Implement parallel delegation via delegate_task
- [ ] 1.12 Implement alignment matrix consolidation logic
- [ ] 1.13 Create review-plan.md output template with alignment matrix
- [ ] 1.14 Add error handling for provider failures
- [ ] 1.15 Test with existing change (e.g., optimize-hermes-agent-configuration)

## 2. Create Code Review Skill (Alignment)

- [ ] 2.1 Create skill directory structure at `~/.hermes/skills/openspec-workflow/openspec-code-review/`
- [ ] 2.2 Write SKILL.md with frontmatter, purpose, and alignment-focused workflow
- [ ] 2.3 Define alignment check dimensions for implementation
- [ ] 2.4 Create review prompt template for Hermes (code ↔ specs alignment)
- [ ] 2.5 Create review prompt template for Claude Code (code ↔ docs alignment)
- [ ] 2.6 Create review prompt template for Codex (code ↔ tests alignment)
- [ ] 2.7 Create review prompt template for Antigravity (code ↔ skills alignment)
- [ ] 2.8 Create review prompt template for fable-5 (code ↔ product alignment)
- [ ] 2.9 Implement artifact reading logic (openspec show --json)
- [ ] 2.10 Implement git diff extraction
- [ ] 2.11 Implement task status extraction from tasks.md
- [ ] 2.12 Implement context reading (existing docs, skills, specs)
- [ ] 2.13 Implement parallel delegation via delegate_task
- [ ] 2.14 Implement alignment matrix consolidation logic
- [ ] 2.15 Create review-code.md output template with alignment matrix
- [ ] 2.16 Add error handling for provider failures
- [ ] 2.17 Test with existing implemented change

## 3. Create Alignment Templates

- [ ] 3.1 Create alignment matrix template (6 edges × status)
- [ ] 3.2 Create review-plan.md template with alignment matrix sections
- [ ] 3.3 Create review-code.md template with alignment matrix sections
- [ ] 3.4 Create provider-specific finding sections
- [ ] 3.5 Create recommended fixes format
- [ ] 3.6 Create documentation/skills update tracking format

## 4. Documentation

- [ ] 4.1 Write usage guide for openspec-plan-review skill (alignment focus)
- [ ] 4.2 Write usage guide for openspec-code-review skill (alignment focus)
- [ ] 4.3 Document alignment check dimensions and what each provider checks
- [ ] 4.4 Document workflow integration points
- [ ] 4.5 Document relationship to /opsx:verify
- [ ] 4.6 Document how to interpret alignment matrix

## 5. Validation

- [ ] 5.1 Test plan review skill with a real change
- [ ] 5.2 Test code review skill with a real implemented change
- [ ] 5.3 Verify parallel execution works (5 providers run concurrently)
- [ ] 5.4 Verify error handling (one provider fails, others continue)
- [ ] 5.5 Verify alignment matrix output is correct and readable
- [ ] 5.6 Verify alignment edges are properly checked
- [ ] 5.7 Update SPEC_INDEX.md if delta specs are created

## 6. Integration

- [ ] 6.1 Add skills to openspec-workflow skill category
- [ ] 6.2 Update openspec-workflow SKILL.md to reference new skills
- [ ] 6.3 Commit all changes to openspec-store
- [ ] 6.4 Archive change after validation
