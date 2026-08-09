---
name: multi-provider-review-orchestration
description: "Use for multi-provider reviews; verify provider evidence."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-provider, review, orchestration, openspec, cli, evidence]
    related_skills: [openspec-plan-review, openspec-code-review, kimi-code, claude-code, codex, antigravity]
---

# Multi-Provider Review Orchestration

Run reliable multi-provider reviews over a shared artifact set while preserving provider identity, read-only boundaries, and verifiable evidence. This is a class-level workflow for OpenSpec plans, code reviews, architecture reviews, and similar reviews—not a recipe for one change or one provider.

## Use When

- A user asks for a review from several AI providers or asks for a named provider's review.
- A review prompt covers multiple changes or repositories and requires a consolidated report.
- Provider names may refer either to model labels, gateway routes, MCP servers, or actual local CLI executables.
- The output must be saved as an artifact and backed by real provider execution.

## Core Rules

1. **Preserve the requested provider slot.** A provider/model label is not automatically a shell command. Verify the exact executable with `command -v`, `--version`, and `--help` before running it. Record the identity that actually produced each report.
2. **Never fabricate or silently substitute.** If the named CLI is unavailable, say so. Use an installed equivalent only when the user has authorized or the task context clearly identifies it as the same provider slot; disclose the substitution in the report summary. Otherwise mark that provider `UNKNOWN` or `NOT_REVIEWED` and continue with independent available reviewers.
3. **Do not replace requested execution with an in-process opinion.** Direct artifact reading can validate scope and help reconcile results, but it is not evidence that the requested provider ran. Keep locally reasoned observations separate from provider output.
4. **Collect the complete scope before review.** Enumerate every requested change and read all required artifacts (`proposal.md`, `design.md`, `tasks.md`, recursive `specs/`, and any explicitly required scope files). Check that each requested change appears in the saved report.
5. **Use read-only reviewer prompts.** Instruct providers not to edit files, create commits, mutate runtime systems, or expose secrets. Give each provider a focused lens and a shared output contract. Explicitly forbid printing Git remotes, credential-helper output, authentication diagnostics, environment variables, or config files: an HTTPS remote can contain an embedded token even when ordinary auth commands redact it. Prefer secret-free repository identity queries such as `gh repo view --json nameWithOwner` and sanitize all progress output before retaining or quoting it.
6. **Bound execution and preserve real output.** Use noninteractive print mode for one-shot reviews, a bounded host timeout, and `set -o pipefail` when piping. Verify the provider exit code, saved file size, line count, and coverage of all requested sections.
7. **Separate progress from findings.** Some CLIs emit planning/tool progress before the final answer. Preserve the raw output when requested, but identify the final report section and do not mistake preamble for findings. For machine-readable output, parse events defensively and retain the final assistant result separately.
8. **Consolidate without laundering uncertainty.** Preserve per-provider verdicts, unresolved provider failures, disagreements, and evidence limitations. Do not turn an unavailable provider into approval by inference.

## Workflow

### 1. Normalize the request

Create a checklist of:

- provider slots and assigned lenses;
- exact changes/repositories in scope;
- required artifacts and output format;
- output path and whether raw or cleaned provider output is requested;
- read-only and secret-handling constraints.

If the prompt says “for each change” but asks for a prompt that reviews all changes, clarify the intended invocation. If clarification is not possible, run the prompt exactly once when it explicitly says to produce one consolidated report, and verify all changes are present.

### 2. Verify provider identity

For each named provider, run independently:

```bash
command -v <cli>
<cli> --version
<cli> --help
```

Also inspect the configured model/provider mapping only through secret-safe commands. Never print API keys, tokens, or full environment files. If a name resolves only as a model in the current session, do not invoke it as a command; locate the documented CLI for that provider slot or report the slot unavailable.

### 3. Gather artifacts once

Read all artifacts before delegating. Build a compact, sanitized context bundle when the provider supports direct prompt context. Exclude credentials, `.env` contents, private keys, raw secret-bearing diagnostics, and unrelated repository data. For very large documents, preserve paths and line ranges so findings remain auditable.

### 4. Run reviewers

Prefer parallel calls for independent providers. Use separate worktrees only if a provider might write; for read-only reviews, explicitly prohibit writes and independently check the worktree afterward. Use the provider's native bounded noninteractive mode rather than guessing flags from another CLI.

**CLI-vs-delegation distinction.** When the user asks for coding-agent CLI reviews (for example `claude`, `agy`, `opencode`, `pi`, `codex`, `kimi`, or `goose`), invoke those real executables and report their actual exit/output. Do not substitute `delegate_task` reviewers. Use `delegate_task` only when the user requests Hermes subagents or when the orchestration plan explicitly assigns that mechanism.

**CRITICAL: Inline context delivery for delegate_task.** ALWAYS pass ALL evidence as inline text in the `context` parameter to `delegate_task`. NEVER pass file paths. File paths cause reviewers to exhaust their iteration budget reading files instead of producing analysis. Pre-collect: change artifacts (proposal, design, tasks), evidence bundles (tool outputs, config state), and reference material — all as strings. The context parameter should contain everything the reviewer needs. If the context exceeds 20KB, it is still better inline than as file paths.

```python
# CORRECT: inline content
context = f"## Proposal\n{proposal_text}\n## Evidence\n{evidence_bundle}"

# WRONG: file paths (reviewers waste iterations reading files)
context = "Read /path/to/proposal.md and /path/to/design.md"
```

**Version-gate provider flags.** Verify the exact subcommand surface with `<cli> <subcommand> --help`, not only `<cli> --version`. If a user mandates exact syntax that the installed version rejects, execute it once to capture the real nonzero status, then use the documented semantic equivalent only with explicit disclosure of both commands/statuses. For `codex-cli 0.146.0`, `codex exec --approval-policy never` exits 2 because that flag is absent; the equivalent is `codex exec -c 'approval_policy="never"' --sandbox read-only ...`. Re-check help on newer versions rather than carrying this compatibility fallback forward blindly. See `references/codex-readonly-review.md` for the verified recipe.

**Parallel dispatch pattern (proven):** Spawn one `delegate_task` subagent per CLI provider. Each subagent reads all change artifacts and invokes its assigned CLI tool with a focused review prompt. The host (Hermes) does its own review directly. This yields 5 parallel reviews with minimal coordination. Do NOT pipe CLI output through `head` — it can truncate the final report or kill the producer early.

For Kimi Code, use the actual `kimi` executable (Kimi is the provider name; do not relabel it as fable-5 or invent a `fable-5` command):

```bash
kimi -p "<read-only review prompt>" --output-format stream-json \
  > /tmp/kimi-review.jsonl 2>&1
```

Capture the complete stream before producing the human-facing artifact. Kimi may emit planning/tool events before its final assistant report; placing `head` before extraction can truncate the report or terminate Kimi early. Parse the JSONL and extract the last assistant record whose `content` is a string, then write that content to the requested report path. If raw shell output is explicitly requested, retain the full stream separately and disclose the progress/tool preamble.

Check the provider exit status independently and confirm the cleaned report contains every required change and verdict. See `references/provider-identity-and-capture.md` for the extraction recipe.

### 5. Validate the saved artifact

Verify:

- the file exists at the exact requested path;
- the provider command exited successfully;
- the final response is non-empty (a provider-level `SUCCESS` status alone is insufficient);
- all requested change names appear;
- the expected number of verdicts/sections appears;
- no secret-shaped values were introduced;
- no unrelated files were modified.

If output is streamed JSON, separate progress/tool events from the final assistant message before producing a cleaned report. If the user asked for raw shell output, retain the raw capture and mention any preamble. Treat an empty final response, a permission-denial preamble followed by `SUCCESS`, or a missing final-message file as an incomplete provider run; retry narrowly with corrected read permissions or mark the slot `UNKNOWN`.

### 5a. Guard against moving review targets

Multi-provider reviews can overlap with another agent committing or amending the branch. Freeze and record the target commit before dispatch, then re-check `HEAD`, worktree status, diff stat, and governing artifact revisions after reviewers finish. If any target moved, do not silently merge stale findings with the new state: rerun affected gates and reviewers against the final commit, or label the stale provider output with the commit it actually reviewed.

For inventory claims, independently enumerate content from the frozen commit rather than trusting the worktree, task prose, or prior reviews. Report per-file counts and sum them so off-by-one disagreements are auditable. If the plan has a “do not start when counts differ” gate, any mismatch is automatically material even when the rest of the design improved.

When proving read-only behavior in a dirty or shared workspace, capture status fingerprints immediately before and after the provider run. Compare in-scope paths separately from unrelated concurrent changes; do not claim the whole workspace was unchanged merely because the provider said so.

### 5b. Reconcile model opinions with executable probes

Provider approval is not stronger than a deterministic counterexample. For policy and security claims—exact exception binding, non-waivable rule families, symlink containment, unknown-state failure, schema/model parity—write the smallest read-only temporary probe that attempts to violate the invariant. Preserve the command and observed result in the consolidated evidence. When providers disagree, prefer file-backed findings plus reproducible probes, and record the disagreement rather than averaging verdicts.

### 6. Report concisely

Lead with the outcome and artifact path. State which provider actually ran, any substitution, exit status, and coverage. Summarize only the most important findings; the saved report is the detailed deliverable. Never claim a provider ran when only local inspection or another provider ran.

## Failure Handling

- **Hermes descriptor exhaustion after parallel CLI fan-out:** distinguish the active Hermes process from the OS limit. Check an independent shell/process channel for `ulimit -n`, `launchctl limit maxfiles`, and current FD counts. If the independent shell has a large soft limit but Hermes returns `EMFILE`, wait for tracked jobs to exit, clean review temp files, and restart Hermes/a fresh session; do not treat a global launchd-limit increase as the fix for the active process. Rerun remaining reviewers sequentially with raw capture after recovery.
- **CLI review context too large or path access is denied:** use a compact sanitized bundle; run OpenCode from the owning repository (or explicitly use its documented auto/permission mode) rather than `/tmp`; use Goose `--instructions <file>` or `--text <text>`, not both; preserve raw output and retry with a narrower prompt.
- **Named CLI not found:** distinguish setup state from provider semantics; do not encode it as a permanent tool limitation. Verify whether the name is a model label, route, MCP server, or alternate executable. If a working documented equivalent exists, use it only with explicit disclosure.
- **Provider timeout/stall:** inspect whether output is progressing, then terminate or retry with a narrower prompt. Preserve partial output as incomplete and mark the provider uncertain; do not infer a verdict.
- **Pipeline hides failure:** use `set -o pipefail`, rerun only after inspecting the first result, and verify the saved artifact.
- **Missing change in report:** treat the report as incomplete and rerun with an explicit scope list.
- **Provider edits files:** stop accepting the result, inspect the diff, restore only with user authorization, and report the violation.
- **Delegation batch "owner exited before recording terminal result":** The batch framework lost the consolidated result, but individual subagent transcripts still exist. Recovery:
  1. Read live transcript files at paths from the delegation response (e.g. `/Users/androidteam/.hermes/cache/delegation/live/{batch_id}/task-{N}.log`).
  2. Extract provider output from the last `assistant|` or `final|` lines in each transcript.
  3. If the provider ran as a background process, parse `process(log ...)` output for JSON results.
  4. Consolidate from available transcripts. Mark any provider whose transcript is empty or unreadable as `NOT_REVIEWED`.
  5. Never fabricate results from missing transcripts.
- **vars() serialization error on final summary:** All reviewers fail with `"vars() argument must have __dict__ attribute"` on their final summary. This is a provider-side serialization bug when the subagent's response object lacks `__dict__`. Every reviewer in the batch will hit it — it is NOT transient. **Fallback:** (1) Extract analysis from `think` entries in transcripts. (2) If transcripts are thin, perform the review yourself using the pre-collected evidence. (3) Write `review-plan.md` with your own findings. See `references/subagent-serialization-error-fallback.md` in openspec-workflow skill.
- **Codex WebSocket errors:** Even when `codex` binary exists and `command -v codex` succeeds, Codex may fail with `websocket_disabled` errors (HTTP 400 Bad Request). This is a provider-side configuration issue, not a missing installation. **Mark as NOT_REVIEWED** and continue. Do not retry — the error is persistent for the session.
- **Codex 429/502 rate limits:** Codex hits 429 Too Many Requests or 502 Bad Gateway when the provider is overloaded. Retry once after 60s. If persistent, mark as NOT_REVIEWED.
- **Claude Code stalls:** Claude Code can hang for 8+ minutes with no output (no `output_preview`). Kill after 5 min of no output. Do not wait indefinitely — this is a known provider-side stall.
- **Antigravity headless permissions:** In headless mode (`agy --print`), Antigravity auto-denies file reads and commands unless `--dangerously-skip-permissions` is set or explicit permission rules exist in `settings.json`. Even with the flag, it may return a help message instead of processing the prompt. **First attempt:** file-based context with `--print`. **Second attempt:** add `--dangerously-skip-permissions`. **Third attempt:** mark as `NOT_REVIEWED`.
- **OpenCode file reading stalls:** OpenCode can hang for >120s when reading large files (>20KB). If it exceeds timeout, kill and retry with **inline context** (first 100 lines of bundle via shell variable). If inline also fails, mark as `NOT_REVIEWED`.
- **Context bundle size:** Keep under 30KB for reliable CLI execution. If larger, extract only relevant sections (diff output, test results, not full source). Large bundles (60KB+) cause timeouts across all providers.
- **Hermes inline fallback (last resort):** When 2+ external CLIs fail (rate limits, stalls, permissions), do NOT leave edges as UNKNOWN — that produces a nearly useless report. Instead, Hermes covers ALL review lenses inline, clearly labeled as `"Hermes (inline)"` in the provider column. This preserves Rule 3's distinction: inline findings are explicitly attributed to Hermes, not presented as external provider evidence. Spawn CLI reviews with `notify_on_complete=true` in parallel; while they run, perform the full inline review across all lenses (security, quality/tests, architecture, etc.). Merge completed CLI results when they arrive. The Hermes inline review IS the report when no CLIs complete — never leave gaps. This is far better than marking 3/4 edges UNKNOWN.

## OpenSpec Alignment Review Pattern

For OpenSpec changes, use an 8-edge alignment matrix with security as a cross-cutting lens:

| Edge | What to Check |
|---|---|
| Spec ↔ Code | Requirements implemented, code matches specs |
| Code ↔ Docs | Code follows documented patterns |
| Docs ↔ Skills | Skills reference current commands/APIs |
| Skills ↔ Specs | Skill workflows match spec requirements |
| Spec ↔ Docs | Documentation covers spec requirements |
| Code ↔ Skills | Skills won't break with code changes |
| Spec ↔ Tests | All spec scenarios have test coverage |
| Code ↔ Tests | Implementation has test coverage |

**Security is a lens, not an edge.** Claude Code applies security checks across ALL edges. Putting it as a separate row causes it to disappear at one gate.

### Edge×Gate×Provider Ownership

Every edge must have a primary provider at both gates:

| Edge | Plan Review | Code Review |
|---|---|---|
| Spec ↔ Code | Hermes | Hermes |
| Code ↔ Docs | Codex | Codex |
| Docs ↔ Skills | Antigravity | Antigravity |
| Skills ↔ Specs | Kimi | Kimi |
| Spec ↔ Docs | Hermes | Hermes |
| Code ↔ Skills | Antigravity | Antigravity |
| Spec ↔ Tests | Codex | Codex |
| Code ↔ Tests | Codex | Codex |
| Security (all) | Claude Code | Claude Code |

**Provider/model identity note:** If the requested provider slot is Kimi Code, the executable is `kimi`; `fable-5` and `gd-Advance` are configured model labels/routes, not executable names. Verify with `command -v kimi` and `kimi --version`; never invent a `fable-5` binary. If a distinct CLI is actually installed, verify that executable separately. If the requested slot is unavailable, mark it `UNKNOWN` or `NOT_REVIEWED`. See `references/provider-identity-and-capture.md` for capture and substitution-disclosure rules.

**Default-model policy:** When the user requests the provider's default model, do not add a model-selection flag. When a model is explicitly requested, verify that the model label is registered for the selected provider before invoking it.

### Orchestrator Evidence Collection

Reviewers are read-only (by instruction). The orchestrator must collect evidence before spawning reviewers:

1. Read change artifacts via `openspec status --change <name> --json`
2. Read context files via `openspec instructions apply --change <name> --json` (requires `--change` flag)
3. Run tests: `uv run pytest --cov` (Python) or `make check-coverage` (Go)
4. Run lint: `uv run ruff check` (Python) or `gofmt` (Go)
5. Run `openspec validate --strict`
6. Bundle all output as string data
7. Validate no secrets in bundle
8. Spawn reviewers with string data only

### Status Semantics

| Status | Meaning |
|---|---|
| `PASS` | Evidence confirms alignment |
| `PARTIAL` | Some evidence, gaps remain |
| `FAIL` | Evidence shows misalignment |
| `N/A` | Edge not applicable |
| `UNKNOWN` | Could not verify |
| `NOT_REVIEWED` | Provider did not cover this edge |

**Never collapse UNKNOWN or NOT_REVIEWED into other statuses.** Include counts for ALL statuses in summaries.

### 3-Round Review Loop Pattern

Design-level issues converge in 2-3 rounds:

| Round | Focus |
|---|---|
| R1 | Proposal format, matrix shape, lens consistency, trust boundary concept |
| R2 | Security lens placement, test edges, evidence collection, status semantics |
| R3 | Edge ownership, provider assignments, review-scope template |

Implementation-level issues (exact commands, provider behavior) resolve during coding, not design review.

## Completion-Claim Integrity

**max_iterations tuning.** Complex review tasks (5+ lenses, multi-artifact evidence bundles) need generous iteration budgets. The default 80 iterations is often insufficient — reviewers exhaust their budget reading files before producing findings. Increase to 120+ for complex reviews via `delegation.max_iterations` in `~/.hermes/config.yaml`. Combined with inline context delivery, this dramatically improves reviewer success rates.

Provider reports and checked task boxes are claims, not completion evidence. Before reporting a change, phase, rollout, or cutover as complete:

1. **Bind evidence to the final revision.** Record the reviewed commit, rerun tests/lint/type checks after the last edit, and reject evidence from a stale revision.
2. **Require real effects for operational tasks.** A procedure document or JSON describing a future publish, rollout, rollback, or migration does not satisfy a task that requires the operation to occur. Mark it `BLOCKED`, `UNKNOWN`, or pending approval until real execution evidence exists.
3. **Verify integration, not only a worktree.** Confirm the implementation commit is reachable from the intended integration branch before deleting its worktree or feature branch. Never remove the only branch containing completed implementation.
4. **One writer per overlapping surface.** Do not dispatch multiple writers to the same worktree/files. Parallelize read-only reviews or disjoint repositories; serialize overlapping implementation and independently inspect every resulting diff.
5. **Do not launder blockers into passes.** A successful CLI exit with findings, a skipped prerequisite, or a docs-only rehearsal remains a finding/blocker unless the governing task explicitly defines it as acceptable.
6. **Reconcile task text with evidence.** Only check a task when its exact acceptance condition and verifier passed. Keep operator-controlled and consumer-owned tasks open until their owners actually provide the required evidence.
7. **Validate exact failure semantics.** A synthetic negative control must assert the expected exit code and expected report content, not merely “nonzero”; otherwise operational errors can false-pass as successful detection.
8. **Model hosting-platform lifecycle order.** New scheduled or manually dispatched workflows generally must exist on the default branch before they can provide default-branch run evidence. Add a required branch-protection context only after its stable job name has appeared and passed on the intended branch. Split baseline, merge/observation, enforcement, and protection changes into separately executable gates when one commit cannot satisfy the sequence.
9. **Require rollback evidence for mutable external state.** For branch protection, global skills, repository settings, or other non-repository state, record the before value/version, exact restoration operation, and a rehearsal or independently verifiable rollback check.

## Evidence Checklist

- [ ] Exact provider executable and version verified.
- [ ] Model/provider label distinguished from executable identity.
- [ ] All requested artifacts read.
- [ ] Reviewer prompts explicitly read-only and secret-safe.
- [ ] Real provider exit status captured.
- [ ] Saved output includes every requested change.
- [ ] Substitutions, timeouts, and unknowns disclosed.
- [ ] Worktree and output artifact independently verified.

See `references/provider-identity-and-capture.md` for the durable Kimi/fable-5 naming and capture pattern discovered during a real review.

See `references/read-only-product-scope-review-probes.md` for frozen-inventory counting, exact negative-control semantics, GitHub promotion ordering, scoped read-only verification, and credential-safe repository identity checks.

See `references/coding-agent-config-review-2026-08.md` for the reviewed CLI/model identity map, provider verdict semantics, OpenCode/Goose invocation quirks, Pi MCP overhead, and Hermes descriptor-exhaustion recovery.
