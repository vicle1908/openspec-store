## Why

Two LLM runtimes — Hermes and omp — operate on the same three providers
(shopapikey, giaoduc, cockpit) but are governed by config schemas that diverge from
the canonical TDT schema, and neither divergence is documented as an intentional
boundary. Readers cannot tell whether the differences are drift to be fixed or
deliberate separation to be preserved. The `cli-provider-profile-resolution` spec
already excludes `prime-agent` and `claude-code-provider-adapter` as separate runtime
boundaries, but omits `omp` despite omp having its own 15-requirement spec.

## What Changes

- **Add omp to the CLI boundary exclusion list**: `cli-provider-profile-resolution`
  has a "Separate runtime boundaries remain explicit" requirement that excludes
  `prime-agent` and `claude-code-provider-adapter`. Add `omp` (oh-my-pi) with its
  exclusion reason: omp owns its own `models.yml` provider blocks, role allocation,
  and credential env-var references, governed by the `omp-provider-routing` capability.

- **Document Hermes provider-config boundary**: `hermes-moa-configuration` uses
  `providers.<name>.model` and `providers.<name>.context_length` fields that do not
  exist in the canonical TDT provider schema (which has `transport`, `protocol`,
  `auth_env`, `cli_provider`, `base_url`, and model-level `context_window`). Add a
  requirement stating that Hermes provider configuration is a separate runtime surface
  not governed by the canonical TDT schema, and that context-window ownership at the
  provider level is intentional for Hermes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `cli-provider-profile-resolution`: Extend "Separate runtime boundaries remain
  explicit" to include omp with its exclusion reason.
- `hermes-moa-configuration`: Add a requirement documenting that Hermes provider
  configuration is a separate runtime surface from the canonical TDT schema.

## Impact

- **Specs only** — no code or config changes. Both runtimes already work as described.
- **No breaking changes** — this documents existing, intentional separation.
- **Affected specs**: 2 canonical LLM specs in `openspec/specs/`.
- **Ownership**: cli-provider-profile-resolution (omp exclusion),
  hermes-moa-configuration (Hermes boundary statement).
