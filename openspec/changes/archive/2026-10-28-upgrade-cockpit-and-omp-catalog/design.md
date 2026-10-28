# Design

## Context
See `proposal.md` for motivation and background. Cockpit Tools (`cockpit-cliproxy`) runs on `127.0.0.1:51006` and exposes an OpenAI Responses-compatible API authenticated by Bearer token (`HERMES_CUSTOM_COCKPIT_API_KEY`). OMP uses `api: openai-responses` to communicate directly with this backend. Upstream Cockpit has released `v1.3.75` while the local app is at `1.3.74`. OMP's current `models.yml` declares only 5 models with inflated 1M context limits and speculative image input configurations.

## Goals / Non-Goals

**Goals:**
- Upgrade `/Applications/Cockpit Tools.app` cleanly to `1.3.75` with backup and rollback capability.
- Synchronize local Homebrew tap formula (`Casks/cockpit-tools.rb`) to version `1.3.75` to prevent drift.
- Update `~/.omp/agent/models.yml` with all 10 native chat/coding models, 272k context limits, 128k output limits, text-only input modalities (`input: [text]`), and full reasoning levels capped at `max` (`low..max`) per OMP schema rules.
- Ensure zero disruption to active fallback chains during Cockpit service downtime.

**Non-Goals:**
- Modifying upstream tap remote repositories.
- Editing non-Cockpit provider blocks or fallback chains.
- Changing OmniRoute container bridge configurations or Hermes WebUI configurations.
- Registering specialized endpoints like `gpt-image-2.5` in OMP's coding catalog.

## Decisions

### Decision 1: DMG Direct Bundle Upgrade with Homebrew Tap Synchronization
- **Rationale**: The official Homebrew tap `jlcodes99/homebrew-cockpit-tools` formula is currently at `1.3.74` and lags behind upstream GitHub Release `v1.3.75`. Upgrading via the official signed `Cockpit.Tools_1.3.75_universal.dmg` release archive provides immediate access to `v1.3.75`. To prevent `brew upgrade --cask` from later downgrading the app to 1.3.74, the local tap formula at `/opt/homebrew/Library/Taps/jlcodes99/homebrew-cockpit-tools/Casks/cockpit-tools.rb` is updated to version `1.3.75` alongside the installation.
- **Alternatives Considered**: Wait for upstream tap maintainer PR. Rejected because release `1.3.75` is already published upstream and contains the new model additions.

### Decision 2: Context Window Set to 272,000 with 128,000 Output Ceiling and Text-Only Input
- **Rationale**: The Cockpit backend enforces a 272,000 token context window and auto-compacts at $90\%$ (244,800 tokens). Declaring 1M in OMP caused OMP to defer client-side compaction until exceeding backend limits, resulting in request truncation or rejection. Correcting to 272k synchronizes OMP's proactive compaction with the gateway. Furthermore, the live backend advertises `"input_modalities": ["text"]` across all chat models; setting `input: [text]` and omitting `imageCountBudget` prevents client-side image attachment failures.
- **Alternatives Considered**: Retain 1M context window and image budget. Rejected because it violates backend capabilities and causes runtime failures on large contexts or multi-modal prompts.

### Decision 3: Exclude `gpt-image-2.5` from OMP Coding Catalog
- **Rationale**: The live endpoint exposes `gpt-image-2.5` solely for image generation (empty `context_length`, no tool calling, no reasoning effort levels). OMP is a coding agent runtime; registering image generation models under chat provider blocks causes schema and tool execution errors.
- **Alternatives Considered**: Include `gpt-image-2.5` with dummy context limits. Rejected because it breaks tool-calling assumptions and cannot serve text chat turns.

### Decision 4: Preserve Existing Role Suffixes and Fallbacks
- **Rationale**: OMP's active `default` role is `cockpit/gpt-6.1-sol:high`. Preserving the `:high` suffix ensures continuous reasoning without inheriting unverified defaults. The `cockpit/*` fallback chain protects against `ECONNREFUSED` during the application upgrade.

## Risks / Trade-offs

- **Risk: Brief Port 51006 Downtime during App Replacement**:
  - *Mitigation*: OMP's `cockpit/*` fallback chain automatically routes requests to `google-antigravity/gemini-4-argon:high` during app restart.
- **Risk: macOS Gatekeeper Quarantine on DMG Extraction**:
  - *Mitigation*: Run `xattr -cr "/Applications/Cockpit Tools.app"` immediately after bundle replacement to clear quarantine bits before launching.
- **Risk: Rollback Requirement if 1.3.75 Regresses**:
  - *Mitigation*: Backup `/Applications/Cockpit Tools.app` to `/Applications/Cockpit Tools.app.bak-1.3.74` before removal.
