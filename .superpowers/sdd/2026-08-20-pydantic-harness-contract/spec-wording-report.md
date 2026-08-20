# Spec Wording Correction Report

## Scope

Change: `clarify-pydantic-harness-spec-wording`
Store: `openspec-store` (`/Users/androidteam/Developer/openspec-store`)
Pre-change HEAD: `bc6e5a616d8f654527b95a6b9f7921fdd78e35d1` on `main`
Archive: `openspec/changes/archive/2026-08-21-clarify-pydantic-harness-spec-wording/`

The supplied verification report was read first:
`.superpowers/sdd/2026-08-20-pydantic-harness-contract/openspec-verify-clarify-pydantic-ai-harness-evidence.md`.
The prior correction archive was read before authoring:
`openspec/changes/archive/2026-08-21-clarify-pydantic-ai-harness-evidence/`.

## CLI workflow evidence

The change was created and inspected through the registered store:

```text
$ openspec new change clarify-pydantic-harness-spec-wording --description 'Correct the three pydantic-ai harness documentation contracts without changing product code.' --goal 'Clarify public runtime projection, compaction disablement, and vendor isolation wording.' --json --store openspec-store
exit 0; created /Users/androidteam/Developer/openspec-store/openspec/changes/clarify-pydantic-harness-spec-wording

$ openspec status --change clarify-pydantic-harness-spec-wording --json --store openspec-store
exit 0; proposal/specs/design/tasks resolved; isPlanningComplete=true; isComplete=true

$ openspec instructions proposal --change clarify-pydantic-harness-spec-wording --store openspec-store --json
exit 0
$ openspec instructions specs --change clarify-pydantic-harness-spec-wording --store openspec-store --json
exit 0
$ openspec instructions design --change clarify-pydantic-harness-spec-wording --store openspec-store --json
exit 0
$ openspec instructions tasks --change clarify-pydantic-harness-spec-wording --store openspec-store --json
exit 0
```

The authored delta paths are exactly:

- `specs/agent-compaction/spec.md`
- `specs/agent-core-capabilities/spec.md`
- `specs/vendor-isolation/spec.md`

All existing scenario labels were retained in their corresponding complete
modified requirement blocks. The correction names `compaction_enabled=false`,
adds it to supported public runtime options, keeps private aliases/config keys
separate, and describes intentional public SDK forwarding plus internal adapter
isolation.

## Validation and archive evidence

Before archive:

```text
$ openspec validate clarify-pydantic-harness-spec-wording --strict --store openspec-store
Using OpenSpec root: openspec-store (/Users/androidteam/Developer/openspec-store)
Change 'clarify-pydantic-harness-spec-wording' is valid
exit 0

$ openspec validate --all --strict --store openspec-store
Totals: 375 passed, 0 failed (375 items)
exit 0
```

Archive:

```text
$ openspec archive clarify-pydantic-harness-spec-wording --yes --store openspec-store --json
{
  "archive": {
    "change": "clarify-pydantic-harness-spec-wording",
    "archivedAs": "2026-08-21-clarify-pydantic-harness-spec-wording",
    "path": "/Users/androidteam/Developer/openspec-store/openspec/changes/archive/2026-08-21-clarify-pydantic-harness-spec-wording",
    "specsUpdated": true,
    "totals": { "added": 0, "modified": 6, "removed": 0, "renamed": 0 }
  }
}
exit 0
```

After archive:

```text
$ openspec validate --all --strict --store openspec-store
Totals: 374 passed, 0 failed (374 items)
exit 0

$ openspec status --change clarify-pydantic-harness-spec-wording --json --store openspec-store
exit 1; Change 'clarify-pydantic-harness-spec-wording' not found (archived as 2026-08-21-clarify-pydantic-harness-spec-wording)

$ git diff --check
exit 0
```

The one-item decrease is the expected transition from an active change to its
archive. The prior `2026-08-21-reconcile-pydantic-ai-harness-capability-contract`
and `2026-08-21-clarify-pydantic-ai-harness-evidence` archives remain present.

## CLI limitation requiring coordinator disposition

OpenSpec 1.10.0 archive applied all six modified requirement blocks but ignores
a delta `## Purpose` for an existing spec. Its instructions explicitly say to
edit the store's main spec directly to change an existing Purpose, and there is
no `openspec spec edit` command. Consequently, the post-archive main specs
contain the requested requirement changes, but these two purpose-level items
remain unchanged pending authorization for a narrow prose patch:

1. `openspec/specs/agent-compaction/spec.md` still has the historical sentence
   saying config fields “are not read by AgentRuntime”; the new requirement
   clarifies the projection boundary but the header note itself does not yet
   mention `AgentConfig.runtime_options()` or public `compaction_enabled=false`.
2. `openspec/specs/agent-core-capabilities/spec.md` still has `Purpose: TBD -
   created by archiving change upgrade-harness-23. Update Purpose after archive.`

No direct patch was made because the task explicitly forbids hand-editing
`openspec/` files. This report therefore records the exact blocker rather than
claiming those two purpose-level corrections are complete.

## Changed-path boundary

At the post-archive inspection, the only workspace changes were the three
CLI-synced main specs and the CLI-created archive tree. The requested report is
the only additional path in scope. No product source, dependency lock,
historical archive, unrelated active change, or `reports/` path was touched.
