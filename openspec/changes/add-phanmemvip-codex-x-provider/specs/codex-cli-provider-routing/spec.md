# Spec Delta

## Purpose

Owns the Codex CLI provider inventory (`[model_providers.*]` in `~/.codex/config.toml`) and the swapable profile-launcher pattern, so Codex can select the phanmemvip provider and its `codex-x` model.

## ADDED Requirements

### Requirement: Codex SHALL expose a phanmemvip provider in its provider inventory

The Codex CLI config (`~/.codex/config.toml`) SHALL declare a `[model_providers.phanmemvip]` provider that targets `https://api.phanmemvip.shop/v1` with `wire_api = "responses"`, `requires_openai_auth = true`, and `env_key = "HERMES_CUSTOM_PHANMEMVIP_API_KEY"`. It SHALL coexist with the existing `codex_local_access` and `omniroute` providers; no existing provider block SHALL be removed or altered.

#### Scenario: phanmemvip provider block is present and correct

- **WHEN** `~/.codex/config.toml` is inspected
- **THEN** a `[model_providers.phanmemvip]` block SHALL exist with `base_url = "https://api.phanmemvip.shop/v1"`
- **AND** it SHALL set `wire_api = "responses"`
- **AND** it SHALL set `env_key = "HERMES_CUSTOM_PHANMEMVIP_API_KEY"`
- **AND** `codex_local_access` and `omniroute` provider blocks SHALL remain unchanged

#### Scenario: phanmemvip provider reuses the registered credential key

- **WHEN** the phanmemvip provider's `env_key` is inspected
- **THEN** it MUST equal `HERMES_CUSTOM_PHANMEMVIP_API_KEY` (registered in the custom-provider credential registry)
- **AND** the config SHALL NOT contain a literal key value or token

### Requirement: The phanmemvip profile SHALL select the codex-x model with xhigh effort

A swapable profile `~/.codex/phanmemvip.config.toml` SHALL set `model = "codex-x"`, `model_provider = "phanmemvip"`, and `model_reasoning_effort = "xhigh"`. It SHALL mirror the `omniroute.config.toml` launcher pattern: the main `config.toml` retains its full provider inventory and is swapped (copied over), not edited in place, to select phanmemvip.

#### Scenario: profile selects phanmemvip/codex-x

- **WHEN** the profile is applied as the active `config.toml`
- **THEN** Codex SHALL use `model_provider = "phanmemvip"` and `model = "codex-x"`
- **AND** `model_reasoning_effort` SHALL be `xhigh`

#### Scenario: swap leaves the main inventory intact

- **WHEN** the phanmemvip profile is applied and later reverted
- **THEN** the restored `config.toml` SHALL retain all original provider blocks and defaults
- **AND** no provider block SHALL be lost during the swap

### Requirement: codex-x SHALL resolve from the phanmemvip gateway without a forced catalog entry

Codex SHALL resolve `codex-x` from the phanmemvip gateway's live `GET /v1/models` endpoint, which lists `codex-x`. No `cockpit-model-catalog.json` entry SHALL be required. A catalog entry is added only if a real Codex session fails to list the model.

#### Scenario: gateway lists codex-x

- **WHEN** `GET https://api.phanmemvip.shop/v1/models` is queried with the phanmemvip key
- **THEN** the returned model list SHALL contain an entry with `id = "codex-x"`
- **AND** a catalog edit SHALL NOT be required for Codex to select it

#### Scenario: catalog fallback is conditional

- **WHEN** a real Codex session cannot list `codex-x` from the gateway
- **THEN** a `codex-x` entry SHALL be added to `cockpit-model-catalog.json` as a fallback
- **AND** the absence of a catalog entry alone SHALL NOT be treated as a provider failure when the gateway lists the model
