# CLI Review Findings: integrate-grok-build-cli

**Review date:** 2026-08-09
**Scope:** OpenSpec plan artifacts only; no Grok installation or user-runtime mutation.
**Reviewers:** Claude Code 2.1.226, Codex CLI 0.147.0, Pi 0.84.1.
**Execution:** Native CLI processes, one parallel batch of three, fixture passed inline, tools disabled/read-only, native exit status captured. All three exited 0 with substantive output.

## Consolidated Verdict

The originally committed `integrate-fable-5` plan was **BLOCKED**. Structural OpenSpec validation had passed, but semantic review found incorrect official identity, executable and config paths, corrupted source names/URLs, wrong cockpit mappings, ambiguous aliases, unsupported completion claims, weak tasks, insufficient secret controls, unresolved URL joining/authentication, and an untestable rollback.

The plan has been corrected and renamed `integrate-grok-build-cli`. Runtime claims remain gated because Grok is not installed.

## Finding Disposition

| ID | Severity | Finding | Reviewers | Disposition |
|---|---|---|---|---|
| R1 | BLOCKER | Wrong product/binary/config identity (`fable-5`, `~/.fable-5`) | Claude, Codex, Pi | **Accepted/fixed:** Grok Build, `grok`, `~/.grok/config.toml` restored everywhere. |
| R2 | BLOCKER | Corrupted xAI names and official URLs | Codex, Pi; manual audit | **Accepted/fixed:** `xAI`, `xai-org/grok-build`, `docs.x.ai`, and `x.ai` restored. |
| R3 | BLOCKER | Cockpit aliases incorrectly mapped to `fable-5` and duplicated | All | **Accepted/fixed:** exact IDs `gpt-5.6-sol` and `gpt-5.6-luna`; four unique aliases used consistently. |
| R4 | BLOCKER | Tasks invoked nonexistent `fable-5` CLI and assumed unverified subcommands | All | **Accepted/fixed:** tasks use `grok`; installed help/source must confirm each interface before use; unsupported capabilities are classified honestly. |
| R5 | MAJOR | Direct HTTP probes were too close to Grok acceptance claims | Codex | **Accepted/fixed:** evidence classes split into official-source, direct compatibility, and native Grok acceptance. |
| R6 | MAJOR | URL joining for root and `/v1` base URLs unresolved | Codex | **Accepted/fixed:** explicit redacted URL-shape gates reject missing/duplicated `/v1`. |
| R7 | MAJOR | Giaoduc auth unresolved and header evidence could leak secrets | Codex, Pi | **Accepted/fixed:** metadata-only native observation, no values, no duplicate credential headers, fail closed. |
| R8 | MAJOR | Installer called pinned without an exact version/integrity plan | Codex, Pi | **Accepted/fixed:** explicit 1.0.0 positional install, installer review, artifact URL/hash, official checksum when available; absence recorded rather than fabricated. |
| R9 | MAJOR | Tasks lacked commands, assertions, evidence classes, and fail conditions | Claude | **Accepted/fixed:** tasks expanded into executable, evidence-bound gates. Exact post-install syntax remains conditional on installed help. |
| R10 | MAJOR | Rollback was undefined/dry-run only | All | **Accepted/fixed:** touched-surface manifest, isolated-HOME rehearsal, exact restore/removal and protected-hash checks. |
| R11 | MAJOR | User-level mutation versus workspace scope unclear | Codex | **Accepted/fixed:** ownership boundaries and protected surfaces named explicitly. |
| R12 | MAJOR | Secret presence, process arguments, logs, and evidence not scanned | Claude, Pi | **Accepted/fixed:** presence-only preflight and secret-shape scans are mandatory. |
| R13 | MAJOR | Disposable worktree isolation and cleanup underspecified | Pi | **Accepted/fixed:** synthetic worktree under `~/Developer`, outside-root verification, cleanup required. |
| R14 | MAJOR | Headless probes lacked time/output bounds | Pi | **Accepted/fixed:** serial one-turn, no-tools, small output, external 60-second timeout. |
| R15 | MINOR | MCP canary and concurrency behavior vague | Pi | **Accepted/fixed:** mcp-router-only harmless canary and bounded non-mutating concurrency smoke. |
| R16 | BLOCKER | `skip_specs: true` should be removed | Claude only | **Rejected:** this is intentionally a user-level tooling/config integration with no product capability delta. Workspace OpenSpec policy explicitly requires `skip_specs: true` for this class. Focused validation must still pass. |
| R17 | MAJOR | Running inspection in `agent-core` violates out-of-scope boundary | Claude | **Partially rejected/fixed:** read-only inspection in a repository does not change `agent-core`, but the corrected plan uses a disposable worktree to remove ambiguity and mutation risk. |
| R18 | MINOR | Duplicate acceptance statements could drift | Claude | **Accepted/fixed:** proposal delegates completion governance to design/tasks; design contains the authoritative matrix. |

## Reviewer Reliability Notes

- The first attempted file-path reviews were invalid: Claude could not read the fixture with tools disabled, Codex correctly returned BLOCKED for missing fixture content, and OpenCode hung. Those attempts are not counted as reviews.
- The valid review batch embedded the sanitized fixture directly. Claude, Codex, and Pi each returned substantive findings with native status 0.
- Some Claude/Pi wording repeated the corrupted names while describing the correction. Dispositions follow the independent verified facts in the fixture, not those typographical slips.

## Re-review Gate

After installation/configuration evidence is added, rerun three native CLI reviews. Approval requires no unresolved BLOCKER or MAJOR finding for the implemented slice. This plan must not be archived before native Grok inference and rollback gates pass.
