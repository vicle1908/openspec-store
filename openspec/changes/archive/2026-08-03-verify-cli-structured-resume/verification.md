# Structured Output and Session Resume Evidence

Date: 2026-08-03

## Contract

Shared nonce: `violet-cascade-7319`.

Shared schema required exactly:

```json
{
  "status": "stored",
  "nonce": "violet-cascade-7319"
}
```

The schema required both fields and rejected additional properties. Initial turns were run in isolated directories with tools disabled or read-only. Resume prompts omitted the nonce and asked each CLI to recover it from prior session context.

## Antigravity

Initial invocation used `--new-project`, `--output-format json`, and `--json-schema <file>`.

Observed:

- Exit: `0`
- Status: `SUCCESS`
- Conversation ID: `58c0f087-c09e-499e-bac1-14a2ea9dd1b6`
- `structured_output`: exactly schema-valid
- Structured fields: `status=stored`, `nonce=violet-cascade-7319`

Resume used `--conversation` with the same ID and did not re-pass `--json-schema`.

Observed:

- Same conversation ID
- Status: `SUCCESS`
- `num_turns`: `2`
- Natural-language response recovered the nonce correctly
- The response envelope still contained the prior schema-valid `structured_output`

Outcome:

- Structured output: **PASS**
- Session continuation: **PASS**
- Caveat: schema state can persist with the conversation across resume.

## Claude Code

Initial invocation used direct settings-owned authentication/endpoint, `--tools ""`, one turn, JSON transport, and `--json-schema`.

Observed:

- API completed successfully
- Session ID: `734b0865-1fab-4487-a65e-cf6a6fe24b44`
- The configured provider/model returned literal tool-call-like markup instead of `structured_output`
- The result did not satisfy the schema

Two isolation probes followed:

1. `--safe-mode`, tools disabled, direct structured task: returned a refusal/prose result without `structured_output`.
2. `--safe-mode`, legitimate Python code-analysis task with Read only: returned ordinary review prose and JSON-in-markdown with fields that did not match the supplied schema; no `structured_output`.

Resume used `--resume <session-id>` from the same directory.

Observed:

- Same session ID
- Exit: `0`
- Terminal reason: `completed`
- Recovered `violet-cascade-7319` correctly from the prior turn

Outcome:

- Structured output: **UNSUPPORTED/FAIL for the configured endpoint/model** (`fable-5[1m]`)
- Session continuation: **PASS**
- Caveat: `--json-schema` support must be verified per provider/model; JSON transport success does not imply schema enforcement.

## Codex

Initial invocation used `codex exec --output-schema <file> --json --output-last-message <file>`.

Observed:

- Exit: `0`
- Thread ID: `019fc824-a78d-7c83-8377-7ba88115c230`
- Final-message file contained exactly the schema-valid object
- Turn completed successfully

Resume used `codex exec resume <thread-id>` from the same directory without re-passing the schema.

Observed:

- Same thread ID
- Exit: `0`
- Natural-language result recovered the nonce correctly
- Final-message file contained the recovered nonce sentence

Outcome:

- Structured output: **PASS**
- Session continuation: **PASS**
- Caveat: pass the schema on each turn where structured output is required; continuation alone does not imply a schema requirement.

## Summary

| CLI | Structured output | Session resume | Notes |
|---|---|---|---|
| Antigravity | Pass | Pass | Schema persisted in resumed conversation |
| Claude Code | Unsupported on configured endpoint/model | Pass | No `structured_output` despite repeated schema probes |
| Codex | Pass | Pass | Re-pass schema for structured resumed turns |

No credentials were recorded. No application repository was modified.
