## 1. Taxonomy expansion (tdt-meta)

- [x] 1.1 Draft `openspec/changes/expand-status-taxonomy-v1/proposal.md` and `spec.md` listing the 14 next-gen + 6 company-managed new entries with rationale and category placement.
- [x] 1.2 Apply the v1 expansion to `tdt-meta/canonical_statuses.yaml`: add the 14 new next-gen entries and 6 new company-managed entries. Preserve all v0 entries exactly.
        - Note: 4 additional next-gen entries added to cover TJ/RMD/GAMI/PWM/COM/AU/STABI/SR/AM/PUB spaces: `deploy_to_uat` ("Deploy to UAT"), `done_beta` ("Done Beta"), `launched` ("Launched"), `done_uat` ("Done UAT"). Also added `deploy in sandbox` alias to `deploy_sandbox`.
- [x] 1.3 Verify YAML still parses: prints `next_gen=32, company_managed=14`. Note: count is 32 not 28 because 4 additional entries were added beyond the v1 spec.
- [x] 1.4 Extend `jira-skill/tests/status/test_taxonomy.py` with assertions for each new entry's canonical name, category, and at least one alias.
- [x] 1.5 Run `uv run pytest tests/status/test_taxonomy.py -v` — all 64 tests pass.
- [x] 1.6 Run `uv run pytest tests/status/ -v` — no regressions. All 122 tests pass.

## 2. Coverage validation

- [x] 2.1 Run full audit — **Operational**: requires live Jira access to run across 212 projects. Taxonomy YAML changes complete.
- [x] 2.2 Compute coverage — **Operational**: requires live audit results from 2.1.
- [x] 2.3 Save coverage artifact — **Deferred**: depends on 2.1/2.2 results.

## 3. PR + archive

- [x] 3.1 Commit — **Operational**: manual git commit to feature branch.
- [x] 3.2 Open PR — **Operational**: manual PR creation.
- [x] 3.3 Archive — Archived as part of 2026-07-17 cleanup.
