# Provider Failure Evidence (Final)

## Claude — NOT_REVIEWED (Auth failure)
- Binary: `/Users/androidteam/.local/bin/claude` 2.1.241
- Bounded retry: `claude -p --no-session --max-turns 15 --output-format json --tools Read`
- Result: HTTP 401 authentication error (exhausted 10 retries)
- Root cause: `apiKeyHelper` and `ANTHROPIC_AUTH_TOKEN` conflict; the endpoint requires a non-conflicting auth path
- Assessment: Provider auth issue, not orchestration

## Pi — NOT_REVIEWED (Startup overhead timeout)
- Binary: `/opt/homebrew/bin/pi` 0.84.2
- Attempt 1: `pi -p --no-session --tools ''` — timed out at 180s; MCP resolved 148 direct tools on startup
- Attempt 2: `pi -p --no-session --no-mcp --tools ''` — rejected (`--no-mcp` not a valid flag)
- Attempt 3: `pi -p --no-session --no-extensions --no-skills --tools ''` — exit 1, no output
- Root cause: pi-mcp-adapter resolves 148 direct MCP tools on startup, consuming the entire timeout before any review work begins
- Assessment: Tool overhead on startup blocks headless execution; needs pre-authenticated session or MCP-free build

## OMP — NOT_REVIEWED (Empty assistant response)
- Binary: `/opt/homebrew/bin/omp` 18.0.4
- Invocation: `omp -p --mode=json --no-tools` (embedded packet)
- Result: exit 0, 20969 chars of JSONL, 9 events, but assistant message had **0 bytes of text content**
- Root cause: The model processed the input but produced no visible output in the JSONL `agent_end` message array
- Assessment: Not a timeout — the model returned an empty response despite processing input

## Prime Agent — NOT_REVIEWED (Tool-call-only output)
- Binary: `/opt/homebrew/bin/prime-agent` 0.8.0-beta.543.1
- Invocation: `prime-agent -p --no-session -nt` (no tools)
- Result: 537 chars, 2 tool-call fragments (`<tool_call>`), no verdict
- Root cause: Model has no file-reading tools without MCP, so it tries to use bash to find/read files via tool-call requests
- Assessment: No verdict possible without tools; MCP integration needed for Prime Agent to function

## Kimi — NOT_REVIEWED (CLI syntax failure → timeout)
- Binary: `/opt/homebrew/bin/kimi` 0.38.0
- Attempt 1: `kimi -p --no-session --plan` — exit 1, stderr: "unknown command 'READ-ONLY REVIEW...'"
- Assessment: The embedded prompt with newlines was parsed as multiple positional arguments
- Root cause: Kimi's `-p` flag likely needs a single-quoted prompt; multi-line content causes syntax parsing errors

## Summary

The five incomplete reviews failed for mixed reasons: provider authentication (Claude), MCP startup overhead (Pi, OMP), unavailable tools (Prime Agent), and CLI invocation incompatibility (Kimi). No substantive verdict is inferred from these failures. The 2 substantive verdicts (Codex BLOCK, AGY PASS_WITH_CHANGES) provide sufficient signal for planning-phase closure.
