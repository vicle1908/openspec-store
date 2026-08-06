# Tasks: Enhance OpenSpec Workflow with Knowledge Tools Integration

## Task 1: Create knowledge-tools-integration reference

- [ ] 1.1 Create `references/knowledge-tools-integration.md` with:
  - Tool routing table (question → first tool → deeper tool)
  - Per-phase integration steps with commands
  - Knowledge context gathering template
  - Knowledge freshness verification commands
  - Post-archive knowledge capture checklist
- [ ] 1.2 Add cross-references from existing `cross-repo-blast-radius-search.md` to new reference

## Task 2: Update openspec-workflow SKILL.md

- [ ] 2.1 Add "Knowledge Context Gathering" step to Phase 1 (Create) after cross-repo search
- [ ] 2.2 Add "Knowledge Evidence" to Phase 2 (Design & Review) — extend context bundle description
- [ ] 2.3 Add "Per-Commit Graph Updates" to Phase 3 (Apply) — after vertical slice commits
- [ ] 2.4 Add "Knowledge Freshness" to Phase 4 (Validate) — before final validation
- [ ] 2.5 Add "Knowledge Capture" to Phase 5 (Archive) — after archive command
- [ ] 2.6 Add reference link to `references/knowledge-tools-integration.md` in Purpose section
- [ ] 2.7 Add pitfall: "Knowledge tools can return stale data — always verify freshness before using as evidence"

## Task 3: Update openspec-review-governance

- [ ] 3.1 Add knowledge tool evidence types to the review governance rules
- [ ] 3.2 Add rule: "When knowledge tool outputs are included in the context bundle, verify their freshness before using as evidence"
- [ ] 3.3 Add rule: "Knowledge ↔ Code edge is UNKNOWN when knowledge tools haven't been queried"

## Task 4: Update openspec-plan-review

- [ ] 4.1 Add "Knowledge ↔ Code" as the 9th edge in the alignment matrix
- [ ] 4.2 Update Step 4 (Build Context Bundle) to include knowledge tool outputs
- [ ] 4.3 Update reviewer assignment table — assign Knowledge ↔ Code edge to Hermes (spec compliance lens)
- [ ] 4.4 Update alignment-matrix-template.md with new edge
- [ ] 4.5 Update review-plan-template.md with new edge

## Task 5: Update openspec-code-review

- [ ] 5.1 Add "Knowledge ↔ Code" as the 9th edge in the alignment matrix
- [ ] 5.2 Update Step 4 (Collect Evidence) to include knowledge freshness checks
- [ ] 5.3 Update reviewer assignment table — assign Knowledge ↔ Code edge to Hermes
- [ ] 5.4 Update alignment-matrix-template.md with new edge

## Task 6: Verify

- [ ] 6.1 Run `openspec validate enhance-openspec-knowledge-tools --store openspec-store`
- [ ] 6.2 Verify all references are internally consistent (no broken links)
- [ ] 6.3 Verify AGENTS.md word count stays ≤ 550 (no changes expected)
