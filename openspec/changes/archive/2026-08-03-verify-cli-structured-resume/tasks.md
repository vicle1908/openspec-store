## 1. Setup

- [x] 1.1 Define a shared JSON Schema and unique nonce-based continuation contract.
- [x] 1.2 Create the disposable workspace and validate the schema independently.

## 2. Structured Output

- [x] 2.1 Verify Antigravity returns schema-valid structured output.
- [x] 2.2 Verify Claude Code's configured endpoint/model does not enforce the supplied schema after normal and safe-mode probes.
- [x] 2.3 Verify Codex returns schema-valid structured output.

## 3. Session Continuation

- [x] 3.1 Resume Antigravity by conversation ID and recover the saved nonce.
- [x] 3.2 Resume Claude Code by session ID and recover the saved nonce.
- [x] 3.3 Resume Codex exec by thread ID and recover the saved nonce.

## 4. Documentation and Closure

- [x] 4.1 Update skills for discovered schema/session caveats.
- [x] 4.2 Record evidence and run focused/full strict validation.
- [x] 4.3 Archive and commit only owned paths, remove fixtures, and preserve concurrent work.
