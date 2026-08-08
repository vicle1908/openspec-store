# Multi-CLI Review Report

## Scope

Review target: `optimize-coding-agent-configuration` proposal, design, and tasks. Review date: 2026-08-08. All review agents were instructed to remain read-only and not expose credentials.

## Dispatch Results

| CLI agent | Version | Result |
|---|---:|---|
| Claude Code | 2.1.220 | No usable verdict; provider returned a connectivity error after a completed-looking session envelope.
| agy | 1.1.11 | No verdict; JSON status reported timeout after loading a very large context.
| OpenCode | 1.18.15 | First run rejected `/tmp` as an external directory; in-repository retry consumed its full bound without a verdict.
| Pi | 0.84.1 | Timed out with no review output; its full environment is known to register 77 direct MCP tools.
| Codex | 0.147.0 | Timed out while traversing workspace guidance; no final review artifact was produced.
| Kimi Code | 0.34.0 | **MODIFY**; substantive findings returned.
| Goose | 1.45.0 | **MODIFY**; substantive findings returned.

A timeout or provider failure is recorded as inconclusive, never as approval.

## Kimi Code Findings

Kimi correctly identified the following required corrections:

1. Do not set Claude timeout variables to zero without verified release semantics.
2. Do not remove `ECC_DISABLED_HOOKS`; that would re-enable suppressed hooks.
3. Correct the Codex path to `~/.codex/config.toml`.
4. Correct the Kimi Code path to `~/.kimi-code/config.toml`.
5. Keep five retries for maximum transient-failure resilience.
6. Validate Pi compaction values against the actual context budget.
## Goose Findings

Goose independently returned **MODIFY** and agreed that:

1. Unlimited Claude/MCP timeouts can hang indefinitely; use generous finite values.
2. Removing plugin-disabled hooks is not equivalent to removing hooks and must not be done blindly.
3. OpenCode wildcard permission may be valid, but external-directory path mapping must be schema-checked.
4. Pi context reserves should be increased only after measuring context behavior.
5. Reducing Kimi retries conflicts with the maximum-capability objective.
6. Global Codex `approval_policy = "never"` is valid for an authorized unrestricted environment but should be explicitly verified.

## Official Documentation Cross-Checks

- Claude Code permissions document `Read(...)` and `Edit(...)` path rules; `Edit` covers built-in file-editing tools. `Write(...)` is not the file-edit permission surface.
- OpenCode official permissions documentation documents wildcard permissions, `doom_loop`, and `external_directory`; Kimi’s claim that these keys are categorically invalid is rejected.
- The revised design preserves `doom_loop: ask` as an operational exception while keeping ordinary tool permissions fully allowed.

## Gate Decision

**Current verdict: MODIFY before implementation.** The original change must not be applied. The revised proposal/design/tasks incorporate the two substantive reviews and the official documentation cross-checks. Implementation remains blocked until the revised change receives final validation.
## Post-Restart Cleanup Verification

After the user restarted the environment:

- Hermes shell soft FD limit: `256`; hard limit: `unlimited`.
- Current shell open FDs: `7`; system FDs: `23287`.
- No Hermes-managed background processes remained.
- No Hermes sandbox directories remained.
- Review-specific temporary files were removed from `/tmp`.
- Three pre-existing `<defunct>` processes remain (PIDs 39096, 31583, 31584); none are from this review session.
- The remaining Pi, Goose desktop daemon, and ChatGPT/Codex app-server processes are expected user-launched processes.

## Current Config Baseline

- Claude: `bypassPermissions`, finite `3000000/800000/800000ms` timeouts, `ECC_DISABLED_HOOKS` present.
- OpenCode: `edit/bash/webfetch=allow`; no `doom_loop` or `external_directory` yet.
- Pi: compaction `16384/20000`; MCP config present; 77 direct tools observed in the full environment.
- Codex: `danger-full-access`; no `approval_policy` yet.
- Kimi Code: `default_plan_mode=false`, five attempts, 50000 reserved context, 100000ms MCP timeout.

The change remains a proposal only; no agent configuration was mutated during cleanup.

## Concurrency Incident

All 7 CLI review agents were dispatched in parallel via `terminal(background=true)`. This bypassed Hermes delegation concurrency limits and caused an `Errno 24` (too many open files) error on subsequent tool calls within the same session.

**Root cause:** Each CLI agent spawns a process tree that opens file descriptors for the CLI binary, provider connections, MCP bridges, plugins, and file handles. With the shell soft FD limit at 256, 6+ parallel agents exhausted the available FDs.

**Fix applied:** Updated `openspec-review-governance` skill with a 3-agent-batch dispatch pattern:

- **Batch 1** (3 parallel): Claude Code, agy, Goose
- **Batch 2** (3 parallel): OpenCode, Codex, Advance Code
- **Batch 3** (serial): Pi (77 MCP tools, heavy startup, timeout risk)

Pi always runs last in isolation due to its 77 direct MCP tool registrations causing startup delays and FD pressure.

**Lesson:** Never dispatch more than 3 CLI review agents concurrently. Use `process(action='wait')` between batches. Record timeouts as inconclusive, never as approval.
