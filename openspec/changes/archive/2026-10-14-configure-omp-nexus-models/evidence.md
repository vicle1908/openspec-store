# Verification Evidence: configure-omp-nexus-models

## Preflight and Baselines
- Captured baseline md5 checksums:
  - `models.yml`: `20165bd91dffcc363e8413b0ea6769cb`
  - `config.yml`: `80c2346bd8d0478f365f38579e717655`
- Backed up live files to `~/.omp/agent/backups-20261014133326/`.
- OmniRoute gateway confirmed healthy (`http://127.0.0.1:20128/healthz` returned `ok`).
- Probed Nexus catalog via `http://localhost:20128/v1/models`; confirmed 19 `nx/*` models present, including `nx/deepseek-v4.1-flash`, `nx/deepseek-v4-pro`, and `nx/Gemini 4 Argon`.

## Isolated Profile Smoke Gate
- Scaffolded `~/.omp/profiles/smoke-nx-models/agent`.
- Staged proposed `models.yml` and `config.yml` with empty fallback chains (`retry: {fallbackChains: {}}`).
- Verified `omp --profile smoke-nx-models models --json` parses all 3 models without schema warnings.
- Executed isolated attribution smoke test:
  ```bash
  timeout 90 omp --profile smoke-nx-models --no-session \
    --model 'omniroute/nx/deepseek-v4.1-flash' -p 'reply only: pong'
  ```
  Result: exited with code 0, returned `pong` with zero fallback events.

## Live Rollout & Verification
- Atomic replacement of `~/.omp/agent/models.yml` adding:
  - `nx/deepseek-v4.1-flash` (128000 ctx, reasoning: true)
  - `nx/deepseek-v4-pro` (1000000 ctx, reasoning: true)
  - `nx/Gemini 4 Argon` (1000000 ctx, reasoning: true)
- Atomic replacement of `~/.omp/agent/config.yml` configuring:
  - `modelRoles.commit: omniroute/nx/deepseek-v4.1-flash`
  - `modelRoles.default: google-antigravity/gemini-3.8-flash:high`
  - `retry.fallbackChains` for `omniroute/nx/*` mapping to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high`.
- Live probe execution:
  ```bash
  omp --mode json --no-session --model 'omniroute/nx/deepseek-v4.1-flash' -p 'reply only: pong'
  ```
  Result: assistant response `pong` with `provider: "omniroute"`, `model: "nx/deepseek-v4.1-flash"`, zero errors, zero fallbacks.
- Live `omp commit --dry-run` probe in git repo confirmed resolution to `DeepSeek V4.1 Flash (Nexus)`.
- Live default probe without `--model` confirmed direct resolution to `google-antigravity/gemini-3.8-flash` with exit code 0.
- Cleaned up temporary test profile `~/.omp/profiles/smoke-nx-models`.
