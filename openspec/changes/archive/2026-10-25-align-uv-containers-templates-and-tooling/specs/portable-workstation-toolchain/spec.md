# Spec Delta: portable-workstation-toolchain

## ADDED Requirements

### Requirement: Sanctioned uv Tool Receipt Reconciliation
The declarative `config/uv-tools.json` manifest in `platform/openspec-store` SHALL accurately record every sanctioned CLI tool installed under `~/.local/share/uv/tools/`, including package extras, pinned version specifiers where intentional, and companion `--with` dependency constraints recorded in `uv-receipt.toml`.

#### Scenario: Reconciling uv-tools.json with installed uv tool receipts
- **WHEN** inspecting `platform/openspec-store/config/uv-tools.json` against `uv tool list --show-version-specifiers` and `~/.local/share/uv/tools/*/uv-receipt.toml`
- **THEN** every installed `uv` tool (`graphifyy`, `tavily-cli`, `browser-use`, and `infinity-emb`) SHALL be declared in `config/uv-tools.json`
- **AND** `graphifyy` SHALL record its required `[mcp,watch,office,pdf,postgres]` extras and `infinity-emb` SHALL record its `[server]` extra and companion `--with` requirements so automated or manual workstation setup reproduces the exact tool environment on Python `3.15`.
