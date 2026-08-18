## 1. Code change (tdt-core)

- [x] 1.1 Remove the `api_key_env` exemption block from `_v2_secret_policy()` in `src/tdt_core/config_loader.py` (lines 202-207, the 6-line `if key == "api_key_env" ... continue` block)
- [x] 1.2 Add a loader-layer regression test: `load_config_mapping` rejects a mapping containing `providers.<id>.api_key_env`
- [x] 1.3 Add a companion test: `load_config_mapping` accepts `providers.<id>.auth_env` (guards against over-broad rejection)
- [x] 1.4 Run the tdt-core test suite (`uv run pytest`) and confirm green

## 1b. Spec correction (same capability)

- [x] 1b.1 Apply MODIFIED delta to "Environment-key registry" requirement: replace `api_key_env` references with `auth_env`, document registry as metadata (not resolution-time gate), preserve all original scenario names

## 2. Stale fixture cleanup

- [x] 2.1 Delete the stale `~/Developer/tdt-v2-credential-proof/` dir (config.yaml + empty .env; pre-canonical-schema proof artifact)
- [x] 2.2 Delete the stale `~/Developer/tdt-v2-accept/proof3/` dir (config.yaml + empty .env); leave sibling proof1/proof2/strict artifacts untouched
- [x] 2.3 Confirm `verify_v2_codex_acceptance.py` does not read either deleted file

## 3. Validation and archive

- [x] 3.1 Run `openspec validate remove-api-key-env-loader-exemption --strict`
- [x] 3.2 Commit the tdt-core change with evidence (test output)
- [x] 3.3 Archive the change
