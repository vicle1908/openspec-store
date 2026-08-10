# Implementation Evidence: Reconcile MoA Documentation Surfaces

Evidence captured on 2026-08-10. Credential values, authorization headers, user identifiers, and private payloads are excluded.

## Audit Result

The live configuration already matched the canonical MoA contract; no live config mutation was performed.

- Primary: `model.provider: moa`, `model.default: default`.
- `moa.default_preset: default`.
- `moa.privacy_filter: display`.
- Default aggregator: `shopapikey:fable-5`, `reasoning_effort: max`.
- Deep aggregator: `giaoduc:Advance`, `reasoning_effort: max`.
- Fast aggregator: `shopapikey:fable-5`, `reasoning_effort: high`.
- Cockpit provider default: `gpt-5.6-luna`.
- Provider context declarations: cockpit, shopapikey, and giaoduc each `1000000`.
- No MoA reference or aggregator slot contains `context_length`.
- `hermes moa list` normalized to the same three aggregators and efforts.
- Existing runbook and canonical spec already described the target aggregator assignments.

## Actionable Drift Corrected

Maintained reference updated:

`/Users/androidteam/.hermes/skills/software-development/openspec-workflow/references/hermes-moa-configuration.md`

Corrections:

1. Removed `context_length` from the generic MoA slot example.
2. Replaced the slot-level context tuning row with provider/model-level ownership guidance.
3. Replaced the stale “set context on every slot” pitfall with the current provider-level contract.
4. Replaced the direct hand-edit Python example with scalar leaf-setter guidance and an agent-only atomic recovery path requiring backup and YAML shape validation.

Reviewed unchanged maintained surfaces:

- `openspec/specs/hermes-moa-configuration/spec.md`
- `docs/governance/hermes-moa-configuration.md`
- `~/.hermes/skills/autonomous-ai-agents/hermes-agent/references/configuration.md`
- `~/.hermes/skills/autonomous-ai-agents/hermes-agent/references/providers-and-models.md`

Archived historical changes were not rewritten. Historical model names remain classified as historical evidence rather than active selections.

## Provider Health

Fresh direct non-streaming inference checks passed:

| Provider/model | Result | HTTP | Latency |
|---|---|---:|---:|
| shopapikey / `fable-5` | PASS | 200 | 1702 ms |
| giaoduc / `Advance` | PASS | 200 | 1069 ms |
| cockpit / `gpt-5.6-luna` | PASS | 200 | 5095 ms |

These checks establish availability and usable response shape, not comparative model quality.

## Real MoA Tool-Loop Evidence

### Default

Session: `@session:default/20260810_122437_048e5e`

- Assistant emitted a `terminal` function call.
- Tool returned `MOA_DOC_DEFAULT_OK`, exit code 0.
- Assistant continued with `MOA_DOC_DEFAULT_SMOKE_OK`.

### Deep

Session: `@session:default/20260810_122518_2dd232`

- Assistant emitted a `terminal` function call after the three references ran.
- Tool returned `MOA_DOC_DEEP_OK`, exit code 0.
- Assistant continued with `MOA_DOC_DEEP_SMOKE_OK`.

## Structural Evidence

- `hermes config check`: exit 0; only the known schema `33 -> 34` update-available notice remains.
- `hermes moa list`: exit 0; default and deep aggregators match the target.
- `hermes fallback list`: exit 0; primary `default` via MoA and fallback order `shopapikey`, `giaoduc`, then `cockpit`.
- Maintained skill-reference SHA-256 after correction: `b05e58a6368afc77e45de2f12ecbdc7af64bdce567a2647234fe6f34d748ca07`.
- Canonical spec strict validation: pass.
- All 340 main specs strict validation: pass.
- Full store baseline: one unrelated active-change failure remains at `align-jti-skill-runtime-contract`; it is outside this documentation slice.
- `openspec store doctor`: exit 0; no store issues.
- Local `main` and `origin/main`: equal before this change.

## Unrelated Work Preserved

The store contained unrelated untracked work and active changes, including `ecosystem-standardization` and the archived `consolidate-ecosystem-shared-code` directory. None was edited, staged, or removed by this change.

## Independent Review Disposition

- Claude Code 2.1.226: **APPROVE with minor metadata cleanup**. Confirmed the context correction, recovery wording, scope, evidence honesty, and complete agent-loop section. Its optional recommendation to move the context note out of the tuning table was applied.
- Antigravity 1.1.11 initial review: **CONDITIONAL APPROVAL**. Its valid findings were task/evidence synchronization and the external-surface diff accounting. Its “proposal frontmatter must contain `skip_specs`” finding is **not applicable**: OpenSpec stores that field in `.openspec.yaml`, and `openspec validate reconcile-moa-documentation-surfaces --strict` passes. Refreshed Antigravity review: **NOT_REVIEWED** because headless mode denied its `read_file` permission and produced no substantive report.
- Claude Code 2.1.226 refreshed review: **APPROVE**. Confirmed all prior findings resolved, the complete seven-step agent-loop section, the final SHA-256, task/evidence state, scope, and historical classification.
- Goose 1.45.0: **NOT_REVIEWED**. The native process exited without substantive `VERDICT`, `FINDINGS`, and `RECOMMENDATIONS`; it attempted an unrelated tool-driven workflow instead of returning a review. Its output is not approval evidence.

The maintained skill directory is intentionally outside Git, so Git cannot produce a source diff for that file (`git rev-parse --is-inside-work-tree` returns the expected not-a-repository result). The changed surface is therefore bound by its absolute path, exact correction summary, and post-change SHA-256 above; the OpenSpec change record and archive are the committed audit trail.

## Rollback

The only modified external surface is the maintained skill reference. Rollback is a targeted replacement of that file using its pre-change content; no live Hermes configuration or credentials were changed.
