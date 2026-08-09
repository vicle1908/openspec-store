# Headless Probe Recipes

Use unique disposable directories and remove them after verification. Replace `/tmp/coding-agent-probe` with a private temporary root when multiple checks run concurrently.

## Common evidence fields

Record:

- CLI version and command form.
- Effective provider/model names without secrets.
- Permission and sandbox settings.
- Process exit code.
- Structured status when available.
- Exact marker path and externally read-back content.
- Repository diff/test result for coding tasks.

## Claude Code

```bash
mkdir -p /tmp/coding-agent-probe/claude
rm -f /tmp/coding-agent-probe/claude/marker
claude -p 'Create exactly one file at /tmp/coding-agent-probe/claude/marker containing exactly CLAUDE_WRITE_OK. Verify it.' \
  --permission-mode bypassPermissions \
  --tools Read,Edit,Write,Bash \
  --max-turns 20 --max-budget-usd 5
test "$(cat /tmp/coding-agent-probe/claude/marker)" = CLAUDE_WRITE_OK
```

Use larger turn and dollar budgets for architecture reviews or multi-file work.

## Antigravity

The prompt must immediately follow `-p`; include the headless permission bypass or file tools can be soft-denied.

```bash
mkdir -p /tmp/coding-agent-probe/agy
rm -f /tmp/coding-agent-probe/agy/marker
agy -p 'Create exactly one file at /tmp/coding-agent-probe/agy/marker containing exactly AGY_WRITE_OK. Verify it.' \
  --dangerously-skip-permissions \
  --output-format json --print-timeout 20m
test "$(cat /tmp/coding-agent-probe/agy/marker)" = AGY_WRITE_OK
```

Check both process exit code and JSON `status`.

## OpenCode

Use `run`; `exec` is not the installed command. `--auto` removes permission prompts not already denied by configuration.

```bash
mkdir -p /tmp/coding-agent-probe/opencode
rm -f /tmp/coding-agent-probe/opencode/marker
opencode run --auto 'Create exactly one file at /tmp/coding-agent-probe/opencode/marker containing exactly OPENCODE_WRITE_OK. Verify it.'
test "$(cat /tmp/coding-agent-probe/opencode/marker)" = OPENCODE_WRITE_OK
```

Check the selected agent profile as well as global permissions.

## Pi

Pi has no separate bypass flag. `--approve` trusts project-local resources; the tool list enables the coding primitives.

```bash
mkdir -p /tmp/coding-agent-probe/pi
rm -f /tmp/coding-agent-probe/pi/marker
pi -p --no-session --approve --tools read,write,edit,bash \
  'Create exactly one file at /tmp/coding-agent-probe/pi/marker containing exactly PI_WRITE_OK. Verify it.'
test "$(cat /tmp/coding-agent-probe/pi/marker)" = PI_WRITE_OK
```

## Codex

```bash
mkdir -p /tmp/coding-agent-probe/codex
rm -f /tmp/coding-agent-probe/codex/marker
codex exec -c 'approval_policy="never"' \
  --sandbox danger-full-access --skip-git-repo-check \
  --output-last-message /tmp/coding-agent-probe/codex/response.txt \
  'Create exactly one file at /tmp/coding-agent-probe/codex/marker containing exactly CODEX_WRITE_OK. Verify it.'
test "$(cat /tmp/coding-agent-probe/codex/marker)" = CODEX_WRITE_OK
```

Use `--skip-git-repo-check` only when the current root is an umbrella directory rather than a Git repository.

## Kimi Code

With the configured `default_permission_mode = "auto"`, prompt mode is already fully autonomous. Do not add `--auto` or `--yolo` to `-p` on current Kimi Code versions.

```bash
mkdir -p /tmp/coding-agent-probe/kimi
rm -f /tmp/coding-agent-probe/kimi/marker
kimi -p 'Create exactly one file at /tmp/coding-agent-probe/kimi/marker containing exactly KIMI_WRITE_OK. Verify it.' \
  --output-format text
test "$(cat /tmp/coding-agent-probe/kimi/marker)" = KIMI_WRITE_OK
```

## Goose

Goose has no permission bypass flag. Extensions (including `developer` for file/shell) execute tools directly in headless mode. First run has ~55s cold start; use generous timeouts. **Exit code 0 does NOT guarantee success** — invalid models, max-turns exhaustion, and missing extensions all return exit 0. Always verify artifacts externally.

```bash
mkdir -p /tmp/coding-agent-probe/goose
rm -f /tmp/coding-agent-probe/goose/marker
goose run -t 'Create exactly one file at /tmp/coding-agent-probe/goose/marker containing exactly GOOSE_WRITE_OK. Then verify it exists by reading it back.' \
  --no-session -q --max-turns 10
# CRITICAL: exit code alone is unreliable — verify the file exists
test -f /tmp/coding-agent-probe/goose/marker
test "$(cat /tmp/coding-agent-probe/goose/marker)" = GOOSE_WRITE_OK
```

For structured output parsing, use `-q --output-format json`, skip banner lines (find first `{`), then `json.loads()`. Extract last assistant text content item (not just index 0, as thinking items may precede text).

Provider override example:
```bash
goose run -t "Reply with exactly: GOOSE_PROVIDER_OK" \
  --provider custom_shopapikey --model fable-5 \
  --no-session -q --max-turns 1
```

## Cleanup

```bash
rm -rf /tmp/coding-agent-probe
```
