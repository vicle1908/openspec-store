# Proposal

## Why

The `claude-opus-5.5` combo previously routed exclusively to a single `combo-ref: gemini-3.8-flash-high` step without calling Claude models, and `claude-sonnet-5.5` did not exist as a gateway combo, causing Claude requests sent to OmniRoute to bypass Antigravity Claude capacity entirely. Furthermore, including `combo-ref: gemini-3.8-flash-high` inside an `auto` combo causes `resolveNestedComboTargets` to flatten all 15 `gemini-3.8-flash-high` steps into the `auto` candidate pool, where `selectAutoProvider` scores `gemini-3.8-flash-high` (`0.682`, cheaper/faster) higher than `claude-opus-4-6-thinking` / `claude-sonnet-4-6` and hijacks 100% of Claude requests to Gemini Flash. Live testing confirmed that all 15 active Google Antigravity (`agy`) OAuth connections have working access to `agy/claude-opus-4-6-thinking` and `agy/claude-sonnet-4-6` (HTTP 200, 1–3s latency across Pro, Ultra, and Free accounts), whereas synthetic 5.5 IDs (`claude-opus-5-5-high`, `claude-sonnet-5-5-high`) return upstream `429: Resource has been exhausted` because Google has not yet activated 5.5 endpoints on these tokens. Pooling all 15 Antigravity accounts as pure Claude model pools under `claude-opus-5.5` and `claude-sonnet-5.5` provides genuine, high-throughput, 15-account Claude routing with an explicit contract to cut over to 5.5 identifiers as soon as Google provisions them upstream.

## What Changes

- **Update `claude-opus-5.5` Combo with Pure 15-Account Antigravity Opus Pool**:
  - Reconfigure `claude-opus-5.5` (combo ID: `4b2430da-0b3b-4b0e-9773-ec0f97adc252`) via `GET /api/combos/{id}` -> merge existing `config` -> `PUT /api/combos/{id}`.
  - Populate 15 explicit connection-scoped model steps targeting `agy/claude-opus-4-6-thinking` across all 15 active `agy` connections (`weight: 0`) without a `gemini-3.8-flash-high` `combo-ref` step (preventing `auto` scorer hijacking to Gemini Flash).
  - Preserve `strategy: "auto"`, `config.candidatePool: ["agy"]`, `zeroLatencyOptimizationsEnabled: true`, `predictiveTtftMs: 25000`, `fallbackCompressionMode: "off"`, `hedging: false`, and set `context_cache_protection: false` (to enable per-connection session stickiness across the 15 accounts).
- **Create `claude-sonnet-5.5` Combo with Pure 15-Account Antigravity Sonnet Pool**:
  - Create combo `claude-sonnet-5.5` (combo ID: `9447399c-856b-4f52-8820-b3bf3dc3f132`) via `POST /api/combos`.
  - Populate 15 explicit connection-scoped model steps targeting `agy/claude-sonnet-4-6` across all 15 active `agy` connections (`weight: 0`).
  - Configure `strategy: "auto"`, `config.candidatePool: ["agy"]`, `zeroLatencyOptimizationsEnabled: true`, `predictiveTtftMs: 25000`, `fallbackCompressionMode: "off"`, `hedging: false`, and `context_cache_protection: false`.
- **Future 5.5 Cutover Contract**:
  - Document the operational requirement: when Google Antigravity provisions and advertises `claude-opus-5-5-*` and `claude-sonnet-5-5-*` in its live discovery catalog, update the 15 step model IDs in these combos to the upstream 5.5 names without changing combo routing topology or account mappings.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `omniroute-compression-and-routing`: Add requirements for 15-account Claude Opus (`claude-opus-5.5`) and Claude Sonnet (`claude-sonnet-5.5`) combo pooling and future upstream 5.5 cutover contracts.

## Impact

- **Affected Ownership Boundaries**:
  - OmniRoute SQLite database (`/app/data/storage.sqlite` in named volume `omniroute-data`): updates `combos` table row for `claude-opus-5.5` and creates `claude-sonnet-5.5`.
  - Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store/`): delta spec in `specs/omniroute-compression-and-routing/spec.md`.
- **Explicit Non-Goals**:
  - Modifying any git-tracked source files inside `/Users/androidteam/Omniroute/`.
  - Pinning un-provisioned `claude-opus-5-5-*` or `claude-sonnet-5-5-*` model IDs to `agy` connections while Google returns 429 quota exhaustion.
  - Modifying existing `gemini-3.8-flash-high` or `gemini-4-argon*` combos.
