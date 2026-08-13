# Design: verification-loop-workflow-correction

## State model

The workflow must keep four signals separate:

| Signal | Authoritative command | Meaning | Not proven |
|---|---|---|---|
| Planning | `openspec status --change <name> --json` | Artifact graph is complete/unblocked | Implementation, tests, live acceptance |
| Implementation | `openspec instructions apply --change <name> --json` | Task checkbox progress and remaining work | Structural validity or runtime behavior |
| Structure | `openspec validate <name> --strict --store openspec-store` | Change/spec syntax and delta validity | Product implementation or task evidence |
| Closure | Repository SHAs, test evidence, review disposition, archive and post-archive checks | Change is historically closed | Future runtime state |

## Verification protocol

1. Freeze the change name, store identity, current SHA/branch, and worktree state.
2. Read `status --json` only for planning/artifact paths and schema.
3. Read `instructions apply --json` for task progress. Do not infer progress from `status.isComplete`.
4. Run focused structural validation with the registered store ID.
5. Run the full-store check once as a regression check and classify unrelated failures.
6. Execute implementation and runtime gates from the owning repository; retain exact exit codes.
7. Repeat a gate only if the reviewed artifact, source/runtime state, or revision changed. Otherwise reuse the recorded result and advance to evidence/reporting.
8. Archive only after implementation tasks, verification tasks, and closure tasks are independently evidenced and checked. Never use `--yes` to bypass an incomplete-task warning.

## Safe task counting

Use the same grammar as OpenSpec 1.8.0: indented `-`/`*` bullets with `[ ]`, `[x]`, or `[X]`. Parse a missing file as zero tasks without shell fallback output. A zero-task file is not implementation-complete; it is either a planning artifact with no tracked work or a malformed/incomplete task surface requiring classification.

## Scope

The correction applies to the user-local OpenSpec workflow, review-governance, plan-review, and code-review guidance. The shared-store change records the contract and evidence; it does not mutate product repositories or archived history.
