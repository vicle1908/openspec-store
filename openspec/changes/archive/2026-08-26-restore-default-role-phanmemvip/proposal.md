## Why

Live `/Users/androidteam/.omp/agent/config.yml` lost its `modelRoles.default` binding after an external removal. Without the explicit binding, OMP resolves the default role to `gemini-3.1-pro:xhigh` instead of phanmemvip, breaking intended default-role routing.

## What Changes

- Restore `modelRoles.default` to `phanmemvip/gpt-5.6-sol:max`.
- Leave every other model role and fallback chain unchanged.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `omp-provider-routing`: Modify Capability-based role allocation so the default binding is explicitly `phanmemvip/gpt-5.6-sol:max`.

## Ownership Boundaries

- Planning artifacts and the canonical `omp-provider-routing` specification are owned by `/Users/androidteam/Developer/openspec-store`.
- The live implementation edit is an explicitly requested external configuration mutation at `/Users/androidteam/.omp/agent/config.yml`.

## Non-goals

- No changes to any other role.
- No changes to fallback chains.
- No changes to `models.yml`.
- No changes to credentials or secret values.
