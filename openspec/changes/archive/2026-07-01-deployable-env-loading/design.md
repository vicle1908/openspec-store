# Deployable Env Loading: Design

## Context

`scripts/deploy.sh` in `ai-review/` and `webhook-receiver/` both
generate a runtime launcher via inline heredoc. The old template
looked like:

```bash
#!/usr/bin/env bash
set -euo pipefail

if [[ -f "\$HOME/.tdt/.env" ]]; then
  set -a
  source "\$HOME/.tdt/.env"
  set +a
fi
export PATH="...:\$HOME/.tdt/bin:..."
exec ".../.venv/bin/uvicorn" ... ...
```

If `~/.tdt/.env` contains a line that bash cannot parse (unescaped
pipe, malformed quoting, etc), `set -e` makes `source` exit
non-zero, which propagates up and prevents `exec` from ever running.
The launchd process exits with status 1 → LaunchAgent stays down.

## Decisions

### D1: Drop bash `source` entirely

The Python app already uses `tdt_core.env.load_tdt_env()` (which
wraps `python-dotenv`). `python-dotenv` is line-tolerant: it logs
a warning and continues on malformed lines. This means we can
remove the bash `source` step and let Python do the loading.

**Risk:** None meaningful — the Python app already needs
`~/.tdt/.env` to be loaded for credential access, and that path
already works.

### D2: launchd plist provides PATH and SSL cert paths

The launchd plist's `EnvironmentVariables` dict already provides
`PATH`, `HOME`, `SSL_CERT_FILE`, and `REQUESTS_CA_BUNDLE`. The
runtime launcher no longer needs to set `PATH` from the env file.

### D3: webhook-receiver-specific env stays inline

`webhook-receiver` needs `JIRA_GUARD_POLICIES_PATH` to point to the
reminder-policies.yaml file. The launcher still sets this
explicitly. This is OK because it's a single, well-known path —
not loaded from `.env`.

### D4: Repair the corrupted .env line 54

The user confirmed `~/.tdt/.env` line 54 (`SHEET_LINKS`) contained
~50 duplicated `,Jira Catalog|...` entries. We strip them down to
a clean comma-separated URL list. This is environmental cleanup;
no code change depends on the new format.

## Implementation

### 1. ai-review/scripts/deploy.sh (heredoc)

```bash
cat > "$LAUNCHER_PATH" <<LAUNCHER
#!/usr/bin/env bash
# ai-review runtime launcher.
# Env-loading strategy: launchd plist provides PATH/SSL_CERT_FILE/REQUESTS_CA_BUNDLE;
# Python code uses tdt_core.env.load_tdt_env() (python-dotenv, tolerant of malformed
# lines) for the rest. We deliberately do NOT `source ~/.tdt/.env` from bash because
# the file may contain unescaped pipes or other shell-unsafe content.
exec "$APP_DIR/.venv/bin/uvicorn" ai_review.api.app:app \
  --host 127.0.0.1 \
  --port "${AI_REVIEW_PORT:-8090}" \
  --log-level info
LAUNCHER
chmod 755 "$LAUNCHER_PATH"
```

### 2. webhook-receiver/scripts/deploy.sh (heredoc)

Same pattern, with `JIRA_GUARD_POLICIES_PATH` set inline before
`exec` because it's not in `.env`.

### 3. Repair ~/.tdt/.env

Manual one-time cleanup of the corrupted `SHEET_LINKS` value.
Out of scope for automated test coverage; documented in the
proposal.

## Testing Strategy

1. **Manual:** run `bash scripts/deploy.sh`, verify both services
   start, verify `/health` returns 200.
2. **Manual:** corrupt `~/.tdt/.env` (add `|JUNK`), restart
   services, verify they still start. Cleanup env after test.
3. **Regression:** full pytest suite for `ai-review/` and
   `webhook-receiver/` passes.

## Risks & Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| `.env` is in `$HOME` not in the repo, so a future .env corruption could still break the env loading | Medium | python-dotenv logs warning and continues; app falls back to plist env vars |
| A new env var added to the plist might not propagate to the running service until the plist is reloaded | Low | The deploy script reloads the plist via `launchctl bootout/bootstrap` |
| Manually-set env vars in the launcher (like `JIRA_GUARD_POLICIES_PATH`) drift from upstream expectations | Low | Single inline declaration; reviewed per change |

## Open Questions

None — design is straightforward.
