# Tasks

## 1. Configuration Deployment & Validation

- [x] 1.1 Declare `gemini-4-argon` combo under `providers.omniroute.models` in `~/.omp/agent/models.yml`.
- [x] 1.2 Reallocate `modelRoles.default` in `~/.omp/agent/config.yml` to `omniroute/gemini-4-argon:high`.
- [x] 1.3 Add explicit fallback chain for `omniroute/gemini-4-argon` in `retry.fallbackChains` pointing to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high`.

## 2. Live Verification & Evidence

- [x] 2.1 Verify `omniroute/gemini-4-argon` appears in `omp models --json` with valid metadata.
- [x] 2.2 Execute live default turn probe `omp --mode json --no-session --no-tools -p "reply only: pong"` and verify response attributes (`provider: omniroute`, `model: gemini-4-argon`, zero fallback events).
