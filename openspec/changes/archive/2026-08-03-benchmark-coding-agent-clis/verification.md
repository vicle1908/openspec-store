# Three-CLI Coding Benchmark Evidence

Date: 2026-08-03

## Fixture and acceptance criteria

Three disposable Git repositories were created under `/tmp/coding-agent-cli-benchmark-20260803/` with identical committed files:

- `slugify.py`
- `test_slugify.py`
- `README.md`

Baseline command:

```bash
python3 -m unittest -v
```

All three baselines ran four tests and failed the same two cases:

- surrounding separators were not trimmed;
- punctuation-only input returned `-` instead of an empty string.

The shared task required each agent to fix only `slugify.py`, preserve the public function signature, avoid modifying tests/README, run the existing test suite, and make the smallest clear change.

Acceptance required external test success, `git diff --check`, and no tracked out-of-scope changes.

## Antigravity

Invocation contract:

- `agy --new-project`
- model `gemini-3.6-flash-low`
- low effort
- JSON print mode
- three-minute print timeout
- existing bounded workspace and permissions

Agent result:

- Exit code: `0`
- Status: `SUCCESS`
- Duration: approximately 9.81 seconds
- Turns: `1`
- Conversation ID: `49004127-34d8-4a21-b457-e5b721bd2a3a`

Change:

```diff
-return re.sub(r"[^a-z0-9]+", "-", value.lower())
+return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
```

Independent verification:

- Four of four tests passed.
- `git diff --check` passed.
- Tracked diff: one insertion and one deletion in `slugify.py` only.
- `test_slugify.py` and `README.md` remained unchanged.
- Running tests produced an untracked `__pycache__/` artifact, which was removed with the disposable fixture during cleanup.

Outcome: **PASS**.

## Codex

Invocation contract:

- `codex exec`
- `approval_policy="never"`
- workspace-write sandbox
- JSONL output plus final-message file

Agent result:

- Exit code: `0`
- Turn completed successfully.
- Codex ran tests, inspected status/diff, and removed generated Python cache artifacts.
- Reported total input tokens: `158525`, including `134400` cached tokens.
- Reported output tokens: `1660`, including `763` reasoning tokens.

Change:

```diff
-return re.sub(r"[^a-z0-9]+", "-", value.lower())
+return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
```

Independent verification:

- Four of four tests passed.
- `git diff --check` passed.
- Tracked diff: one insertion and one deletion in `slugify.py` only.
- `test_slugify.py` and `README.md` remained unchanged.
- No untracked test-cache artifact remained after the agent exited.

Outcome: **PASS**.

## Claude Code

Invocation contract:

- token-loaded `zsh -lic` context
- `claude -p`
- `dontAsk` permission mode
- tools restricted to `Read`, `Edit`, and `Bash`
- Bash permission limited to the unittest command
- maximum eight turns
- JSON output

Observed environment:

- Token authentication was present and previously verified.
- The login shell set `ANTHROPIC_BASE_URL` to a local loopback endpoint.
- The configured endpoint refused TCP connections during diagnosis.

Attempts:

1. Coding attempt: `ConnectionRefused`, zero input/output tokens, no edits.
2. Coding retry: `ConnectionRefused`, zero input/output tokens, no edits.
3. A minimal no-tools connectivity probe succeeded and returned `CONNECTIVITY_OK`.
4. Final coding attempt: `ConnectionRefused`, zero input/output tokens, no edits.

Independent verification:

- Git worktree remained unchanged.
- The original two tests still failed.
- No permission denial or model-generated edit occurred.

Outcome: **RUNTIME UNAVAILABLE** for the tool-enabled benchmark. This is not classified as a coding-correctness failure because every coding attempt failed before model token processing. The intermittent local endpoint accepted a minimal request but consistently refused the tool-enabled task.

## Comparison

| CLI | Runtime available | Correct fix | Tests | Tracked scope |
|---|---:|---:|---:|---|
| Antigravity | Yes | Yes | 4/4 pass | `slugify.py` only |
| Codex | Yes | Yes | 4/4 pass | `slugify.py` only |
| Claude Code | No during coding attempts | Not evaluated | baseline 2/4 fail | no changes |

Antigravity and Codex independently produced the same minimal correct implementation. The single benchmark does not establish a general quality ranking. Claude Code requires repair or stabilization of its configured local API endpoint before a fair coding comparison can be completed.

## Security and cleanup

- No credential values were recorded in this evidence.
- No application repository was modified.
- Disposable repositories were removed after evidence collection.
- The separately owned `fix-ci-workflow-issues` OpenSpec change was not staged or modified.
