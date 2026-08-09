# Seven-CLI OpenSpec Review Orchestration

The historical filename is retained for existing links. The current workflow uses seven external CLI reviewers plus the inline Hermes orchestrator.

## Review lenses

| Lens | Reviewer |
|---|---|
| Spec compliance and consolidation | Hermes orchestrator |
| Security | Claude |
| Quality and tests | Codex |
| Architecture | Antigravity (`agy`) |
| Product scope and usability | Kimi (`kimi`) |
| Cross-cutting consistency | OpenCode |
| Migration and compatibility | Pi |
| Docs, config, and operations | Goose |

## Verified default-model invocations

```text
claude -p PROMPT --max-turns 5 --output-format text --no-session-persistence
codex exec --ephemeral PROMPT
agy -p PROMPT --output-format text --print-timeout 5m
kimi -p PROMPT --output-format text
opencode run PROMPT
pi -p --no-session --no-tools --no-extensions PROMPT
goose run --no-session -q --max-turns 10 -t PROMPT
```

Do not pass model, provider, endpoint, API-key, or reasoning overrides. Runtime controls for noninteractive mode, sessions, tools/extensions, turns, output format, and host timeout are allowed. Pi's lifecycle controls preserve its configured default model/provider.

## Dispatch

Use these exact batches:

1. Claude, Agy, Goose
2. OpenCode, Codex, Kimi
3. Pi alone

Never run more than three concurrently. Embed one sanitized fixture under 20 KB into each prompt. Keep the retained fixture immutable until all children terminate and all results are parsed.

## Evidence contract

Use native subprocess execution, not shell pipelines. Capture before filtering:

- true exit code or timeout;
- stdout and stderr separately;
- executable path and installed version;
- start/end timestamps and duration;
- prompt, fixture, stdout, and stderr SHA-256;
- public argv flags with the prompt represented only by its hash;
- parsed verdict and terminal classification.

A zero exit code alone is not success. Require `VERDICT:`, `FINDINGS:`, and `RECOMMENDATIONS:` with substantive content.

## Statuses

`PASS`, `PASS_WITH_FINDINGS`, `REJECTED`, `TIMEOUT`, `MISSING`, `INVOCATION_ERROR`, `SIGNAL_TERMINATION`, `PROCESS_ERROR`, `SEMANTIC_FAILURE`, `EMPTY_OUTPUT`, and `CONFIG_ERROR`.

A failed reviewer does not erase sibling evidence and is never retried silently. Apply findings, rebuild the fixture, then perform a second full round.

## Pi lifecycle repair

Pi previously exposed 77 direct MCP tools (`directTools: true`). Its model produced valid reviews, but headless processes remained alive. Configure `directTools: false` for MCP proxy mode. For bounded no-tool reviews use `--no-session --no-tools --no-extensions`. This uses Pi's configured default provider/model and exits cleanly.

## Identity rules

Kimi's executable is `kimi`. `fable-5` is a model alias, not an executable. Keep product, executable, provider, and model identities distinct.

## Completion gate

Do not claim all reviewers work or archive the change until two full rounds have seven smoke `PASS` results and seven review `PASS`/`PASS_WITH_FINDINGS` results, all actionable findings are resolved, canonical skill sources are committed, installed copies match by SHA-256, and OpenSpec validation is honest.
