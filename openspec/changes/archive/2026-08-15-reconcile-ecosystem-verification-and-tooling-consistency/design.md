# Design: Reconcile Ecosystem Verification and Tooling Consistency

## Root causes

1. **False-positive pytest exit codes** — Prior verification piped `uv run pytest ... | tail` without `set -o pipefail`. The reported exit code was `tail`'s status (0), masking real pytest failures. This produced impossible rows like "PASS, 122 failed."

2. **`process_inventory()` returns success unconditionally** — The function increments a `failed` counter when any provider fails, but always logs `overall "success"` and exits 0. This conflicts with the fail-visible/non-zero-on-provider-failure contract.

3. **`.gitattributes` drift** — `mcp-router/.gitattributes` was untracked and contained obsolete/duplicate Graphify rules (now normalized to canonical form). The tracked 17 repositories all use the single canonical rule. `openspec-store` has no `.gitattributes` because it has no generated graph output.

4. **mcp-router verification blocked** — `node_modules` was absent, preventing lint/typecheck/test. A frozen-lockfile install resolves this without changing the lockfile.

5. **ProviderModelConfig `extra="forbid"` rejects `transport` field** — The `config.yaml` includes a `transport` field in provider definitions that the Pydantic `ProviderModelConfig` schema rejects. This affects `agent-docs-sync` (55 failures), `code-daily-scan` (2 failures), and all `agent-core` consumers. Root cause is in `tdt-core/src/tdt_core/provider_model_profile.py` where `ProviderConfig` has `model_config = {"extra": "forbid"}`.

6. **Tracked `graphify-out/` inconsistency** — Documentation calls output "generated" while repositories track it, causing central refresh to skip repos for being dirty. This is a runtime/spec decision requiring explicit resolution.

## Changes

### Runtime behavior fix
- `process_inventory()`: log overall `failed` status when any provider failed, return `RC_FAILURE` when `failed > 0`, retain continuation so all targets are attempted.

### Normalized merge attributes
- All 17 tracked `.gitattributes` files: single rule `graphify-out/graph.json merge=graphify`
- mcp-router: normalize untracked `.gitattributes` to match

### Verified tooling
- mcp-router: `npx pnpm@10.22.0 install --frozen-lockfile` restores dependencies
- All Python repos re-run with trustworthy exit capture (no pipe to tail)

## Verification
- `bash -n` on all shell scripts
- `process_inventory()` returns nonzero when any provider fails
- Accurate pytest exit codes for every Python repository
- mcp-router pinned pnpm gates with unchanged lockfile
- `openspec validate --all --strict` and `--archived --strict` pass
- `openspec store doctor` clean
- `git diff --check` in every touched repository
