# Tasks

## 1. Create Plan Review Skill

- [ ] 1.1 Create skill directory structure at `~/.hermes/skills/openspec-workflow/openspec-plan-review/`
- [ ] 1.2 Write SKILL.md with frontmatter, purpose, and workflow steps
- [ ] 1.3 Define review prompt template for each provider (Hermes, Claude Code, Codex, Antigravity, fable-5)
- [ ] 1.4 Implement artifact reading logic (openspec show --json)
- [ ] 1.5 Implement parallel delegation via delegate_task
- [ ] 1.6 Implement feedback consolidation logic
- [ ] 1.7 Create review-plan.md output template
- [ ] 1.8 Add error handling for provider failures
- [ ] 1.9 Test with existing change (e.g., optimize-hermes-agent-configuration)

## 2. Create Code Review Skill

- [ ] 2.1 Create skill directory structure at `~/.hermes/skills/openspec-workflow/openspec-code-review/`
- [ ] 2.2 Write SKILL.md with frontmatter, purpose, and workflow steps
- [ ] 2.3 Define review prompt template for each provider (security, performance, architecture, product, completeness)
- [ ] 2.4 Implement artifact reading logic (openspec show --json)
- [ ] 2.5 Implement git diff extraction
- [ ] 2.6 Implement task status extraction from tasks.md
- [ ] 2.7 Implement parallel delegation via delegate_task
- [ ] 2.8 Implement feedback consolidation logic
- [ ] 2.9 Create review-code.md output template
- [ ] 2.10 Add error handling for provider failures
- [ ] 2.11 Test with existing implemented change

## 3. Create Review Templates

- [ ] 3.1 Create review-plan.md template with sections for each provider
- [ ] 3.2 Create review-code.md template with sections for each provider
- [ ] 3.3 Create consensus/divergence tracking format
- [ ] 3.4 Create recommended actions format

## 4. Documentation

- [ ] 4.1 Write usage guide for openspec-plan-review skill
- [ ] 4.2 Write usage guide for openspec-code-review skill
- [ ] 4.3 Document workflow integration points
- [ ] 4.4 Document provider-specific review lenses
- [ ] 4.5 Document relationship to /opsx:verify

## 5. Validation

- [ ] 5.1 Test plan review skill with a real change
- [ ] 5.2 Test code review skill with a real implemented change
- [ ] 5.3 Verify parallel execution works (5 providers run concurrently)
- [ ] 5.4 Verify error handling (one provider fails, others continue)
- [ ] 5.5 Verify output format is correct and readable
- [ ] 5.6 Update SPEC_INDEX.md if delta specs are created

## 6. Integration

- [ ] 6.1 Add skills to openspec-workflow skill category
- [ ] 6.2 Update openspec-workflow SKILL.md to reference new skills
- [ ] 6.3 Commit all changes to openspec-store
- [ ] 6.4 Archive change after validation
