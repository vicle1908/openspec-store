# Tasks: reduce-openspec-workflow-context-footprint

## Phase 1 — Inventory and classify

- [ ] 1.1 Scan `~/.hermes/skills/software-development/openspec-workflow/SKILL.md` for all `**Pitfall**` blocks. Record line ranges, byte counts, and surrounding context.
- [ ] 1.2 Classify each block as Normative, Operational, or Historical using the design taxonomy.
- [ ] 1.3 Build a manifest (`evidence/classification-manifest.md`) listing every block with its class, line range, byte count, and relocation recommendation.

## Phase 2 — Relocate historical incidents

- [ ] 2.1 For each Historical block: write a concise Hermes-native reference file under `references/` preserving the incident pattern and cross-reference.
- [ ] 2.2 Replace each relocated inline block with a one-line pointer: `See references/<name>.md`.
- [ ] 2.3 Validate after each relocation batch: `openspec validate reduce-openspec-workflow-context-footprint --strict --store openspec-store`.
- [ ] 2.4 Measure bytes and estimated tokens after all relocations. Record before/after in evidence.

## Phase 3 — Repair broken reference links

- [ ] 3.1 Identify all broken `references/...` links in the primary SKILL.md.
- [ ] 3.2 For each broken link: determine if target was renamed, moved, or never created. Create missing files or update paths.
- [ ] 3.3 Verify no orphaned references remain after repair.

## Phase 4 — Lint context-awareness and regression tests

- [ ] 4.1 Add severity classification (actionable / informational / baseline) to `openspec_doc_lint.py` findings.
- [ ] 4.2 Record the approved baseline of existing findings. Gate passes only when new actionable count is 0.
- [ ] 4.3 Write executable Python regression tests (not just Markdown scenarios) that verify the lint catches real anti-patterns and ignores negations.
- [ ] 4.4 Integrate regression tests into the pre-archive gate script.

## Phase 5 — Final verification and closure

- [ ] 5.1 Run focused validation, full-store validation, store doctor, and gate script.
- [ ] 5.2 Measure final byte/token count of primary SKILL.md. Record reduction percentage.
- [ ] 5.3 Verify Hermes skill loading after restructuring: all 4 custom skills load correctly.
- [ ] 5.4 Run documentation lint. Confirm actionable count is 0.
- [ ] 5.5 Commit owned artifacts. Archive only when all tasks are genuinely complete.
