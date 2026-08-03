## Context

The CLIs expose different output and continuation contracts: Antigravity uses `--json-schema` and `--conversation`, Claude uses `--json-schema` and `--resume`, while Codex uses a schema file and `codex exec resume`. A fair check needs equivalent schema and hidden context while respecting each native envelope.

## Goals / Non-Goals

**Goals:**

- Verify valid structured data, not merely JSON transport envelopes.
- Prove continuation uses saved context by asking for a nonce omitted from the second prompt.
- Parse results independently and fail on schema or context mismatch.

**Non-Goals:**

- Requiring all three CLIs to return identical envelope fields.
- Testing session forks or interactive pickers.

## Decisions

### Decision: Use a small shared schema

The structured object contains `status` and `nonce` string fields with `additionalProperties: false`. The first prompt supplies a unique nonce and asks the model to retain it.

### Decision: Separate structured-output and continuation assertions

First validate the structured output against the common schema. Then resume by identifier and ask for the remembered nonce using the CLI's normal text/JSON result path. This avoids assuming schema flags persist on resume.

### Decision: Use direct Claude invocation

The updated Claude settings own its working endpoint/token; avoid the stale login-shell endpoint override.

## Risks / Trade-offs

- **Customization rejects exact-output prompts** → Use a legitimate session-memory task and validate structured fields rather than forced prose.
- **Resume configuration is not persisted** → Re-pass required output/tool restrictions explicitly when supported.
- **Session lookup is CWD-scoped** → Run initial and resume calls from the same disposable directory.
