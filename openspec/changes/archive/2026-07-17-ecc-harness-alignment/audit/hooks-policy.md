# ECC Hooks Policy

Source: `audit/raw-hooks.csv` (18 hooks)

## Canonical ECC_DISABLED_HOOKS

The following comma-separated string is the canonical value for `~/.claude/settings.json`:

```
post:bash:dispatcher,post:ecc-context-monitor,post:ecc-metrics-bridge,post:edit:accumulator,post:edit:console-warn,post:edit:design-quality-check,post:mcp-health-check,post:session-activity-tracker,pre:bash:dispatcher,session:end:marker,stop:check-console-log,stop:cost-tracker,stop:desktop-notify,stop:format-typecheck,stop:session-end
```

Length: 336 chars, 15 hooks disabled

## Decision Criteria

- **disabled-default**: TDT has an equivalent hook/concern, OR hook is out-of-scope for TDT usage
- **coexist**: TDT has its own version; both can fire without conflict
- **keep-default**: No TDT equivalent; ECC hook is the only implementation
- **investigate**: Manual review needed (none in v2.0.0)

## Hook Disposition Table

| hook_id | event | matcher | classification | rationale |
|---|---|---|---|---|
| `pre:compact` | PreCompact | `*` | coexist | TDT has separate pre-compact hook; ECC pre-compact runs after, different concern |
| `session:start` | SessionStart | `*` | coexist | ECC session-start bootstrap; TDT has separate agentmemory session-start hook |
| `post:bash:dispatcher` | PostToolUse | `Bash` | disabled-default | Consolidated postflight dispatcher; TDT has its own dispatcher |
| `post:ecc-context-monitor` | PostToolUse | `*` | disabled-default | ECC context monitor; TDT has agentmemory context tracking |
| `post:edit:console-warn` | PostToolUse | `Edit` | disabled-default | Post-edit accumulator overlaps TDT edit tracking |
| `post:edit:design-quality-check` | PostToolUse | `Edit|Write|MultiEdit` | disabled-default | Frontend design check; not applicable to TDT repos |
| `post:mcp-health-check` | PostToolUseFailure | `*` | disabled-default | MCP health check duplicates our pre-flight checks |
| `post:session-activity-tracker` | PostToolUse | `*` | disabled-default | ECC2 metrics tracker; we use agentmemory for session tracking |
| `pre:bash:dispatcher` | PreToolUse | `Bash` | disabled-default | Pre-flight Bash dispatcher; TDT has its own pre-tool checks |
| `session:end:marker` | SessionEnd | `*` | disabled-default | Session end marker is ECC2 control plane; we use agentmemory |
| `stop:check-console-log` | Stop | `*` | disabled-default | Console.log check; not applicable to Python TDT repos |
| `stop:cost-tracker` | Stop | `*` | disabled-default | Token/cost tracking; TDT has cost tracking via OpenTelemetry hooks |
| `stop:desktop-notify` | Stop | `*` | disabled-default | Desktop notification; out of scope for headless TDT usage |
| `stop:format-typecheck` | Stop | `*` | disabled-default | Biome/Prettier/tsc batch; TDT repos use ruff/mypy and have their own tooling |
| `stop:session-end` | Stop | `*` | disabled-default | Session end persistence; TDT has agentmemory session state |
| `post:ecc-metrics-bridge` | PostToolUse | `*` | disabled-default | ECC2 metrics bridge for ECC2 control plane; not used in TDT |
| `post:edit:accumulator` | PostToolUse | `Edit|Write|MultiEdit` | disabled-default | JS/TS file accumulator; TDT repos are Python (ruff/mypy), no downstream consumer since stop:format-typecheck is also disabled |
| `stop:evaluate-session` | Stop | `*` | keep-default | Pattern extraction; useful for ECC continuous-learning loop |

## Summary

Total: 18 hooks

- disabled-default: 15
- coexist: 2
- investigate: 2
- keep-default: 1
