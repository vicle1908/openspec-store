# Tasks: standardize-agent-llm-environment-resolution-v2

## Phase 1: Native CLI research and conceptual mapping (complete)

- [x] 1.1 Research Codex, Grok Build, Kimi, and Pi configuration patterns.
- [x] 1.2 Identify provider definition → model alias → default selection pattern.
- [x] 1.3 Document native CLI versions and config structure.

## Phase 2: Current resolver implementation baseline (complete)

- [x] 2.1–2.8 Implement and test the six-layer resolver, provenance, secure config readers, dotenv authority, credential registry, CLI profile projection, and existing consumer wiring.

## Phase 3: Interim registry credential fix (complete — `d63aa08` lineage)

- [x] 3.1 Register custom provider credentials for legacy compatibility.
- [x] 3.2 Run consumer suites after the registry fix.

## Phase 4: New YAML provider/model/default schema (complete — current tdt-core `75cd519`)

- [x] 4.1–4.7 Implement typed provider/model/default schema, URL hardening, referential integrity, `auth_env`, protocol validation, alias semantics, migration compatibility, and focused parser/resolver tests.

## Phase 5: Registry retirement decision (complete — retained)

- [x] 5.1 Retain the registry for legacy aliases and CLI capability metadata.
- [x] 5.2 Keep new-schema `auth_env` provider-local.
- [x] 5.3 Defer removal until all legacy consumers migrate.
  - Evidence: successor `design.md`; no registry removal performed.

## Phase 6: CLI projections and consumer wiring (complete in successor)

- [x] 6.1 Add canonical per-CLI selection/projection through `project_canonical_cli_profile()`.
- [x] 6.2 Add independent per-CLI selection and no cross-contamination.
- [x] 6.3 Wire ai-harness-skills runtime boundary.
  - Evidence: `02d0410`; 606 collected, 602 passed, 0 failed, 4 skipped.
- [x] 6.4 Wire ai-review reviewer construction boundary.
  - Evidence: `bd27767`; 183 passed, 0 failed; source compilation, Ruff, and mypy clean.
- [x] 6.5 Handle model/effort capability differences for Claude/Codex and safe defaults for Kimi/Pi.

## Phase 7: Isolated TDT_HOME tests (complete — `21dcd5b` lineage)

- [x] 7.1–7.5 Isolated fixtures, six-layer precedence, credential non-disclosure, provenance, and cache isolation.

## Phase 8: Spec reconciliation (complete)

- [x] 8.1–8.10 Reconcile existing agent/config/provider specs against tdt-core implementation.

## Phase 9: Full downstream validation (complete)

- [x] 9.1 Integrated consumer suites: tdt-core 721/715/0/6; agent-core 746/746; agent-harness 343/343; agent-docs-sync 245/245; ai-review 183/183.
- [x] 9.2 Re-run consumer suites through the final new-schema path.
- [x] 9.3 Native Codex acceptance before consumer wiring: exit 0, nonce `TDT_8ef49e53`, 7.25s.
- [x] 9.4 Redacted diagnostics/provenance verification through both consumer launch boundaries.
  - Evidence: `~/Developer/tdt-cli-acceptance/verify_phase6_live.py`; nonce `TDT_PHASE6_AI_REVIEW_4cbec67f`; no credential leakage observed.

## Phase 10: Validation and delivery

- [x] 10.1 Focused OpenSpec change validation.
- [x] 10.2 Full-store validation run: 362 passed, 1 unrelated pre-existing failure in `standardize-omp-homebrew-installation`.
- [x] 10.3 Implementation/store diffs pass `git diff --check`.
- [x] 10.4 Archive parent and successor changes, then validate/synchronize canonical specs.
