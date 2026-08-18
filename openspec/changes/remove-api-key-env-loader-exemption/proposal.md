## Why

The generic config loader (`tdt_core/config_loader.py`) carries a backward-compat
exemption that accepts the retired `providers.*.api_key_env` field, while the
canonical schema parser (`parse_provider_model_config`) rejects it. This creates a
two-gate divergence: the loader's secret-policy scanner lets `api_key_env` through
(validating only env-var grammar), then the canonical parser fails it as an unknown
field. The `api_key_env` → `auth_env` migration completed on 2026-08-17 (live config
uses `auth_env`; no runtime code reads `api_key_env`), so the exemption is dead
compat that contradicts the fail-closed legacy-field contract and is a latent footgun
for any future consumer that reads `providers` without routing through the canonical
parser.

## What Changes

- **BREAKING** (for legacy configs only): Remove the `api_key_env` exemption block
  from `_v2_secret_policy()` in `tdt_core/config_loader.py`. With it gone,
  `api_key_env` matches the secret-shaped key regex and its bare env-var-name value
  fails the `${ENV}` reference grammar check, so the loader rejects it fail-closed
  with `ConfigError("secret-shaped key rejected at providers.<id>.api_key_env")` —
  consistent with the canonical schema's rejection and caught one layer earlier.
- Add a regression test asserting that a config containing `providers.*.api_key_env`
  is rejected by `load_config_mapping` (loader layer), complementing the existing
  `parse_provider_model_config` rejection test.
- Clean up the two stale legacy fixture directories still using `api_key_env`
  (`~/Developer/tdt-v2-credential-proof/`, `~/Developer/tdt-v2-accept/proof3/`) —
  historical proof artifacts from the pre-canonical-schema era that also use the
  dead `model.primary` top-level key. Each holds a `config.yaml` plus an empty `.env`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdt-env-loader-tdt-home`: Tighten "Typed configuration uses secret references" to
  state that retired credential-field names (e.g. `api_key_env`) are secret-shaped and
  rejected by the loader, with no backward-compat exemption.

## Impact

- **Code**: `tdt_core/config_loader.py` (remove 6-line exemption block, lines 202-207), one new test.
- **Behavior**: configs using the retired `api_key_env` field now fail at the loader
  with a clear `ConfigError` instead of passing the loader and failing later at the
  canonical parser with `SchemaError`. No live config is affected (all use `auth_env`).
- **No credential leak risk**: the canonical parser already rejects `api_key_env`;
  this only makes the loader consistent and fail-closed earlier.
- **Ownership**: tdt-core config loading.
