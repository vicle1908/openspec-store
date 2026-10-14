# Tasks

## 1. Preflight and Baseline Snapshots

- [x] 1.1 Compute md5 baselines and create timestamped backups of `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml`.
- [x] 1.2 Verify OmniRoute gateway health on `http://127.0.0.1:20128/healthz` and verify Nexus model catalog availability (`nx/deepseek-v4.1-flash`) via `omni-models` contract (`bun ~/Omniroute/bin/omniroute.mjs models nx --json` or `/api/v1/models`), testing route reachability using `omni-combos-routing` simulation (`/api/routing/simulate`) if multi-target combos are evaluated.

## 2. Isolated Profile Smoke Gate

- [x] 2.1 Scaffold temporary test profile directory at `~/.omp/profiles/smoke-nx-models/agent`.
- [x] 2.2 Stage proposed `models.yml` (including `nx/deepseek-v4.1-flash`, `nx/deepseek-v4-pro`, `nx/Gemini 4 Argon`) and `config.yml` with empty fallback chains (`retry: {fallbackChains: {}}`) in the isolated profile.
- [x] 2.3 Run `omp --profile smoke-nx-models models --json` to verify catalog parser accepts the new model definitions without schema warnings.
- [x] 2.4 Execute isolated smoke test: `omp --profile smoke-nx-models --no-session --model 'omniroute/nx/deepseek-v4.1-flash' -p 'reply only: pong'` and verify exit code 0, response `pong`, and absence of fallback markers.

## 3. Live Configuration Application

- [x] 3.1 Verify live file md5 checksums match baselines from task 1.1 to guard against concurrent edits.
- [x] 3.2 Atomically update `~/.omp/agent/models.yml` with the new Nexus model catalog entries.
- [x] 3.3 Atomically update `~/.omp/agent/config.yml` with `modelRoles.commit` set to `omniroute/nx/deepseek-v4.1-flash` and `retry.fallbackChains` for `omniroute/nx/*`.

## 4. Live Verification and Cleanup

- [x] 4.1 Run `omp models --json` on the live profile to verify `omniroute/nx/deepseek-v4.1-flash` and associated entries are present.
- [x] 4.2 Execute a live JSON-mode probe: `omp --mode json --no-session --model 'omniroute/nx/deepseek-v4.1-flash' -p 'reply only: pong'` to verify direct execution without fallback events, verifying token metrics and reasoning capture via `omni-usage-logs` / `omni-inference` contracts.
- [x] 4.3 Clean up the temporary profile at `~/.omp/profiles/smoke-nx-models` and any temporary verification artifacts.
