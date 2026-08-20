# Task second correction report: clarify pydantic-ai harness evidence

Date: 2026-08-21
Repository: `/Users/androidteam/Developer/openspec-store`
Change: `clarify-pydantic-ai-harness-evidence`

## Result

The second correction was created, validated, archived, and post-validated
through the registered `openspec-store` CLI workflow. It corrects the
vendor-isolation purpose/boundary, distinguishes supported public agent-core
runtime options from private legacy aliases, names `compaction_enabled=false`
as the explicit compaction disablement, retains all existing scenario labels,
and narrows evidence language so deterministic results are not presented as
live-provider or live-compaction acceptance.

The new archive is:

`openspec/changes/archive/2026-08-21-clarify-pydantic-ai-harness-evidence/`

The existing correction archive remains preserved at:

`openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/`

## Resolved versions and implementation provenance

The resolved environments for `agent-core`, `agent-docs-sync`, and
`agent-harness` each reported:

```text
pydantic-ai=2.32.0
pydantic-ai-harness=0.23.0
```

The implementation identities supplied for this correction are:

| Repository | Implementation SHAs |
|---|---|
| `agent-core` | `1de06ca`, `2a560dd`, `03f5a3c` |
| `agent-harness` | `25f1dd1` |
| `agent-docs-sync` | `9c78670`, `4eff50c` |

These identities and versions are recorded as provenance; this correction did
not modify those repositories.

## Forwarding evidence

The new harness-forwarding command was run exactly as follows:

```bash
cd /Users/androidteam/Developer/agent-harness && \
  uv run pytest -q tests/test_harness_capability_forwarding.py
```

Result: exit 0, `2 passed`.

Package versions were resolved with the following command in each consumer
repository, each returning exit 0 and the versions shown above:

```bash
uv run python -c 'from importlib.metadata import version; print("pydantic-ai=" + version("pydantic-ai")); print("pydantic-ai-harness=" + version("pydantic-ai-harness"))'
```

## CLI lifecycle evidence

The store was selected with `openspec store list --json`; it resolved
`openspec-store` to `/Users/androidteam/Developer/openspec-store`.

Creation:

```text
openspec new change "clarify-pydantic-ai-harness-evidence" --store openspec-store
exit 0
created openspec/changes/clarify-pydantic-ai-harness-evidence/
schema: spec-driven
```

The required CLI status and instruction lookups resolved the new change root
to:

`/Users/androidteam/Developer/openspec-store/openspec/changes/clarify-pydantic-ai-harness-evidence/`

The proposal, specs, design, and tasks instructions were fetched with
`openspec instructions ... --json --store openspec-store` before authoring.

Pre-archive change validation:

```text
openspec validate clarify-pydantic-ai-harness-evidence --type change --strict --store openspec-store
exit 0: Change is valid
```

Pre-archive strict all-store validation:

```text
openspec validate --all --strict --store openspec-store
exit 0: Totals: 375 passed, 0 failed (375 items)
```

Pre-archive readiness:

```text
python3 ~/Developer/openspec-store/scripts/validate-archive-readiness.py \
  --change clarify-pydantic-ai-harness-evidence --json
exit 0: ready; 12 total tasks, 12 completed, 0 remaining; 3 delta specs; no warnings
```

The first archive attempt exited 1 without changing files because the
agent-core delta accidentally repeated the existing `One harness capability
configuration boundary` header. The delta was repaired, change validation and
readiness were rerun successfully, and the second CLI archive completed:

```text
openspec archive clarify-pydantic-ai-harness-evidence --yes --store openspec-store
exit 0
specs updated: agent-compaction, agent-core-capabilities, vendor-isolation
archived as 2026-08-21-clarify-pydantic-ai-harness-evidence
```

The CLI reported one expected warning: an existing capability's Purpose is
ignored during delta sync. Because the requested end state explicitly requires
the vendor-isolation Purpose to match its public SDK/internal adapter
requirements, the main Purpose line was then corrected in the scoped
`openspec/specs/vendor-isolation/spec.md` file. No dated archive or unrelated
active change was edited.

Post-archive checks:

```text
openspec validate --all --strict --store openspec-store
exit 0: Totals: 374 passed, 0 failed (374 items)

openspec list --json --store openspec-store
exit 0: active changes remain only establish-agent-observability-contract and align-jti-skill-runtime-contract

git diff --check
exit 0
```

The two archive directories above were both present after archive, and the
new archive is no longer listed as active.

## Changed-path and preservation evidence

Before the correction, the working tree had an unrelated untracked `reports/`
directory. After archive and the targeted Purpose correction, the scoped
tracked modifications were:

```text
openspec/specs/agent-compaction/spec.md
openspec/specs/agent-core-capabilities/spec.md
openspec/specs/vendor-isolation/spec.md
```

The CLI-created archived correction directory is:

```text
openspec/changes/archive/2026-08-21-clarify-pydantic-ai-harness-evidence/
```

The requested report is:

```text
.superpowers/sdd/2026-08-20-pydantic-harness-contract/task-second-correction-report.md
```

Only these three main-spec paths, the new CLI-created archive directory, and
this report are in scope for the correction commit. The pre-existing
`reports/` directory and both active unrelated changes remain outside the
scope and must not be staged.

## Evidence limits

The forwarding test and package-version probes are deterministic local
evidence. They do not claim a live provider call, live compaction behavior,
provider acceptance, external-network behavior, clean-install dependency
resolution, durable cross-process harness acceptance, or provider credential
validity. Compaction live behavior/provider acceptance is not claimed because
those paths were not directly run. The resolved shared environment versions do
not change the direct dependency/optional-extra ownership contract.
