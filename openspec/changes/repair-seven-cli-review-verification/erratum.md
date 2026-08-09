# Erratum: Seven-CLI Review Verification

This document supersedes the operational conclusions in:

`openspec/changes/archive/2026-08-09-standardize-seven-cli-review-orchestration/`

The earlier archive is retained as immutable history, but its verification summary and completion claims are not valid evidence.

## Invalid prior claims

- Wrapper `EXIT:0` values were reported as CLI success even though shell pipelines returned the status of `tail`.
- Codex, Pi, and OpenCode were labeled TIMEOUT without preserved child exit status.
- Goose was archived as pending while tasks were marked complete.
- Kimi was invoked using `fable-5`, which is a model alias and not an installed executable.
- Claude's recorded verdict was REJECT, not PASS.
- Agy's output primarily discussed an invocation flag rather than performing the requested review.
- The fixture was removed before all background processes had been fully parsed.
- The archive claimed all tasks complete despite unresolved and invalid evidence.

## Replacement evidence

Only evidence under this repair change's `verification/results/` directory is authoritative for current seven-CLI capability. Every accepted result must contain the true child process status and a substantive parsed verdict. The repair change remains active until two rounds demonstrate seven PASS/PASS_WITH_FINDINGS classifications.
