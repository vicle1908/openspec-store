# Spec Delta

## ADDED Requirements

### Requirement: OmniRoute Gateway Gemini 4 Neon Quota-Weighted Routing Strategy and Transport Keepalive
OmniRoute SQLite database (`storage.sqlite`) on `iosteam-mac-mini` SHALL configure `gemini-4-neon*` combos with `strategy: "quota-weighted"`, SHALL set `feature_flags:RESPONSES_TRANSPORT_KEEPALIVE_ENABLED` to `'true'`, and SHALL reload the `omniroute` runtime cache.

#### Scenario: OmniRoute Neon combos use quota-weighted load balancing
- **WHEN** `SELECT name, data FROM combos WHERE name LIKE 'gemini-4-neon%'` is executed on `/app/data/storage.sqlite`
- **THEN** each of `gemini-4-neon`, `gemini-4-neon-high`, `gemini-4-neon-medium`, and `gemini-4-neon-low` SHALL declare `strategy: "quota-weighted"`
- **AND** `config.quotaWeightedFloorPercent` SHALL equal `5` and `config.quotaWeightedScoring` SHALL equal `'leftover'`
- **AND** requests dispatched to `gemini-4-neon` SHALL distribute across all active Google AI Pro connections rather than exhausting `step-1` exclusively

#### Scenario: Responses transport-only keepalive is active in OmniRoute runtime
- **WHEN** `SELECT value FROM key_value WHERE namespace = 'feature_flags' AND key = 'RESPONSES_TRANSPORT_KEEPALIVE_ENABLED'` is executed on `/app/data/storage.sqlite` and the `omniroute` runtime is reloaded
- **THEN** the returned value SHALL equal `'true'`
- **AND** `isFeatureFlagEnabled('RESPONSES_TRANSPORT_KEEPALIVE_ENABLED')` in the live `omniroute` process SHALL evaluate to `true`

### Requirement: Host Coding-Agent Fleet and Editor Integrations Default to Gemini 4 Neon with 512K Compaction Bounds
All configurable workstation coding agents and editor integrations on `iosteam-mac-mini` that default to OmniRoute SHALL configure `gemini-4-neon` as their primary default model at `high` reasoning effort, enforce context limit `512,000` with auto-compaction threshold `<= 400,000`, and register `gemini-4-neon*` combos under their active OmniRoute provider blocks.

#### Scenario: Host coding agents and editors default to Gemini 4 Neon
- **WHEN** `~/.kimi-code/config.toml`, `~/.config/opencode/opencode.json`, `~/.config/goose/config.yaml`, `~/.factory/settings.json`, `~/.grok/config.toml`, `~/.config/zed/settings.json`, `~/.config/kilo/kilo.jsonc`, `~/.cline/data/settings/providers.json`, and `~/.shb/.env` are inspected on `iosteam-mac-mini`
- **THEN** each surface SHALL designate `gemini-4-neon` (or client equivalent `omniroute-responses/gemini-4-neon`, `custom:OmniRoute-Gemini-4-Neon-11`) as its default interactive model
- **AND** `~/.config/goose/config.yaml` SHALL declare `GOOSE_CONTEXT_LIMIT: 512000` and `GOOSE_PLANNER_CONTEXT_LIMIT: 512000`, and `custom_omniroute.json` SHALL declare `context_limit: 512000`
- **AND** `~/.factory/settings.json` SHALL declare `compactionTokenLimitPerModel` with `"custom:OmniRoute-Gemini-4-Neon-11": 400000`
- **AND** `~/.shb/.env` SHALL specify `SHB_DEFAULT_MODEL=gemini-4-neon`

### Requirement: Cross-Host Setup Script Verification Parity for Gemini 4 Neon Combos
The workstation client setup script `scripts/setup-macbook-omniroute-client.sh` and its repository mirror SHALL include `gemini-4-neon` and `gemini-4-neon-{xhigh,high,medium,low}` in `required_combos`, maintain matching SHA-256 digests, and exit with code `0` under `--check` on `iosteam-mac-mini`.

#### Scenario: Setup script includes Gemini 4 Neon in required combo audit
- **WHEN** `~/Developer/scripts/setup-macbook-omniroute-client.sh --check` is executed on `iosteam-mac-mini`
- **THEN** the audit script SHALL include `gemini-4-neon` and `gemini-4-neon-{xhigh,high,medium,low}` in `required_combos`
- **AND** the script SHALL exit with code `0` confirming all required combos present in `/v1/models`
- **AND** `~/Developer/scripts/setup-macbook-omniroute-client.sh` and `platform/openspec-store/scripts/setup-macbook-omniroute-client.sh` SHALL have identical SHA-256 digests

### Requirement: Specialized Client Boundary Isolation for Codex CLI on Macmini
Codex CLI on `iosteam-mac-mini` SHALL retain `model = "gemini-4-hydrogen"` in `~/.codex/config.toml` and `~/.codex/omniroute.config.toml` while providing an absolute `~/.codex/model-catalog.json` that exposes `gemini-4-{neon,hydrogen,argon,carbon}`.

#### Scenario: Codex CLI preserves Hydrogen default while exposing full Gemini 4 catalog
- **WHEN** `~/.codex/config.toml`, `~/.codex/omniroute.config.toml`, and `~/.codex/model-catalog.json` are inspected on `iosteam-mac-mini`
- **THEN** `~/.codex/config.toml` and `omniroute.config.toml` SHALL both maintain `model = "gemini-4-hydrogen"`
- **AND** `~/.codex/model-catalog.json` SHALL declare entries for `gemini-4-neon` (`context_window: 512000`), `gemini-4-hydrogen` (`context_window: 1000000`), `gemini-4-argon` (`context_window: 1000000`), and `gemini-4-carbon` (`context_window: 1000000`, `default_reasoning_level: "high"`)
