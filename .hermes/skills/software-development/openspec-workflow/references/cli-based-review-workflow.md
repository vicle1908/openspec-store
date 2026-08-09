# CLI-Based OpenSpec Review Workflow

## Ground truth

Verified on 2026-08-09 with native subprocess status, separate stdout/stderr, retained metadata, and substantive review parsing.

| CLI | Binary | Version | Default-model review invocation |
|---|---|---:|---|
| Claude Code | `claude` | 2.1.226 | `claude -p "$PROMPT" --max-turns 5 --output-format text --no-session-persistence` |
| Codex | `codex` | 0.147.0 | `codex exec --ephemeral "$PROMPT"` |
| Antigravity | `agy` | 1.1.11 | `agy -p "$PROMPT" --output-format text --print-timeout 5m` |
| Kimi | `kimi` | 0.34.0 | `kimi -p "$PROMPT" --output-format text` |
| OpenCode | `opencode` | 1.18.15 | `opencode run "$PROMPT"` |
| Pi | `pi` | 0.84.1 | `pi -p --no-session --no-tools --no-extensions "$PROMPT"` |
| Goose | `goose` | 1.45.0 | `goose run --no-session -q --max-turns 10 -t "$PROMPT"` |

These commands use each CLI's configured default model and provider. Do not pass model, provider, endpoint, API-key, or reasoning overrides. Pi's extra flags are lifecycle/tool controls, not model overrides.

## Required execution model

1. Create a compact sanitized fixture under 20 KB.
2. Embed the fixture into the prompt so all CLIs receive identical content without filesystem-permission differences.
3. Run exact batches: Claude/Agy/Goose, OpenCode/Codex/Kimi, then Pi alone.
4. Use native subprocess timeouts; never pipe the child command through `head`, `tail`, or `tee` before capturing status.
5. Save stdout and stderr separately.
6. Retain executable path, version, timestamps, duration, true exit code, prompt/fixture/output SHA-256, and public argv flags.
7. Keep the fixture until every process terminates and every result is parsed.
8. A zero exit code is not sufficient. Require `VERDICT:`, `FINDINGS:`, and `RECOMMENDATIONS:` with substantive content.
9. Apply findings, rebuild the fixture, and run a second full round.

## Status contract

- `PASS`: exit 0, substantive `APPROVE`, no findings.
- `PASS_WITH_FINDINGS`: exit 0, substantive approved review with findings.
- `REJECTED`: substantive `REJECT`; reviewer works, artifact must be fixed and re-reviewed.
- `TIMEOUT`: native subprocess timeout.
- `MISSING`: executable absent/127.
- `INVOCATION_ERROR`: invalid flags or usage.
- `SIGNAL_TERMINATION`: child exited from a signal.
- `PROCESS_ERROR`: other nonzero process result.
- `SEMANTIC_FAILURE`: exit 0 but no valid review.
- `EMPTY_OUTPUT`: no meaningful output.
- `CONFIG_ERROR`: authentication/provider/default-config failure.

## Pi setup

Pi previously loaded 77 direct MCP tools because `~/.pi/agent/mcp.json` used `directTools: true`. The model produced valid output but headless processes did not terminate. Set `directTools: false` to use proxy mode. For bounded no-tool reviews use `--no-session --no-tools --no-extensions`; this preserves the configured default provider/model and exits cleanly.

## Identity rules

Kimi's executable is `kimi`. `fable-5` is a model alias, not an executable. Keep product, executable, provider, and model names distinct.

## Completion gate

Do not report all agents operational or archive the change until two full rounds contain seven smoke `PASS` results and seven review `PASS`/`PASS_WITH_FINDINGS` results, with actionable findings resolved and retained evidence internally consistent.
