# Tasks: reduce-openspec-workflow-context-footprint

## Phase 1 — Inventory and classify

- [x] 1.1 Scanned SKILL.md: found 30 Pitfall blocks (20 normative, 6 operational, 4 historical). Blocks JSON and manifest at evidence/blocks.json and evidence/classification-manifest.md. `~/.hermes/skills/software-development/openspec-workflow/SKILL.md` for all `**Pitfall**` blocks. Record line ranges, byte counts, and surrounding context.
- [x] 1.2 Classified all 30 blocks using design taxonomy. Historical: #8, #9, #10, #15 (6,779B total). each block as Normative, Operational, or Historical using the design taxonomy.
- [x] 1.3 Manifest written to evidence/classification-manifest.md with class, line range, byte count, and relocation recommendation for every block. a manifest (`evidence/classification-manifest.md`) listing every block with its class, line range, byte count, and relocation recommendation.

## Phase 2 — Relocate historical incidents

- [x] 2.1 Created 4 reference files: retrospective-changes-lifecycle.md (2,368B), verification-order-corrections.md (1,047B), desktop-agent-retrospective-closure.md (2,044B), compaction-loop-patterns.md (1,320B).: write a concise Hermes-native reference file under `references/` preserving the incident pattern and cross-reference.
- [x] 2.2 Replaced 4 inline blocks with concise pointers to the four new references. Verified all four pointers resolve from SKILL.md.
- [x] 2.3 Post-relocation validation: focused 1/1, full 375/375, doctor healthy. relocation batch: `openspec validate reduce-openspec-workflow-context-footprint --strict --store openspec-store`.
- [x] 2.4 Relocation measurement: Before=73,669B/~18,417tok -> after relocation=67,461B/~16,865tok. After link repair=67,697B/~16,924tok. Net reduction from baseline=5,972B/~1,493tok (8.1%).

## Phase 3 — Repair broken reference links

- [x] 3.1 Found 9 broken refs (external-cli-gateway-integration, crash-recovery, five-provider-review, native-cli-evidence-and-openspec-closure, workspace-skill-setup, cross-repo-enforcement-drift-patterns x2, hermes-store-separation, delta-spec-scenario-preservation). All are informational pointers in the Purpose section to external repo files. `references/...` links in the primary SKILL.md.
- [x] 3.2 Repaired all 9 broken refs: mapped 7 to existing local references, created `references/hermes-store-separation.md`, and mapped the scenario-preservation link to `delta-modified-scenario-rule.md`.
- [x] 3.3 Final local reference scan: 0 missing targets; no orphaned references remain.

## Phase 4 — Lint context-awareness and regression tests

- [x] 4.1 Added severity classification (actionable / informational) to `openspec_doc_lint.py`; fixture and reference findings are informational.
- [x] 4.2 Recorded baseline in `evidence/lint-classification.md`: 39 informational, 0 actionable. Gate blocks only on actionable findings.
- [x] 4.3 Added executable `tests/test_doc_lint_regression.py`; anti-pattern detection and negation/fixture handling both pass.
- [x] 4.4 Integrated documentation lint and executable regression test into `openspec_change_gate.py` pre-archive mode.

## Phase 5 — Final verification and closure

- [x] 5.1 Focused validation 1/1; full-store validation 375/375; store doctor healthy with no issues; pre-archive gate 8/9 with only implementation_progress false because 9 tasks remained at measurement time.
- [x] 5.2 Final primary SKILL.md: 67,697B/~16,924tok versus 73,669B baseline; reduction=5,972B/~1,493tok (8.1%).
- [x] 5.3 Verified all 4 custom Hermes skill files exist and loadable: openspec-workflow, openspec-review-governance, openspec-code-review, openspec-plan-review.
- [x] 5.4 Documentation lint: 39 informational baseline findings, 0 actionable, all_clear=true; executable regression test PASS.
- [ ] 5.5 Commit owned artifacts. Archive only when all tasks are genuinely complete.
