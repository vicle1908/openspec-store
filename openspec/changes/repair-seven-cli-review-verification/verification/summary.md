# Seven-CLI Verification Summary

## Superseded evidence

This repair supersedes the operational conclusions in `archive/2026-08-09-standardize-seven-cli-review-orchestration`. That archive used shell pipelines that masked child status, removed a shared fixture before every result was parsed, invoked Kimi as the nonexistent `fable-5` executable, and marked pending or invalid results complete. See `erratum.md`.

## Root causes and fixes

1. **Masked exit status** — replaced shell pipelines with a Python subprocess harness that retains true child return code, stdout, stderr, version, duration, hashes, and parsed status.
2. **Kimi identity** — verified Kimi executable `kimi` v0.34.0; removed current operational `fable-5 -p` guidance.
3. **Agy semantic diversion** — read-only review uses configured defaults and does not pass or discuss permission-bypass flags.
4. **Pi lifecycle defect** — Pi's configured model/provider responded, but `directTools: true` registered 77 MCP tools and kept headless processes alive. Set `directTools: false` in `~/.pi/agent/mcp.json`; bounded reviews use `--no-session --no-tools --no-extensions` without model/provider overrides.
5. **Installed-only skill edits** — established a Git-tracked canonical source under `.hermes/skills/`, added checksum synchronization, and verified all managed installed copies match.

## Authoritative evidence

### Round 1 — diagnosis

- Claude, Codex, Agy, Kimi, OpenCode, and Goose: smoke `PASS`; substantive review `PASS_WITH_FINDINGS`.
- Pi: model produced smoke and substantive output, but the process did not terminate under the 77-direct-tool setup. The retained status is non-passing.

### Pi diagnostic 3 — repaired invocation

After MCP proxy-mode and lifecycle fixes, Pi v0.84.1 completed smoke `PASS` and review `PASS_WITH_FINDINGS`, return code 0, using its configured default model/provider.

### Round 6 — first clean full round

Fixture SHA-256: `a5a8551417c662a4dfda064bd885d5cfd1d1729c3daa08685b1e2f50cc45b472`

Runner SHA-256: `c59819c09dd99ef37ffb22f95dfaa2657bbd038dc1be63a6c5fbefd59f973793`

| CLI | Smoke | Review | Verdict | Return code |
|---|---|---|---|---:|
| Claude | PASS | PASS | APPROVE | 0 |
| Codex | PASS | PASS_WITH_FINDINGS | APPROVE_WITH_CONDITIONS | 0 |
| Agy | PASS | PASS_WITH_FINDINGS | APPROVE_WITH_CONDITIONS | 0 |
| Kimi | PASS | PASS | APPROVE | 0 |
| OpenCode | PASS | PASS | APPROVE | 0 |
| Pi | PASS | PASS_WITH_FINDINGS | APPROVE_WITH_CONDITIONS | 0 |
| Goose | PASS | PASS_WITH_FINDINGS | APPROVE_WITH_CONDITIONS | 0 |

### Round 7 — consecutive clean full round

Used the identical fixture and runner hashes as Round 6.

| CLI | Smoke | Review | Verdict | Return code |
|---|---|---|---|---:|
| Claude | PASS | PASS_WITH_FINDINGS | APPROVE_WITH_CONDITIONS | 0 |
| Codex | PASS | PASS_WITH_FINDINGS | APPROVE_WITH_CONDITIONS | 0 |
| Agy | PASS | PASS | APPROVE | 0 |
| Kimi | PASS | PASS | APPROVE | 0 |
| OpenCode | PASS | PASS_WITH_FINDINGS | APPROVE_WITH_CONDITIONS | 0 |
| Pi | PASS | PASS | APPROVE | 0 |
| Goose | PASS | PASS_WITH_FINDINGS | APPROVE_WITH_CONDITIONS | 0 |

Both full rounds meet the gate: seven smoke `PASS`, seven review `PASS`/`PASS_WITH_FINDINGS`, and seven review return codes 0.

## Current default-model commands

```text
claude -p PROMPT --max-turns 10 --output-format text --no-session-persistence
codex exec --ephemeral PROMPT
agy -p PROMPT --output-format text --print-timeout 5m
kimi -p PROMPT --output-format text
opencode run PROMPT
pi -p --no-session --no-tools --no-extensions PROMPT
goose run --no-session -q --max-turns 10 -t PROMPT
```

No command passes a model/provider override.

## Durable surfaces

- Canonical skills: repository `.hermes/skills/`
- Installed skills: `~/.hermes/skills/`
- Source/install mapping: `verification/canonical-source-manifest.json`
- Checksum evidence: `verification/sync-evidence/`
- Pi config mutation evidence: `verification/pi-config-change.json`
- Raw/redacted CLI evidence: `verification/results/{round-1,pi-diagnostic-3,round-6,round-7}/`

## Final conclusion

All seven CLI agents are able to run noninteractively with their configured default model/provider and produce substantive review output under the documented bounded invocations. The prior false timeout/pending/missing-binary conclusions are superseded.
