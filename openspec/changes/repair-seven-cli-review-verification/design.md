# Design: Repair Seven-CLI Review Verification

## Context

The superseded verification used shell pipelines whose final status was the status of `tail`, not the reviewer process. It deleted the fixture before all background reviewers were parsed, invoked Kimi using a model alias instead of `kimi`, passed Agy a distracting permission flag, and marked pending or invalid evidence complete.

## Decisions

### Preserve history and supersede conclusions

The prior archive remains immutable historical evidence. `erratum.md` declares its operational conclusions invalid; this repair supplies replacement evidence.

### Use a compact embedded fixture

`verification/review-context.md` is UTF-8, below 20 KB, and embedded identically in every review prompt. This avoids cross-CLI filesystem permission differences. The runner retains its hash and checks it before and after each round.

### Capture native process evidence

`verification/run_cli_reviews.py` uses direct Python subprocess execution without shell pipelines. It retains separate stdout/stderr, true return code, timeout/signal state, timestamps, elapsed duration, executable path/version/hash, public argv with prompt hash, stream sizes/hashes, and parsed verdict/status.

A zero return code is insufficient. Smoke requires `CONNECTION_OK`; review requires one recognized verdict and substantive findings/recommendations.

### Use configured defaults

No invocation passes model, provider, endpoint, API key, or reasoning overrides. Noninteractive, session, tool/extension, output, turn, and timeout controls are allowed because they do not select the provider/model.

### Run bounded batches

1. Claude, Agy, Goose
2. OpenCode, Codex, Kimi
3. Pi alone

No more than three run concurrently.

### Repair Pi at the configuration/lifecycle layer

Pi's default provider/model responded, but `directTools: true` registered 77 MCP tools and kept bounded print-mode processes alive. The repair set `directTools: false` in `~/.pi/agent/mcp.json`, preserving provider/model defaults. Bounded no-tool reviews use `--no-session --no-tools --no-extensions`.

### Establish durable canonical skills

The repository `.hermes/skills/` tree is the tracked canonical source for the managed guides. `verification/sync_skills.py` backs up installed copies, installs the canonical files, and verifies source/install SHA-256 values. Installed-only edits are not durable evidence.

### Require two consecutive clean rounds

Round 1 diagnosed setup defects. Pi diagnostic 3 proved the Pi repair. Rounds 6 and 7 are consecutive full accepted rounds with identical fixture and runner hashes. Each contains seven smoke `PASS` results and seven review `PASS`/`PASS_WITH_FINDINGS` results with return code 0.

## Classification

Accepted: `PASS`, `PASS_WITH_FINDINGS`.

Non-passing: `REJECTED`, `TIMEOUT`, `MISSING`, `INVOCATION_ERROR`, `SIGNAL_TERMINATION`, `PROCESS_ERROR`, `SEMANTIC_FAILURE`, `EMPTY_OUTPUT`, and `CONFIG_ERROR`.

## Rollback

The Pi config backup is stored outside Git under `~/.pi/agent/backups/` with mode 0600. Skill synchronization retains timestamped checksum evidence. Any source/install mismatch blocks completion.

## Verification evidence

Authoritative evidence is retained under:

- `verification/results/round-1/`
- `verification/results/pi-diagnostic-3/`
- `verification/results/round-6/`
- `verification/results/round-7/`
- `verification/summary.md`
- `verification/sync-evidence/`
- `verification/pi-config-change.json`
