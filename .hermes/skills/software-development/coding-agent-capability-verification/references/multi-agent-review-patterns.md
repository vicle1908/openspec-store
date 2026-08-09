# Multi-Agent Review Patterns

## Use real CLI agents

Use actual external CLIs for coding-agent reviews: `claude`, `codex`, `agy`, `kimi`, `opencode`, `pi`, and `goose`. Do not substitute Hermes `delegate_task` when the user requests coding-agent CLI review.

## Verified default-model invocations (2026-08-09)

| Agent | Bounded review invocation | Host timeout |
|---|---|---:|
| Claude | `claude -p "$PROMPT" --max-turns 5 --output-format text --no-session-persistence` | 360s |
| Codex | `codex exec --ephemeral "$PROMPT"` | 600s |
| Agy | `agy -p "$PROMPT" --output-format text --print-timeout 5m` | 360s |
| Kimi | `kimi -p "$PROMPT" --output-format text` | 600s |
| OpenCode | `opencode run "$PROMPT"` | 600s |
| Pi | `pi -p --no-session --no-tools --no-extensions "$PROMPT"` | 900s |
| Goose | `goose run --no-session -q --max-turns 10 -t "$PROMPT"` | 600s |

Use each CLI's configured default model/provider. Do not pass model, provider, endpoint, API-key, or reasoning overrides. Runtime controls for noninteractive mode, sessions, tools/extensions, turns, output format, and host timeout are allowed.

## Batch order

1. Claude, Agy, Goose
2. OpenCode, Codex, Kimi
3. Pi alone

Never exceed three concurrent reviewer processes.

## Context and evidence

Embed one sanitized fixture under 20 KB into every prompt. Use native subprocess execution without shell pipelines. Retain true exit code, stdout/stderr separately, executable/version, timestamps/duration, public argv with prompt hash, fixture/output hashes, parsed verdict, and terminal classification.

Exit 0 is not sufficient. Require exact `VERDICT:`, `FINDINGS:`, and `RECOMMENDATIONS:` labels with substantive content.

## Pi lifecycle repair

The local Pi MCP adapter previously used `directTools: true`, registering 77 tools and keeping print-mode processes alive after valid output. Configure `directTools: false` for proxy mode. For bounded no-tool reviews use `--no-session --no-tools --no-extensions`; this preserves the configured default provider/model and exits cleanly.

## Identity

Kimi's executable is `kimi`. `fable-5` is a model alias, not an executable. Keep product, executable, provider, and model names distinct.

## Completion gate

After applying Round 1 findings, rebuild the fixture and run a full Round 2. Claim all agents operational only when both rounds contain seven smoke `PASS` results and seven review `PASS`/`PASS_WITH_FINDINGS` results, with canonical skills committed and installed copies checksum-matched.
