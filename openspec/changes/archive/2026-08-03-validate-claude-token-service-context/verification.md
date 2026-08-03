# Verification Evidence

Date: 2026-08-03

## Presence checks

The direct Hermes subprocess environment reported these variables absent:

- `ANTHROPIC_API_KEY`
- `ANTHROPIC_AUTH_TOKEN`
- `CLAUDE_CODE_OAUTH_TOKEN`

The user login-shell context was checked without printing values:

```bash
zsh -lic 'for name in ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN CLAUDE_CODE_OAUTH_TOKEN; do ... presence only ...; done'
```

Observed:

- `ANTHROPIC_AUTH_TOKEN`: present
- Other checked variables: absent
- No token value was displayed or persisted.

## Authentication status

Direct invocation:

```text
loggedIn: false
```

Login-shell invocation:

```bash
zsh -lic 'claude auth status'
```

Observed:

- `loggedIn: true`
- `authMethod: oauth_token`
- `apiProvider: firstParty`

## Model execution

Command shape:

```bash
zsh -lic 'claude -p "Reply with exactly CLAUDE_TOKEN_OK" --tools "" --max-turns 1 --output-format json'
```

Observed:

- Exit code: `0`
- `is_error`: `false`
- `subtype`: `success`
- `terminal_reason`: `completed`
- `num_turns`: `1`
- Result: `CLAUDE_TOKEN_OK`
- Session ID: `bb2169dc-37b3-44ba-88d6-8adb374b9e75`
- Model provider: `firstParty`
- Canonical model reported by the CLI: `fable-5[1m]`
- No tools, web searches, or fetches were used.
- Reported cost: approximately USD 0.011728.

## Skill update

The Claude Code skill now documents that service environments may not inherit login-shell tokens, and instructs Hermes to run presence, auth status, and Claude execution through the same `zsh -lic` context. It explicitly prohibits printing, copying, persisting, or passing the token as a command-line value.

## Limitations

- This depends on the user's login-shell initialization continuing to load the token.
- Token expiration or shell-profile changes can invalidate the path.
- The verification proves authentication and basic model execution, not broad file/shell/MCP permissions.
