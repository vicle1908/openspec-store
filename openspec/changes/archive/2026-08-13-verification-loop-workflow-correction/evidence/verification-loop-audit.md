# Verification-loop audit evidence

**Date:** 2026-08-13
**Scope:** User-local OpenSpec workflow and review guidance; shared store change `verification-loop-workflow-correction`.

## Frozen store and CLI

```text
openspec: 1.8.0
verification baseline HEAD: 7928ddd772e671cacbf592511411b6a30cda5599
verification baseline branch: main
verification baseline store doctor: healthy=true, issues=[]
pre-closure snapshot: 2 dirty/untracked paths, including the corrective evidence and unrelated research report

The baseline SHA and dirty-path count above are historical evidence captured before the scoped closure commits; they are not claimed as post-commit provenance.
```

At the verification baseline, the store was dirty in unrelated paths. No unrelated path was edited, staged, or archived. Earlier baseline validation at `97ce028d31bd0213e44094ac989a26d8e74f3a22` is retained below as historical evidence, not current provenance.

## Reproduced state mismatch

Command:

```text
openspec status --change complete-agent-llm-config-integration --json --store openspec-store
```

Observed: `isComplete=true`; proposal, specs, design, and tasks artifacts all reported `done`.

Command:

```text
openspec instructions apply --change complete-agent-llm-config-integration --json --store openspec-store
```

Observed at the current baseline: `state=ready`, `progress.total=154`, `complete=0`, `remaining=154`.

Interpretation: status completion is planning-artifact completion, not implementation completion.

## Reproduced command-scope failure

From `~/Developer/agent-core`:

```text
openspec validate --strict --no-interactive --json
```

Observed: exit 1, `Nothing to validate`.

From the registered store:

```text
openspec validate complete-agent-llm-config-integration --strict --store openspec-store
```

Observed: exit 0, focused change valid.

## Reproduced shell-count failure

The legacy pattern:

```bash
done_count=$(grep -c '\\[x\\]' missing/tasks.md 2>/dev/null || echo 0)
todo_count=$(grep -c '\\[ \\]' missing/tasks.md 2>/dev/null || echo 0)
```

produced `done_count=$'0\n0'` and `todo_count=$'0\n0'`; arithmetic expansion then failed with a syntax error. The corrected guidance uses the OpenSpec-compatible Python checkbox parser.

## Validation results

Focused:

```text
openspec validate verification-loop-workflow-correction --strict --no-interactive --json --store openspec-store
exit=0; items=1; passed=1; failed=0
```

Full store before unrelated LSP drift:

```text
openspec validate --all --strict --no-interactive --json --store openspec-store
exit=0; items=373; passed=373; failed=0
```

Current full-store run at the verification baseline:

```text
openspec validate --all --strict --no-interactive --json --store openspec-store
exit=0; items=374; passed=374; failed=0
```

The earlier LSP failures are historical evidence from a prior concurrent-edit state, not a current blocker.

## Official documentation reconciliation

- Installed CLI: `@fission-ai/openspec` 1.8.0 from Homebrew (`/opt/homebrew/Cellar/openspec/1.8.0`), repository `https://github.com/Fission-AI/OpenSpec`.
- Exact-version CLI reference: `https://raw.githubusercontent.com/Fission-AI/OpenSpec/v1.8.0/docs/cli.md`.
- Exact-version store guide: `https://raw.githubusercontent.com/Fission-AI/OpenSpec/v1.8.0/docs/stores-beta/user-guide.md`.
- Official v1.8.0 semantics match the local CLI on root selection and lifecycle: `--store` selects a registered store ID; `status`, `instructions`, `validate`, and `show` support agent-oriented JSON; `archive` finalizes a completed change and is not a dry-run.
- Documentation gap: the installed 1.8.0 `openspec archive --help` exposes `--json` (`Output as JSON (non-interactive)`), while the exact v1.8.0 `docs/cli.md` archive-options table does not list that flag. Treat local `--help` as the version-pinned flag source, and do not infer dry-run behavior from the flag name.
- Rolling `HEAD` documentation was checked separately and treated as current/beta guidance, not as proof of older behavior.

## Additional correctness and loop-prevention findings

- Installed source inspection (`dist/core/archive.js`) confirmed incomplete-task behavior: without `--yes`, JSON mode returns `archive_tasks_incomplete`; interactive mode warns/asks; with `--yes`, the command continues and prints a warning. Guidance now treats `--yes` as a real override, never as harmless preview/readiness behavior.
- `active-change-triage.md` used fragile `grep -c ... || true` arithmetic and claimed archive would refuse incomplete tasks. It now uses `instructions apply` progress and explicitly requires independent evidence before any `--yes` archive.
- `implementation-pitfalls.md` used direct `grep -c` task counts and broad `git add -A`/unscoped validation in its archive workflow. It now uses the CLI task surface and scoped staging/validation.
- `phase-rollout-evidence.md` had unscoped final validation/doctor commands; these now use an explicit store ID and preserve exit codes.
- CLI review references required a second full provider round after remediation even when no state changed. They now require bounded re-review only for changed artifacts/evidence or failed/unknown/actionable findings.
- Plan/code review skills previously requested unrestricted reviewer permissions (`bypassPermissions`, `--dangerously-skip-permissions`) despite a read-only review contract. They now require bounded read-only execution and installed-help verification.
- Code-review context guidance previously wrote `.review-context.md` inside the active change and piped test output through `tail`; it now uses a disposable external context file and removes the masking pipeline.
- Historical CLI v1.7 guidance now has an explicit 1.8.0 correction overlay. Historical examples remain labeled rather than silently rewritten.


- Primary workflow: four-state lifecycle model, explicit store-scoped validation, task progress from `instructions apply`, safe task parser, finite state-change-gated rounds, and archive warning semantics.
- Plan/code review skills: explicit store scope, max-three reviewer batches, and bounded dispatch.
- Review governance and multi-agent orchestration: structural-vs-implementation state distinction and store-scoped evidence.
- Pre-archive, MoA, consolidated-closure, shared-provider, browserbase, reconciliation, and related operational references: removed actionable unscoped/masked verifier commands.

Historical or explanatory command mentions were not blindly rewritten; CLI help/history examples remain illustrative. Actionable high-risk workflow/review examples were corrected.
