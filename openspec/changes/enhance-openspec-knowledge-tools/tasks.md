# Tasks: Enhance OpenSpec Workflow with Knowledge Tools Integration

## Task 1: Create knowledge-tools-integration reference

- [ ] 1.1 Create `references/knowledge-tools-integration.md` with sections:
  - `## Tool Routing Table` — question type → first tool → deeper tool (4 rows: structural/semantic/episodic/curated)
  - `## Phase 1: Knowledge Context Gathering` — graphify query, gitnexus impact, wiki_search, memory_smart_search commands
  - `## Phase 2: Knowledge Evidence in Reviews` — how to add knowledge outputs to context bundle
  - `## Phase 4: Knowledge Freshness Verification` — graphify check-update, wiki_stale, gitnexus staleness commands
  - `## Phase 5: Post-Archive Knowledge Capture` — simplified: update wiki entity pages for affected services, run graphify update on affected repos
  - `## Minimal Path for Small Changes` — skip knowledge steps when change touches ≤1 repo, no documented services, no core code
- [ ] 1.2 Add cross-references from existing `cross-repo-blast-radius-search.md` to new reference

## Task 2: Update openspec-workflow SKILL.md

- [ ] 2.1 Add "Knowledge Context Gathering" step to Phase 1 (Create) after cross-repo search
- [ ] 2.2 Add "Knowledge Evidence" to Phase 2 (Design & Review) — extend context bundle description
- [ ] 2.3 Add "Post-Apply Knowledge Update" to Phase 3 (Apply) — batch graphify update after ALL slices complete (not per-commit)
- [ ] 2.4 Add "Knowledge Freshness" to Phase 4 (Validate) — before final validation
- [ ] 2.5 Add "Knowledge Capture" to Phase 5 (Archive) — after archive command
- [ ] 2.6 Add reference link to `references/knowledge-tools-integration.md` in Purpose section
- [ ] 2.7 Add pitfall: "Knowledge tools can return stale data — always verify freshness before using as evidence"

## Task 3: Update openspec-review-governance

- [ ] 3.1 Add knowledge tool evidence types to the review governance rules
- [ ] 3.2 Add rule: "When knowledge tool outputs are included in the context bundle, verify their freshness before using as evidence"
- [ ] 3.3 Add rule: "Knowledge ↔ Code edge is UNKNOWN when knowledge tools haven't been queried"

## Task 4: Update openspec-plan-review — CLI-based reviews

- [ ] 4.1 Add "Knowledge ↔ Code" as the 9th edge in the alignment matrix
- [ ] 4.2 Update Step 4 (Build Context Bundle) to include knowledge tool outputs
- [ ] 4.3 Replace Step 5 (delegate_task) with external CLI invocations:
  - `claude -p` for security (300s timeout, stream-json)
  - `codex exec` for quality & tests (300s timeout, json output)
  - `agy --print` for architecture (300s timeout)
  - `kimi -p` for product scope (300s timeout, stream-json)
  - `opencode run` for cross-cutting (300s timeout)
- [ ] 4.4 Add orchestrator inline review for spec compliance (Hermes does this directly)
- [ ] 4.5 Update reviewer assignment table — assign Knowledge ↔ Code edge to Hermes (spec compliance lens)
- [ ] 4.6 Update alignment-matrix-template.md with new edge
- [ ] 4.7 Update review-plan-template.md with new edge
- [ ] 4.8 Add pitfall: "delegate_task reviews fail with vars() serialization bug — always use external CLI agents"
- [ ] 4.9 Add CLI budget guidance: "Give each reviewer 300-600s timeout. Reviews are reasoning-heavy."

## Task 5: Update openspec-code-review — CLI-based reviews

- [ ] 5.1 Add "Knowledge ↔ Code" as the 9th edge in the alignment matrix
- [ ] 5.2 Update Step 4 (Collect Evidence) to include knowledge freshness checks
- [ ] 5.3 Replace Step 5 (delegate_task) with external CLI invocations (same pattern as Task 4.3)
- [ ] 5.4 Update reviewer assignment table — assign Knowledge ↔ Code edge to Hermes
- [ ] 5.5 Update alignment-matrix-template.md with new edge
- [ ] 5.6 Add CLI budget guidance (same as Task 4.9)

## Task 5b: Update hermes-skills spec

- [ ] 5b.1 Update `openspec/specs/hermes-skills/spec.md` — change 8-edge alignment matrix to 9 edges (add Knowledge ↔ Code)
- [ ] 5b.2 Update alignment matrix scenario descriptions to include Knowledge ↔ Code edge

## Task 6: Verify

- [ ] 6.1 Run `openspec validate enhance-openspec-knowledge-tools --store openspec-store`
- [ ] 6.2 Verify references are internally consistent — check these specific files:
  - `references/knowledge-tools-integration.md` (new) — all tool commands valid
  - `references/cross-repo-blast-radius-search.md` — cross-reference to new file works
  - `references/alignment-matrix-template.md` — 9 edges listed
  - `references/review-plan-template.md` — 9 edges listed
- [ ] 6.3 Verify AGENTS.md word count stays ≤ 550 (no changes expected)
