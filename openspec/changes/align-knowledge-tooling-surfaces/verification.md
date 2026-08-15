# Verification: align-knowledge-tooling-surfaces

Date: 2026-08-15

## Ground truth

- Graphify: `graphify 0.9.42`
- Distribution: `graphifyy v0.9.42`
- Managed Python: `3.12.13`
- GitNexus: `1.6.9`
- OpenSpec: `1.9.0`
- skills CLI: `1.5.22`

## Focused checks

- `bash scripts/tests/knowledge-tools-test.sh` — exit 0; final line reported `status=passed`, including fail-visible refresh, guarded setup, unique snapshots, idempotent hooks, lifecycle, redaction, and boundary checks.
- `bash -n scripts/knowledge-tools.sh scripts/tests/knowledge-tools-test.sh` — exit 0.
- `python3 -m json.tool scripts/config/agent-skill-surfaces.json` — exit 0.
- Tracked `.gitattributes` audit — 17/17 valid; exactly one `graphify-out/graph.json merge=graphify`, no `.graphify/graph.json`, no `merge=graphify-json`.
- Current OpenSpec path audit — zero `.graphify/graph.json` references in main specs.
- Current go-microservices and main-spec stale sweep — zero old provider/version/weekly-cron hits.

## OpenSpec checks

- `openspec validate align-knowledge-tooling-surfaces --strict` — pass.
- Focused validation for four edited specs — pass.
- `openspec validate --all --strict` — 375 passed, 0 failed.

## Owning commits

- `go-microservices`: `002ab2f34d08a96d824fc6e619150ff6eedf078b`
- `agent-core`: `053edb665ace70315a2f5e70ab94ca3949629c5d`
- `agent-docs-sync`: `6ca68f1e0960952521ea4adf414149d2b0ab2511`
- `agent-harness`: `af3aa94a9ffccc3ae0138f67bc1e031027e0e21e`
- `ai-harness-skills`: `b9d3c8af937bd7463872dd070c819d6609d17f91`
- `ai-review`: `4f5258073964196e29b89d005e489f7c427a7160`
- `browser-cli`: `fd7bbbc08d39850d95f979f72672b2f72402522f`
- `code-daily-scan`: `fb8b419ec7d81b45014eb541943e2456e2934f1f`
- `jira-daily-reports`: `63541bcc19ea5c565c7240b4d197181ac3455287`
- `jira-epic-report`: `ca22584890aabfb229dfe23be13eb5533159d09e`
- `jira-kanban-from-spreadsheet`: `eb48d7e8a09461ba218a2ae701da22244f7c21fa`
- `jira-skill`: `130ae28a76d610227ec4956a3a716cecbb90a642`
- `ops-automation-suite`: `51f867db31a9ec1d2aeb46bc20bc5e689ca978b0`
- `tdt-core`: `4ffa354d681c723e2d94c9724074195a70d78284`
- `tdt-observability`: `b446b093837362905a451c066d0b3f130b1d1440`
- `tdt-sheets`: `feec0290b73f1a817a5ae628e3436f4fcc8fc52b`
- `webhook-receiver`: `b3e4d4957f21dbbb7ca0d7278fa99401a3dd5848`

## Review limitations

GitNexus semantic change detection was available for `openspec-store` and returned low risk with no affected execution flows. `go-microservices` is not currently present in the GitNexus registry; its shell syntax, focused fixture, JSON, diff, and scoped-path checks are the available review evidence. Generated Graphify output and unrelated user-local configuration remain intentionally dirty and were not staged.
