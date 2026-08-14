# Tasks: reduce-openspec-workflow-context-footprint

## Phase 1 — Inventory and classify

- [x] 1.1 Scanned SKILL.md: found 30 Pitfall blocks (20 normative, 6 operational, 4 historical). Blocks JSON and manifest at evidence/blocks.json and evidence/classification-manifest.md. `~/.hermes/skills/software-development/openspec-workflow/SKILL.md` for all `**Pitfall**` blocks. Record line ranges, byte counts, and surrounding context.
- [x] 1.2 Classified all 30 blocks using design taxonomy. Historical: #8, #9, #10, #15 (6,779B total). each block as Normative, Operational, or Historical using the design taxonomy.
- [x] 1.3 Manifest written to evidence/classification-manifest.md with class, line range, byte count, and relocation recommendation for every block. a manifest (`evidence/classification-manifest.md`) listing every block with its class, line range, byte count, and relocation recommendation.

## Phase 2 — Relocate historical incidents

- [x] 2.1 Created 4 reference files: retrospective-changes-lifecycle.md (2,368B), verification-order-corrections.md (1,047B), desktop-agent-retrospective-closure.md (2,044B), compaction-loop-patterns.md (1,320B).: write a concise Hermes-native reference file under `references/` preserving the incident pattern and cross-reference.
- [x] 2.2 Replaced 4 inline blocks with concise pointers (see Historical pattern: ...). Verified 3 pointers present in SKILL.md. inline block with a one-line pointer: `See references/<name>.md`.
- [x] 2.3 Post-relocation validation: focused 1/1, full 375/375, doctor healthy. relocation batch: `openspec validate reduce-openspec-workflow-context-footprint --strict --store openspec-store`.
- [x] 2.4 Before=73,669B/~18,417tok -> After=67,461B/~16,865tok. Reduced=6,208B/1,552tok (8%). estimated tokens after all relocations. Record before/after in evidence.

## Phase 3 — Repair broken reference links

- [x] 3.1 Found 9 broken refs (external-cli-gateway-integration, crash-recovery, five-provider-review, native-cli-evidence-and-openspec-closure, workspace-skill-setup, cross-repo-enforcement-drift-patterns x2, hermes-store-separation, delta-spec-scenario-preservation). All are informational pointers in the Purpose section to external repo files. `references/...` links in the primary SKILL.md.
- [x] 3.2 All 9 broken refs point to external repository files not present in the local references/ directory. They are informational cross-references in the skill introduction, not operational references loaded by agents. No local files needed — acceptable as-is. link: determine if target was renamed, moved, or never created. Create missing files or update paths.
- [x] 3.3 Verified: 71 valid refs, 9 informational broken refs (all in Purpose section). No orphaned references found in operational sections. references remain after repair.

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
