# Design: Hermes Matrix Integration

## Architecture

Matrix connectivity in Hermes is provided by the `matrix_platform` plugin (located at `hermes_plugins/matrix_platform/adapter.py`). The adapter is a **lazy-install pattern** — the plugin registers itself regardless of dependencies, but only initializes the actual adapter when the required packages are present at runtime.

### Dependency Chain

```
libolm (C library, system-level)
  └─ python-olm (Python bindings)
       └─ mautrix[encryption] (Matrix SDK + E2EE)
            └─ aiosqlite, asyncpg (storage backends)
            └─ aiohttp-socks (SOCKS proxy support)
            └─ aiohttp==3.14.1 (pinned for CVE fixes)
```

### Installation Target

All Python packages install into the Hermes venv at `~/.hermes/.venv` (Python 3.11.15). The install command uses `uv pip install -e ".[matrix]"` from the hermes-agent source directory, which resolves the `[matrix]` extras group from `pyproject.toml`.

### Configuration Layers

| Layer | File | Purpose |
|-------|------|---------|
| Secrets | `~/.hermes/.env` | `MATRIX_HOMESERVER`, `MATRIX_ACCESS_TOKEN`, `MATRIX_USER_ID`, `MATRIX_ENCRYPTION`, `MATRIX_ALLOWED_USERS` |
| Behavior | `~/.hermes/config.yaml` | `matrix:` section — mention requirements, threading, session scope |
| System | `/opt/homebrew/lib/libolm.dylib` | Crypto library for E2EE |

### E2EE Key Management

With `MATRIX_ENCRYPTION=true` (equivalent to `MATRIX_E2EE_MODE=required`):
- First connection uploads device keys to homeserver
- Encryption keys stored at `~/.hermes/platforms/matrix/store/` (created on first successful connect)
- Cross-signing verification via `MATRIX_RECOVERY_KEY` recommended for key rotation resilience

### Trade-offs

1. **Access token vs password login**: Using access token (current setup) is more secure — the password is not stored. Trade-off: token can be revoked server-side without notice.
2. **`session_scope: room`**: Stable per-room sessions lose auto-threading isolation but gain persistence across messages in the same room. Recommendation: keep `auto_thread: true` for conversation isolation.
3. **`libolm` vs `vodozemac`**: libolm is the mature, battle-tested crypto library. vodozemac (Rust) is newer but mautrix 0.21.0 targets libolm.

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| libolm version mismatch | E2EE fails at runtime | `brew install libolm` pulls latest stable |
| mautrix version pin drift | Adapter fails on restart | Pin exact versions in pyproject.toml `[matrix]` group |
| Access token revocation | Bot loses Matrix access | Monitor gateway logs; re-auth via Element if needed |
| E2EE store corruption | Decrypt failures | Store at `~/.hermes/platforms/matrix/store/` — can delete and re-bootstrap |
