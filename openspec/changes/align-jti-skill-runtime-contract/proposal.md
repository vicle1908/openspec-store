## Why

The `jira-ticket-intelligence` skill and its OpenSpec contract describe a v2.0 RCA and Sheets surface, but the shipped `jira-skill` runtime still reports v1.2, exposes the older ten-category taxonomy, and writes 26 rather than 28 classification columns. At the same time, the skill frontmatter exceeds the loader's 1,024-byte description limit and the generated skill index mis-parses YAML block scalars as the literal value `>-`.

This change is needed now because agents can be routed using incomplete metadata and consumers can be guided toward a contract that the runtime does not produce. The existing v2.0 contract remains the intended target; this change makes that target real and verifies it across the editable consumer repos.

## What Changes

- **BREAKING**: Complete and publish the v2.0 `TicketIntelligenceBundle` contract in `jira-skill`, including the eight-category RCA taxonomy, distinct unclassified sentinel, calibrated confidence mapping, and v2.0 bundle version.
- Add the v2 RCA fields to all required bundle/summary surfaces and make `secondary_categories` deterministic, deduplicated, priority-ordered, and capped at three entries.
- **BREAKING**: Extend the Sheets Classification schema from 26 to 28 columns with `RCA 4P Lens` and `Secondary RCA`, keeping row/header alignment and downstream output tests consistent.
- Update the editable `jira-epic-report`, `jira-daily-reports`, and `webhook-receiver` compatibility tests and documentation for the v2.0 contract without duplicating core analysis logic.
- Replace the long skill description with a concise routing description below the loader limit, keep detailed contract material in the skill body/reference documentation, and remove stale claims such as the 10-versus-9 signal-family count and 24/26/28 column contradictions.
- Fix the skill-index parser to support the six supported YAML block-scalar forms (`>`, `>-`, `>+`, `|`, `|-`, `|+`) and add metadata/index validation for description length, parse correctness, duplicate names, invalid skill placement, and generated-entry freshness.
- Retire the duplicate `_regenerate_index.py` writer and unused `config/codex/skills-index.json` snapshot, remove the exact duplicate root-level `.agents/skills/SKILL.md`, and rebuild the canonical indexes from the 131 valid directory-owned skills (versus 103 in the stale generated indexes).
- Align the runtime docs, OpenSpec contract references, generated indexes, and verification commands around one canonical contract source.
- Reconcile the older JTI accuracy, impact-Sheets, and RCA test-coverage specifications whose current requirements still assert v1.2, removed category names, obsolete column positions, or a nonexistent 65-case survey (the executable survey currently contains 45 cases).

## Non-goals

- No new Jira, GitLab, Google Sheets, or Python package dependencies.
- No change to Jira collection, authentication, filter discovery, dashboard automation, or consumer-local policy behavior.
- No full source-code semantic RCA engine; existing deterministic ticket/SCM evidence boundaries remain unchanged.
- No migration of launchd or Docker scheduling services.

## Capabilities

### New Capabilities

- `skill-index-hygiene`: deterministic parsing, validation, and generation of TDT skill metadata indexes, including the 1,024-byte description limit and YAML block scalar support.

### Modified Capabilities

- `ticket-intelligence-core`: publish the v2.0 RCA taxonomy, signal fields, severity confidence mapping, deterministic secondary-cause behavior, and 28-column Sheets rendering as the shipped shared contract.
- `jti-classification-accuracy`: align RCA evidence positions, v2 category migration, 4P/secondary field ownership, and the classification-quality gate with the executable v2 taxonomy.
- `impact-sheet-integration`: preserve v1.1/v1.2 deserialization history while changing current runtime expectations to v2.0 and correcting the 28-column positional contract.
- `fix-rca-fix-status-detection`: replace the obsolete nine-category test matrix with the seven concrete v2 categories plus the distinct unclassified sentinel.

All four modified capabilities have matching delta spec files so the current-version requirements can be merged and validated together before implementation.

## Impact

- **Runtime:** `jira-skill/src/jira_skill/analysis/{bundle.py,rca.py,signals.py,extractors/rca_patterns.py,sheets_writer.py,analyzer.py,VERSIONING.md}` and related fixtures and analysis tests.
- **CLI/output:** `jira-skill` version reporting, `analyze-filter`, Sheets writers, fixture expectations, and classification helper scripts.
- **Consumers:** editable dependencies in `jira-epic-report`, `jira-daily-reports`, and `webhook-receiver`. No consumer currently branches on RCA category names or Classification column positions; only `webhook-receiver` has an explicit `v1` assertion, so consumer implementation risk is narrower than the shared-contract surface suggests.
- **Skills tooling:** `tdt-meta/.agents/skills/jira-ticket-intelligence/SKILL.md`, the stray duplicate `.agents/skills/SKILL.md`, `tdt-meta/config/codex/scripts/{build-skills-index.sh,skill-validation-check.sh}`, a standard-library Python generator/test entry point, the duplicate `.agents/skills/_regenerate_index.py`, the canonical `.codex/skills-index.json`, both Markdown skill indexes, and the unused `config/codex/skills-index.json` artifact. The audited workspace has 131 valid directory-owned skills plus one duplicate root-level `SKILL.md`, while every generated canonical index still reports 103.
- **Documentation/specs:** `jira-skill/docs/bundle-contract.md`, `analysis/VERSIONING.md`, the JTI skill references, and four existing JTI capability specs whose version/category/column requirements overlap.
- **Sheets migration:** `SheetsWriter` currently clears only `A:Z`; the v2 columns occupy `AA:AB`, so the write/rollback plan must clear the full 28-column range to prevent stale tail cells.
- **Blast radius:** GitNexus reports LOW risk for each targeted symbol, with 5 upstream dependencies for `BundleVersion`, 3 for `detect_rca`, 7 for `RootCauseSignal`, and 9 for `SheetsWriter.write_bundle`; the combined contract change affects the `analyze_filter` process and multiple consumer test suites, so it requires coordinated verification.
