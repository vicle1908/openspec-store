# Proposal

## Why

OmniRoute's `gemini-4-argon` combo (`id: f1cefc64-7662-4f0a-9234-84f70603cbe4`) currently fails with `HTTP 429` because its single target points to the disabled upstream sentinel `agy/gemini-4-argon-disabled` with a stale `config.candidatePool` (`["openai-compatible-responses-396066d4-c57b-44ab-9683-013cdaa89d49"]`), and OmniRoute lacks dedicated tier combos (`gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`) pinned to the two Google AI `Ultra` `agy` CLI accounts (`vinhghtk1908@gmail.com` and `vinhvumobile@gmail.com`). Reconciling `gemini-4-argon` and provisioning the three tier-specific combos over the two entitled `Ultra` `agy` CLI connections restores reliable Gemini 4 Argon routing across `/v1/responses` and `/v1/chat/completions` without hitting `HTTP 429` retry stalls on the 13 `Pro`-tier `agy` accounts.

## What Changes

- Reconcile the existing OmniRoute `gemini-4-argon` combo (`id: f1cefc64-7662-4f0a-9234-84f70603cbe4`) via `PATCH http://127.0.0.1:20128/api/combos/f1cefc64-7662-4f0a-9234-84f70603cbe4` to use strictly two `agy` CLI steps (`agy/gemini-4-argon-high`) pinned to the two Google AI `Ultra` accounts (`338764b8-1cd7-4946-b789-ee5dad4c5073` / `vinhghtk1908@gmail.com` and `0532bad4-2486-4286-8f06-510e9c678620` / `vinhvumobile@gmail.com`), with `strategy: "auto"`, `context_length: 1000000`, `context_cache_protection: false` (relying on built-in per-connection `sessionStickiness`), `config.candidatePool: ["agy"]`, `config.resetAwareQuotaCacheTtlMs: 300000`, and `config.resetAwareQuotaCacheMaxStaleMs: 3600000`.
- Provision three dedicated tier-specific OmniRoute combos (`POST http://127.0.0.1:20128/api/combos`):
  - `gemini-4-argon-high`: two `agy/gemini-4-argon-high` steps pinned to `338764b8-1cd7-4946-b789-ee5dad4c5073` and `0532bad4-2486-4286-8f06-510e9c678620`.
  - `gemini-4-argon-medium`: two `agy/gemini-4-argon-medium` steps pinned to `338764b8-1cd7-4946-b789-ee5dad4c5073` and `0532bad4-2486-4286-8f06-510e9c678620`.
  - `gemini-4-argon-low`: two `agy/gemini-4-argon-low` steps pinned to `338764b8-1cd7-4946-b789-ee5dad4c5073` and `0532bad4-2486-4286-8f06-510e9c678620`.
- Remove the un-suffixed manual custom model `agy/gemini-4-argon` (`source: "manual"`) via `~/.local/bin/omniroute models remove agy gemini-4-argon --yes` so pure-auto catalog expansion never selects a model ID absent from Google Cloud Code's live `v1internal:streamGenerateContent` catalog (`HTTP 400`).
- Register `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` alongside `gemini-4-argon` under `providers.omniroute.models` in `~/.omp/agent/models.yml`, and add explicit fail-closed fallback entries in `~/.omp/agent/config.yml` (`retry.fallbackChains`).

### Non-Goals

- Modifying git-tracked source files inside `/Users/androidteam/Omniroute` (all combo and catalog adjustments execute through OmniRoute's live management REST API and CLI).
- Including any of the 13 Google AI `Pro` `agy` accounts (`vicgnome*`, `phamkive425@gmail.com`, `ascenddevtwo@gmail.com`, `vicle1908@gmail.com`, `ghtkmobile@gmail.com`) in the Argon 4 combos, as upstream Google Cloud Code only entitles `Ultra` accounts to `gemini-4-argon-{high,medium,low}` and returns `gemini-4-argon-disabled` (`HTTP 429`) on `Pro` accounts.
- Mutating existing coding-agent default model selections (`gemini-3.8-flash-high` across `codex`, `kimi-code`, `goose`, `zed`, `qwen`, `pi`, and Claude Code, or `muse-spark-1.3` in Muse Code) or changing OMP's active `modelRoles` assignments.

### Ownership Boundaries

- **OmniRoute Runtime State (`http://127.0.0.1:20128`, Docker volume `omniroute-data`)**: Owns combo definitions (`/api/combos`) and manual provider model overrides (`/api/provider-models`) managed via `~/.local/bin/omniroute` and authenticated loopback REST endpoints.
- **OMP Agent Configuration (`~/.omp/agent/models.yml`, `~/.omp/agent/config.yml`)**: Owns static `omniroute` provider model catalog declarations and `retry.fallbackChains` rules for OMP.
- **Central OpenSpec Governance (`/Users/androidteam/Developer/platform/openspec-store`)**: Owns specification deltas and verification evidence under `omniroute-agent-cli-routing` and `omp-provider-routing`.

## Capabilities

### New Capabilities

<!-- None -->

### Modified Capabilities

- `omniroute-agent-cli-routing`: Add requirements governing OmniRoute's `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `gemini-4-argon` combos backed exclusively by the two Google AI `Ultra` `agy` CLI connections (`338764b8-1cd7-4946-b789-ee5dad4c5073` and `0532bad4-2486-4286-8f06-510e9c678620`) with `config.candidatePool: ["agy"]` and removal of the invalid manual `agy/gemini-4-argon` catalog override.
- `omp-provider-routing`: Extend the OmniRoute model catalog and fallback chain requirements in `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml` to include `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, and `omniroute/gemini-4-argon-low` alongside `omniroute/gemini-4-argon`.

## Impact

- **OmniRoute Gateway (`http://127.0.0.1:20128`)**: Exposes top-level combo IDs `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `gemini-4-argon` on `/v1/models`, `/v1/responses`, and `/v1/chat/completions`, load-balanced across the two `Ultra` `agy` CLI accounts with built-in per-connection session stickiness, 5-minute quota-cache TTL (`300000` ms), and `1,000,000` token context windows.
- **OMP CLI (`~/.omp/agent/`)**: Enables direct selection of `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, and `omniroute/gemini-4-argon` with fail-closed fallback to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high`.
