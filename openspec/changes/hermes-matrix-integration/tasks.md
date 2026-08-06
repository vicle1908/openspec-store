# Tasks: Hermes Matrix Integration

## Phase 1: System Dependencies

- [ ] 1.1 Install `libolm` via Homebrew: `brew install libolm`
- [ ] 1.2 Verify installation: `brew list libolm` and check `/opt/homebrew/lib/libolm.dylib` exists

## Phase 2: Python Dependencies

- [ ] 2.1 Install Matrix extras into Hermes venv: `cd ~/.hermes/hermes-agent && uv pip install -e ".[matrix]"`
- [ ] 2.2 Verify mautrix installed: `~/.hermes/.venv/bin/python -c "import mautrix; print(mautrix.__version__)"`
- [ ] 2.3 Verify E2EE crypto available: `~/.hermes/.venv/bin/python -c "from mautrix.crypto import OlmMachine; print('OK')"`

## Phase 3: Config.yaml Matrix Section

- [ ] 3.1 Add `matrix:` section to config.yaml via `hermes config set matrix.require_mention true`
- [ ] 3.2 Set auto-threading: `hermes config set matrix.auto_thread true`
- [ ] 3.3 Set session scope: `hermes config set matrix.session_scope room`

## Phase 4: Gateway Restart and Verification

- [ ] 4.1 Restart gateway process and verify Matrix adapter initializes (no "required packages not installed" warnings)
- [ ] 4.2 Verify Matrix store directory created at `~/.hermes/platforms/matrix/store/`
- [ ] 4.3 Send test DM from `@victory1908:matrix.org` and confirm bot responds

## Phase 5: Cross-Signing (Optional)

- [ ] 5.1 Obtain recovery key from Element (Settings → Security & Privacy → Encryption)
- [ ] 5.2 Set `MATRIX_RECOVERY_KEY` in `.env`
- [ ] 5.3 Restart gateway and verify cross-signing completes (device verified)
