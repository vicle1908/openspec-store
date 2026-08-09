# Seven-CLI Verification Evidence

This directory contains the durable evidence that supersedes the inaccurate operational conclusions in `archive/2026-08-09-standardize-seven-cli-review-orchestration`.

## Run

```bash
# From the change directory
python3 verification/run_cli_reviews.py --round <round-name>
```

The runner invokes each CLI with its configured default model and provider. It does not pass model, provider, endpoint, API-key, reasoning, or permission-bypass overrides.

## Batch order

1. Claude, Agy, Goose
2. OpenCode, Codex, Kimi
3. Pi serially

No more than three CLIs run concurrently.

## Evidence layout

For each round and CLI:

- `smoke.stdout.txt`
- `smoke.stderr.txt`
- `smoke.meta.json`
- `review.stdout.txt`
- `review.stderr.txt`
- `review.meta.json`

The round also contains `summary.json` and, for the final harness, `summary.sha256`. The fixture SHA-256 binds every review to the retained `review-context.md`.

## Classification

A wrapper exit code is never sufficient. `PASS` and `PASS_WITH_FINDINGS` require a recognized verdict plus `FINDINGS:` and `RECOMMENDATIONS:` sections. Other classifications include `TIMEOUT`, `MISSING`, `INVOCATION_ERROR`, `PROCESS_ERROR`, `SEMANTIC_FAILURE`, `EMPTY_OUTPUT`, `CONFIG_ERROR`, `REJECTED`, and `HARNESS_ERROR`.

## Completion gate

Round 1 is diagnostic. Pi diagnostic 3 proves the Pi lifecycle repair. Rounds 6 and 7 are the authoritative consecutive final rounds: each contains seven smoke `PASS` results and seven reviews classified `PASS` or `PASS_WITH_FINDINGS`, with every review return code 0 and identical fixture/runner hashes.

## Safety

Retained evidence must not contain credentials. Public argv evidence replaces prompt text with its byte count and SHA-256. The runner uses no shell pipelines, captures stdout and stderr separately, and records the true child status before parsing.

## Canonical skill source

The repository `.hermes/skills/` tree is the tracked canonical source. `canonical-source-manifest.json` defines the managed source/install mapping. `sync_skills.py` copies those files to their installed Hermes locations and writes checksum evidence. Installed-only modifications are not considered durable.

Synchronization reports use stable atomic files at `sync-evidence/latest-apply.json` and `sync-evidence/latest-check.json`. Pre-install backups are stored outside Git under `~/.hermes/skill-backups/repair-seven-cli-review-verification/<timestamp>/`.

The check report is deterministic when source and installed hashes are unchanged; it uses portable source/install labels and does not embed a new timestamp on each read-only check.

## Authoritative retained results

- `results/round-1/` — diagnosis
- `results/pi-diagnostic-3/` — repaired Pi invocation
- `results/round-6/` — first clean full round
- `results/round-7/` — consecutive clean full round
- `final-findings-disposition.md` — final findings triage
