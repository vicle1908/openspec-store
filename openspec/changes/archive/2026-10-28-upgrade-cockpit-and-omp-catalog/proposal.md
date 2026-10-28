# Proposal

## Why
Cockpit Tools provides a local native OpenAI Responses endpoint (`localhost:51006/v1`) that OMP uses as its active default coding model (`cockpit/gpt-6.1-sol:high`). Cockpit Tools has released upstream version `1.3.75` introducing `gpt-6.1-terra` and updated model manifests, while OMP's current `models.yml` declares an incomplete 5-model subset with inflated context windows (`1,000,000` tokens instead of the backend's enforced `272,000` limit and `244,800` compaction threshold). Upgrading Cockpit Tools to `1.3.75` and aligning OMP's static model catalog ensures OMP avoids compaction failures, gains access to all 10 native chat/coding models, and accurately reflects reasoning efforts up to `max`.

## What Changes
- Upgrade the local `/Applications/Cockpit Tools.app` bundle from `1.3.74` to `1.3.75` via the official upstream DMG release (`jlcodes99/cockpit-tools`).
- Synchronize the local Homebrew tap formula `/opt/homebrew/Library/Taps/jlcodes99/homebrew-cockpit-tools/Casks/cockpit-tools.rb` to version `1.3.75` to prevent Homebrew Cask drift on routine upgrades.
- Expand the OMP `cockpit` provider block in `~/.omp/agent/models.yml` from 5 to 10 chat/coding models:
  - Add missing models: `gpt-6.1-terra` (new in v1.3.75), `gpt-6-sol`, `gpt-6-luna`, `codex-auto-review`, and `gpt-reserve`.
  - Exclude specialized endpoint `gpt-image-2.5` (an image generation model lacking completion context, reasoning, and tool-call support).
  - Correct context windows from `1000000` to `272000` across all Cockpit models to match backend limits and prevent compaction errors.
  - Set explicit `maxTokens: 128000` output limits and correct thinking efforts (`low..max`).
  - Set input modalities to `input: [text]` matching live endpoint advertisement (`input_modalities: ["text"]`), omitting unsupported image budgets.
- Retain existing `modelRoles.default: cockpit/gpt-6.1-sol:high` and active fallback chains in `~/.omp/agent/config.yml`.
- Verify runtime service readiness on port `51006` and smoke test model resolution with fallback disabled.

## Capabilities

### Modified Capabilities
- `omp-provider-routing`: Update the Cockpit model catalog definition, context window constraints, input modalities, and reasoning configuration within OMP's custom provider specification.

## Non-Goals
- Modifying non-Cockpit provider blocks or fallback chains in `~/.omp/agent/models.yml` or `~/.omp/agent/config.yml`.
- Changing OmniRoute internal routing rules or Docker setup.
- Modifying Hermes WebUI configuration or port assignments.
- Exposing or rotating API key credentials.
- Registering non-chat models (such as `gpt-image-2.5`) in OMP's coding catalog.
