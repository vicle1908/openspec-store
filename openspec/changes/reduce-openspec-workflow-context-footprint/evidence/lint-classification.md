# Documentation Lint Classification

## Current baseline

- Scanner: `~/.hermes/skills/software-development/openspec-workflow/scripts/openspec_doc_lint.py`
- Scan scope: active Markdown guidance and references; `tests/fixtures/` excluded from production scans.
- Total findings: 39
- Actionable findings: 0
- Informational findings: 39
- Regression test: `tests/test_doc_lint_regression.py` → PASS

## Severity rules

- **Actionable:** active guidance prescribes a masked pipeline, unscoped staging, planning-status conflation, or archive-preview misuse.
- **Informational:** warning/negation text, historical/reference material, or fixture content.
- **Baseline:** pre-existing informational findings are retained for traceability and do not block closure.

## Repaired links

The 9 previously missing links in the primary SKILL.md were repaired:

| Previous target | Replacement |
|---|---|
| `external-cli-gateway-integration.md` | `coding-agent-cli-provider-integration.md` |
| `crash-recovery.md` | `crash-recoverable-filesystem-migration-design.md` |
| `five-provider-review.md` | `five-provider-review-orchestration.md` |
| `native-cli-evidence-and-openspec-closure.md` | `cli-based-review-workflow.md` |
| `workspace-skill-setup.md` | `workspace-agent-skills-setup.md` |
| `cross-repo-enforcement-drift-patterns.md` (2) | `cross-repo-cleanup-workflow.md` |
| `hermes-store-separation.md` | newly created local reference |
| `delta-spec-scenario-preservation.md` | `delta-modified-scenario-rule.md` |

Final local reference scan: 0 missing targets.
