# Design: remove-api-key-env-loader-exemption

## Context

See proposal.md — Why. Investigation traced the full call graph of
`_v2_secret_policy()` and confirmed the exemption is dead compat:

- The exemption was added 2026-08-11 (`8496f8e`, v2 config primitives) during the
  `api_key_env` → `auth_env` migration and survived the legacy-removal refactor
  (`08890f9`).
- Two consumers read `load_config_mapping` output: `resolve_agent_profile` (routes
  `providers` through `parse_provider_model_config`, which rejects `api_key_env` via
  `extra="forbid"`) and `TDTSettings.load` (`extra="ignore"`, no provider fields —
  silently drops `providers`). Neither leaks the field.
- No runtime code reads `api_key_env` from loaded mappings (grep-verified).
- Live `~/.tdt/config.yaml` uses `auth_env` (0 occurrences of `api_key_env`).
- `auth_env` does not match the secret regex, so it passes the loader naturally —
  the exemption exists only for the retired field name.

## Goals / Non-Goals

**Goals:**
- Make the loader fail-closed on `api_key_env`, consistent with the canonical parser.
- One regression test at the loader layer.
- Remove the two stale legacy fixtures.

**Non-Goals:**
- Changing the canonical parser (already correct).
- Migrating any consumer (none use `api_key_env`).
- Touching the secret regex or `${ENV}` reference grammar.

## Decisions

### D1: Delete the exemption rather than convert it to an explicit rejection

Removing the block lets the existing secret-shaped path reject `api_key_env`
(`classify_secret_key("api_key_env")` is True; the bare-name value fails the
`${ENV}` grammar). This reuses the established fail-closed machinery and produces
the standard "secret-shaped key rejected at <path>" error. Alternative considered:
replace the exemption with a dedicated `ConfigError("retired field api_key_env")`
message — rejected as extra code for marginal message improvement; the standard
message already names the path.

### D2: Test at the loader layer, not the parser layer

`test_canonical_agent_contract.py:125` already proves parser-layer rejection. The
new test targets `load_config_mapping` to lock the loader-layer behavior the change
creates. Alternative considered: end-to-end via `resolve_agent_profile` — rejected
as redundant coverage of the same assertion.

### D3: Also correct the stale registry scenarios in the same capability

While reviewing the delta, the main spec's "Environment-key registry" requirement was
found to contain the same stale `api_key_env` references and a false claim that
`credential_entry()` gates resolution. Verified against live code:
`resolve_agent_profile()` builds `CredentialAvailability` from
`provider.auth_env in os.environ` (agent_profile.py:788-789) — the registry is
credential metadata, not a resolution-time gate. Since this change already modifies
the same capability, the corrected registry requirement is included here rather than
in a separate change.

### D4: Delete stale fixtures, don't migrate them

`tdt-v2-credential-proof/` and `tdt-v2-accept/proof3/` are Aug 12 proof-artifact
directories (each a `config.yaml` using the dead `model.primary` schema plus an
empty `.env`); the current `verify_v2_codex_acceptance.py` writes its own canonical
YAML and reads only the nonce output file, not these fixtures. Deleting the two
directories avoids leaving configs that would now fail the loader. Alternative
considered: migrate them to `auth_env` — rejected because nothing consumes them.

## Risks / Trade-offs

- [An unknown external consumer loads a legacy config through the loader] → The
  failure is loud and early (`ConfigError` naming the exact path), which is the
  intended fail-closed behavior; migration guidance is `api_key_env` → `auth_env`.
- [Error message says "secret-shaped" for a non-secret env-var name] → Acceptable;
  the message identifies the path, and the field IS classified secret-shaped by the
  shared regex. A clearer message can be a follow-up if it causes confusion.
- [Loader becomes more permissive for `api_key_env: ${REF}` form] → Verified edge case:
  currently the exemption's grammar check rejects a `${...}` value under `api_key_env`;
  after removal, the normal secret policy ACCEPTS it (like any `${REF}` under a
  secret-shaped key). This is still fail-closed end-to-end because the canonical
  parser rejects `api_key_env` as an unknown field regardless of value form
  (verified: `parse_provider_model_config` raises SchemaError). The delta spec
  documents both layers explicitly.

## Migration Plan

1. Remove exemption block, add loader-layer test, run tdt-core test suite.
2. Delete the two stale fixture files.
3. Rollback = revert the commit (restores exemption).

## Open Questions

None.
