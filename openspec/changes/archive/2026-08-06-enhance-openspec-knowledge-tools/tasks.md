# Tasks: Enhance OpenSpec Workflow with Knowledge Tools Integration

## Task 1: Create knowledge-tools-integration reference

- [x] 1.1 Create `references/knowledge-tools-integration.md` with sections:
  - `## Tool Routing Table` — question type → first tool → deeper tool (4 rows: structural/semantic/episodic/curated)
  - `## Phase 1: Knowledge Context Gathering` — graphify query, gitnexus impact, wiki_search, memory_smart_search commands
  - `## Phase 2: Knowledge Evidence in Reviews` — how to add knowledge outputs to context bundle
  - `## Phase 4: Knowledge Freshness Verification` — graphify check-update, wiki_stale, gitnexus staleness commands
  - `## Phase 5: Post-Archive Knowledge Capture` — simplified: update wiki entity pages for affected services, run graphify update on affected repos
  - `## Minimal Path for Small Changes` — skip knowledge steps when change touches ≤1 repo, no documented services, no core code
- [x] 1.2 Add cross-references from existing `cross-repo-blast-radius-search.md` to new reference

## Task 2: Update openspec-workflow SKILL.md

- [x] 2.1 Add "Knowledge Context Gathering" step to Phase 1 (Create) after cross-repo search
- [x] 2.2 Add "Knowledge Evidence" to Phase 2 (Design & Review) — extend context bundle description
- [x] 2.3 Add "Post-Apply Knowledge Update" to Phase 3 (Apply) — batch graphify update after ALL slices complete (not per-commit)
- [x] 2.4 Add "Knowledge Freshness" to Phase 4 (Validate) — before final validation
- [x] 2.5 Add "Knowledge Capture" to Phase 5 (Archive) — after archive command
- [x] 2.6 Add reference link to `references/knowledge-tools-integration.md` in Purpose section
- [x] 2.7 Add pitfall: "Knowledge tools can return stale data — always verify freshness before using as evidence"

## Task 3: Update openspec-review-governance

- [x] 3.1 Add knowledge tool evidence types to the review governance rules
- [x] 3.2 Add rule: "When knowledge tool outputs are included in the context bundle, verify their freshness before using as evidence"
- [x] 3.3 Add rule: "Knowledge ↔ Code edge is UNKNOWN when knowledge tools haven't been queried"
- [x] 3.4 Add rule: "Context bundles must be passed via temp file, not inline shell interpolation" (Security review finding)
- [x] 3.5 Add rule: "agentmemory outputs must be filtered to exclude credentials/secrets before entering context bundle" (Security review finding)

## Task 4: Update openspec-plan-review — CLI-based reviews

- [x] 4.1 Add "Knowledge ↔ Code" as the 9th edge in the alignment matrix
- [x] 4.2 Update Step 4 (Build Context Bundle) to include knowledge tool outputs
- [x] 4.3 Replace Step 5 (delegate_task) with external CLI invocations:
  - `claude -p` for security (300-600s timeout, stream-json)
  - `codex exec` for quality & tests (300-600s timeout, json output)
  - `agy --print` for architecture (300-600s timeout)
  - `kimi -p` for product scope (300-600s timeout, stream-json)
  - `opencode run` for cross-cutting (300-600s timeout)
- [x] 4.4 Add orchestrator inline review for spec compliance (Hermes does this directly)
- [x] 4.5 Update reviewer assignment table — assign Knowledge ↔ Code edge to Hermes (spec compliance lens)
- [x] 4.6 Update alignment-matrix-template.md with new edge
- [x] 4.7 Update review-plan-template.md with new edge
- [x] 4.8 Add pitfall: "delegate_task reviews fail with vars() serialization bug — always use external CLI agents"
- [x] 4.9 Add CLI budget guidance: "Give each reviewer 300-600s timeout. Reviews are reasoning-heavy."
- [x] 4.10 Add CLI availability check: "Run `command -v <cli>` before spawning. Mark unavailable CLIs as UNKNOWN."
- [x] 4.11 Add file-based context passing: "Write context to /tmp/openspec-review-<name>.md, pass via cat, NOT inline $CONTEXT"
- [x] 4.12 Add agentmemory filtering: "Extract only session metadata (title, date, outcome) — no raw content"
- [x] 4.13 Add context sanitization: "Redact IPs, credential URLs before external dispatch"

## Task 5: Update openspec-code-review — CLI-based reviews

- [x] 5.1 Add "Knowledge ↔ Code" as the 9th edge in the alignment matrix
- [x] 5.2 Update Step 4 (Collect Evidence) to include knowledge freshness checks
- [x] 5.3 Replace Step 5 (delegate_task) with external CLI invocations (same pattern as Task 4.3)
- [x] 5.4 Update reviewer assignment table — assign Knowledge ↔ Code edge to Hermes
- [x] 5.5 Update alignment-matrix-template.md with new edge
- [x] 5.6 Add CLI budget guidance (same as Task 4.9)
- [x] 5.7 Add CLI availability check (same as Task 4.10)
- [x] 5.8 Add file-based context passing (same as Task 4.11)

## Task 5b: Update hermes-skills spec

- [x] 5b.1 Update `openspec/specs/hermes-skills/spec.md` — change 8-edge alignment matrix to 9 edges (add Knowledge ↔ Code)
- [x] 5b.2 Update alignment matrix scenario descriptions to include Knowledge ↔ Code edge

## Task 6: Verify

- [x] 6.1 Run `openspec validate enhance-openspec-knowledge-tools --store openspec-store`
- [x] 6.2 Verify references are internally consistent — check these specific files:
  - `references/knowledge-tools-integration.md` (new) — all tool commands valid
  - `references/cross-repo-blast-radius-search.md` — cross-reference to new file works
  - `references/alignment-matrix-template.md` — 9 edges listed
  - `references/review-plan-template.md` — 9 edges listed
- [x] 6.3 Verify AGENTS.md word count stays ≤ 550 (no changes expected)
- [x] 6.4 Security verification: confirm no inline shell context passing in any SKILL.md
- [x] 6.5 Security verification: confirm agentmemory filtering documented in reference
