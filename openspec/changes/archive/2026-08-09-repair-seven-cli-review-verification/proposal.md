# Proposal: Repair Seven-CLI Review Verification

## Why

The archived change `2026-08-09-standardize-seven-cli-review-orchestration` contains invalid verification evidence. Its shell pipelines captured the status of `tail`, not the reviewer process; the review fixture was deleted before every background process was parsed; Kimi was invoked as the nonexistent `fable-5` executable; Agy received and then discussed a permission-bypass flag; and several agents were classified before their runs completed. The archive consequently claimed completion without evidence that all seven CLIs could perform a substantive review.

This change supersedes those operational claims without rewriting historical commits.

## What Changes

- Add a durable verification fixture, runner, parser, raw outputs, metadata, and consolidated summary.
- Verify Claude, Codex, Agy, Kimi, OpenCode, Pi, and Goose using configured default models with no model/provider override.
- Capture the real child exit code before any filtering, with separate stdout and stderr.
- Classify each run as PASS, PASS_WITH_FINDINGS, TIMEOUT, MISSING, INVOCATION_ERROR, SEMANTIC_FAILURE, EMPTY_OUTPUT, or CONFIG_ERROR.
- Require two rounds in which all seven reviewers reach PASS or PASS_WITH_FINDINGS.
- Correct stale operational references, especially `fable-5 -p`, premature timeout/pending claims, and wrapper `EXIT:0` claims.
- Update the tracked canonical skill source when identified, synchronize installed copies, and retain checksum evidence.

## Scope

This is an operational skills, documentation, and verification repair. It does not change product behavior or introduce a durable product capability, so `skip_specs: true` applies.

## Success Criteria

The change is complete only when both verification rounds contain seven substantive reviews classified PASS or PASS_WITH_FINDINGS, all actionable findings are resolved, installed skill copies match their durable source, focused validation passes, and the change is archived and committed.
