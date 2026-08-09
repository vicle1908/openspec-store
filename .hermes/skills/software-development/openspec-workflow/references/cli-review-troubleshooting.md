# CLI Review Troubleshooting

## Verified baseline (2026-08-09)

All seven coding-agent CLIs completed a connectivity probe and substantive review with configured default models/providers.

| CLI | Version | Verified bounded review command |
|---|---:|---|
| Claude | 2.1.226 | `claude -p "$PROMPT" --max-turns 5 --output-format text --no-session-persistence` |
| Codex | 0.147.0 | `codex exec --ephemeral "$PROMPT"` |
| Agy | 1.1.11 | `agy -p "$PROMPT" --output-format text --print-timeout 5m` |
| Kimi | 0.34.0 | `kimi -p "$PROMPT" --output-format text` |
| OpenCode | 1.18.15 | `opencode run "$PROMPT"` |
| Pi | 0.84.1 | `pi -p --no-session --no-tools --no-extensions "$PROMPT"` |
| Goose | 1.45.0 | `goose run --no-session -q --max-turns 10 -t "$PROMPT"` |

Runtime/session/tool controls do not override the configured model/provider. Never pass model, provider, endpoint, API-key, or reasoning overrides during default-config verification.

## Evidence rules

- Do not pipe a reviewer into `head`, `tail`, or `tee` before capturing its status.
- Retain stdout/stderr separately and record the true child exit code.
- Exit 0 requires a substantive parsed `VERDICT`, `FINDINGS`, and `RECOMMENDATIONS` response.
- Keep the fixture until every process terminates and parsing completes.
- Run at most three concurrently: Claude/Agy/Goose; OpenCode/Codex/Kimi; Pi alone.
- Treat product, executable, provider, and model names as distinct. Kimi runs as `kimi`; `fable-5` is not an executable.

## Pi does not terminate

**Symptom:** Pi emits a correct response but remains alive; stderr says 77 direct MCP tools were resolved.

**Cause:** `~/.pi/agent/mcp.json` exposes all tools with `directTools: true`, and optional extensions retain lifecycle resources.

**Repair:**

1. Back up the config outside Git with mode 0600.
2. Set `directTools: false` to use MCP proxy mode; preserve provider/model settings.
3. For bounded no-tool reviews, use `--no-session --no-tools --no-extensions`.
4. Verify both smoke and substantive review exit 0 through a native subprocess harness.

## Semantic failure

A reviewer may discuss invocation details instead of the artifact. Do not pass or mention permission-bypass flags in a read-only embedded-context review. Preserve the response and classify it `SEMANTIC_FAILURE` if required labels/content are absent.

## Timeout and process failure

Use the native subprocess result. `TIMEOUT` means the subprocess timeout fired; `MISSING` means executable absent/127; negative exit means `SIGNAL_TERMINATION`; invalid flags mean `INVOCATION_ERROR`; auth/provider failures mean `CONFIG_ERROR`.

Do not silently retry. Fix the cause, rebuild the fixture if artifacts changed, and retain a new diagnostic or verification round.

## Completion

Do not claim all agents work or archive an OpenSpec change until two full rounds show seven smoke `PASS` results and seven review `PASS`/`PASS_WITH_FINDINGS` results, with actionable findings resolved and installed skills matching committed canonical sources by SHA-256.
