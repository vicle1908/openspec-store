## Decisions

### Claude Code
Do not set undocumented zero timeout values. Retain the current generous finite values and use high per-run `--max-turns` plus Hermes host timeouts for long tasks. Keep `ECC_DISABLED_HOOKS`; removing it would re-enable plugin hooks. The existing `bypassPermissions` default and explicit `--permission-mode bypassPermissions` already provide maximum unattended capability. Do not add unverified `Write(*)` rules.

### Antigravity
No persistent mutation. Use `agy -p ... --dangerously-skip-permissions --print-timeout 20m` for large authorized tasks; the installed v1.1.11 has no max-turn or budget flag.

### OpenCode
The official permission schema supports `*`, `doom_loop`, and `external_directory`. Set ordinary permissions to allow, retain `doom_loop: ask` as the only operational loop guard, and use an absolute workspace path mapping for external access. `external_directory` applies only when a task crosses the active workdir boundary.

### Pi
The full installation resolves 77 direct MCP tools and timed out after producing output. Prefer the adapter’s proxy mode or a curated 5–20-tool direct set before changing token compaction. Keep full tool authority for the selected set. Measure context behavior before increasing reserves.

### Codex
The actual configuration is `~/.codex/config.toml`. Add `approval_policy = "never"` only after validating the installed schema; retain existing `sandbox_mode = "danger-full-access"` because the user authorized unrestricted agents.

### Kimi Code
The actual configuration is `~/.kimi-code/config.toml`. Keep `default_permission_mode = "auto"`, `max_attempts_per_step = 5`, and current `reserved_context_size = 50000`. Plan mode and larger context reserves become explicit profiles for complex tasks, not mandatory defaults.
## Risks / Trade-offs

- Finite timeouts prevent deadlocks while remaining generous; Hermes host bounds remain the outer control.
- `doom_loop: ask` may interrupt a pathological loop, but normal tools remain fully allowed.
- Pi proxy/curated MCP access preserves capability while reducing prompt/tool-registration overhead.
- Keeping Kimi retries at five improves transient-failure resilience but can extend a stalled run; host timeout remains the bound.

## Official References

- Claude Code permissions: https://code.claude.com/docs/en/permissions
- OpenCode CLI: https://opencode.ai/docs/cli/
- OpenCode permissions: https://opencode.ai/docs/permissions/
- Pi documentation: https://pi.dev/docs/latest
- Antigravity CLI: https://antigravity.google/docs/cli/using
- Codex CLI: https://developers.openai.com/codex
- Kimi Code CLI: https://moonshotai.github.io/kimi-code/en/reference/kimi-command
