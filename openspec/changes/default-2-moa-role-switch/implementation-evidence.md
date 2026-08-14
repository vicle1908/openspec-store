# Implementation Evidence: `default-2` MoA Role-Switch Preset

Evidence captured on 2026-08-14. Credential values and authorization headers are excluded.

## Change and Baseline

- Change: `default-2-moa-role-switch`
- Worktree: `/Users/androidteam/Developer/openspec-default-2`
- Branch: `create-default-2-moa-role-switch`
- Baseline main before worktree creation: `7f4d8895 docs(openspec): correct Hermes skill ownership boundaries`
- Store was clean before change creation.
- Existing active changes were inspected and no active change claimed `default-2` or this Hermes MoA role-switch.

## Direct Provider Verification

Fresh direct Hermes sessions completed before mutation:

| Provider/model | Result | Evidence |
|---|---|---|
| `shopapikey:fable-5` | PASS | Exact `SHOPAPIKEY_HEALTH_OK`, exit 0, session `20260814_071122_b31b03` |
| `giaoduc:Advance` | PASS | Exact `GIAODUC_HEALTH_OK`, exit 0, session `20260814_071145_be12d9` |

The provider-health HTTP probe returned HTTP 200 for both endpoints, but its response shape was not classified as the expected normalized shape. Hermes-native direct sessions are the authoritative availability evidence for this change.

## Config Mutation

- Backup: `/Users/androidteam/.hermes/backups/config-before-default-2-20260814-071353.yaml`
- Backup SHA-256: `a72bb3fb81dca8bba5d0b04b3a0d4f95df753a293456bbce0b97ae41d1825b65`
- Pre-mutation config SHA-256: `a72bb3fb81dca8bba5d0b04b3a0d4f95df753a293456bbce0b97ae41d1825b65`
- Post-mutation config SHA-256: `ec8caa4d31020ab96e8b17f889f43acd31519e9d24fee8e1cdbe216870940376`
- Mutation method: atomic YAML replacement after parse/type assertions.

The only semantic addition was `moa.presets.default-2`. Existing preset hashes remained unchanged:

- `default`: `a380a203a3a4fe7900770991e176ec75a1aaffb129cb2f2ed54c4531b9d57c9c`
- `deep`: `941d3cd6581756fa29741a012e30248d4ef4115424e181f665db719c9f8e617b`
- `fast`: `d04dadcf5664cc6d48c1d25553ce978580072791fd828294a9f8b321c6925e37`

## Target Preset

```text
default-2:
  refs: shopapikey:fable-5(high), cockpit:gpt-5.6-sol(high)
  aggregator: giaoduc:Advance(xhigh)
  max_tokens: 8192
  reference_max_tokens: 1000
  reference_temperature: 0.6
  aggregator_temperature: 0.4
  fanout: every_n:3
  degraded_reference_policy: loud
  enabled: true
```

Post-mutation YAML assertions passed:

- `moa` remains a mapping.
- `moa` root keys remain exactly `default_preset`, `privacy_filter`, `presets`.
- No legacy flat-level MoA keys were introduced.
- `model.provider: moa` and `model.default: default` remain unchanged.
- Presets are `default`, `deep`, `default-2`, and `fast`.

## Hermes CLI Verification

- `hermes config check`: PASS, schema v34.
- `hermes config get moa`: PASS, shows `default-2` with the target slots.
- `hermes moa list`: PASS, shows `default-2` with shopapikey and cockpit references and giaoduc aggregator.

## Runtime Verification

### New route

Command:

```text
hermes chat -Q --provider moa -m default-2 --source default-2-role-switch-smoke --max-turns 8 -q 'Use the terminal tool to run printf "DEFAULT_2_TOOL_OK\\n". Then reply exactly DEFAULT_2_SMOKE_OK.'
```

Session: `20260814_071417_ccecdd`

Session-store evidence:

1. User request: message `148805`.
2. Assistant terminal function call: message `148806`.
3. Tool result `DEFAULT_2_TOOL_OK`, exit code 0: message `148807`.
4. Assistant continued with a terminal call: message `148808`.
5. Second tool result with the marker, exit code 0: message `148809`.
6. Final response `DEFAULT_2_SMOKE_OK`: message `148810`.

The shopapikey advisor failed with a provider-side HTTP 403 burst lock during this session, but the aggregator path continued successfully using the cockpit advisor and giaoduc aggregator. This proves degraded-reference isolation and aggregator tool continuation; it does not prove shopapikey availability at smoke time.

### Existing default route

Command:

```text
hermes chat -Q --provider moa -m default --source default-2-existing-default-check --max-turns 4 -q 'Reply exactly EXISTING_DEFAULT_CHECK_OK'
```

Session: `20260814_071509_1bf975`; exact response received; exit 0.

## Rollback

Restore `/Users/androidteam/.hermes/backups/config-before-default-2-20260814-071353.yaml` atomically, or remove only `moa.presets.default-2`, then rerun YAML assertions, `hermes config check`, `hermes moa list`, and the existing-default smoke check.
