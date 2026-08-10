# Review Findings

## Scope

- Change: `prime-agent-three-provider-integration`
- Prime Agent stable revision: `v0.7.1` / `95afd319a78ae017a41241d50b013d656a0685ce`
- Audited newer source revision: `a18809e00ea30638584d87b3afea7285a9d7296c`
- Review date: 2026-08-09
- Live installation performed: No
- `~/.prime/agent` modified: No
- Paid Prime Agent inference performed: No
- Protected Hermes/TDT configuration modified: No

## Reviewer Results

### Claude Code 2.1.226 — provider/source lens

- Native status: completed provider/source inspection but reached `max_turns` before emitting the contracted final report; operational lens is `PARTIAL`, not counted as approval.
- Finding `CLAUDE-01` (`REQUIRED`): Anthropic request `max_tokens` may default below the catalog `maxTokens` value when no explicit run option is supplied. The design must not present `32000` as proven request behavior.
  - Evidence: reviewer inspection of `packages/ai/src/providers/anthropic.ts`; reviewer transcript ended while checking this exact source section.
  - Disposition: fixed in `design.md` under **Output-token semantics** and gated by `STREAM-01`.
- Finding `CLAUDE-02` (`REQUIRED`): execution tasks needed stable IDs, commands, and retained evidence paths.
  - Disposition: fixed by the rewritten `tasks.md`.

### Antigravity 1.1.11 — execution-readiness lens

- Native status: `SUCCESS`, one-turn substantive review.
- Verdict: `APPROVE_WITH_REQUIRED_REVISIONS`.
- Finding `AGY-01` (`REQUIRED`): stable gate IDs, command shapes, and evidence paths were missing.
  - Disposition: fixed in `tasks.md`; all gates now have stable IDs and `evidence/<gate-id>/` locations.
- Finding `AGY-02` (`REQUIRED`): Giaoduc `X-Api-Key` versus Bearer behavior required a pre-inference decision gate.
  - Disposition: fixed in `design.md` and `WIRE-MSG-01`.
- Finding `AGY-03` (`REQUIRED`): standard Responses failure needed an explicit stop/amend/re-review path before Codex testing.
  - Disposition: fixed by the failure-classification table and `WIRE-RESP-01/02`.
- Finding `AGY-04` (`ADVISORY`): checked research tasks lacked durable retained evidence.
  - Disposition: fixed by `evidence/research/baseline.md` and retained installer bytes.
- Finding `AGY-05` (`ADVISORY`): proposal should explain `skip_specs: true`.
  - Disposition: fixed in `proposal.md` under **Spec Impact**.

### Pi 0.84.1 — governance/security lens

- Native status: exit 0 with a substantive final report.
- Verdict: `APPROVE_WITH_REQUIRED_REVISIONS`.
- Finding `PI-01` (`REQUIRED`): stable gate IDs, exact commands, expected outcomes, and evidence paths were missing.
  - Disposition: fixed in `tasks.md`.
- Finding `PI-02` (`REQUIRED`): protocol failure classification and amendment/re-review rules were underspecified.
  - Disposition: fixed in `design.md`.
- Finding `PI-03` (`REQUIRED`): Giaoduc Bearer-only risk needed an enforceable fallback/abort decision.
  - Disposition: fixed in `WIRE-MSG-01`; source modification remains outside this change.
- Finding `PI-04` (`ADVISORY`): retained evidence needed for checked research tasks.
  - Disposition: fixed in `evidence/research/`.
- Finding `PI-05` (`REQUIRED`): exact installer provenance and verification were missing.
  - Disposition: installer bytes retained as `evidence/research/install.sh`, captured digest recorded, and `INSTALL-02` requires re-fetch comparison and re-review on change. The digest is explicitly not treated as an upstream signature.
- Finding `PI-06` (`REQUIRED`): rollback scope and touched-surface manifest were underspecified.
  - Disposition: fixed in `INSTALL-01`, `ROLLBACK-01`, and `LIVE-01`.
- Finding `PI-07` (`REQUIRED`): same-user execution/secret-state risks needed enforceable controls.
  - Disposition: fixed by `SECRET-01`, minimal child-environment requirements, isolated state, and protected-surface checks. The suggested broad grep/chmod approach was narrowed to avoid leaking secret matches or assuming ownership.

### Codex 0.147.0 — attempted lens

- Native process started against the correct fixture and read the artifacts/source, but did not produce a final result or final-message file before lifecycle termination.
- Disposition: `NOT_REVIEWED`; no approval claimed. Its partial diagnostic notes were not used as completion evidence.

### Kimi 0.34.0 and OpenCode 1.18.15 — attempted lenses

- Kimi attempted a file read but produced no substantive final report.
- OpenCode's read was denied by its effective external-directory permission policy and produced no substantive report.
- Disposition: `NOT_REVIEWED`; no approval claimed.

## Consolidated Traceability

| Gate | Requirement | Command/probe shape | Expected evidence | Failure action |
|---|---|---|---|---|
| `INSTALL-02` | Reviewed installer identity | SHA-256 of retained/re-fetched installer | matching reviewed bytes and source URL | stop, inspect, amend, re-review |
| `CONFIG-02` | Registry loads | isolated `prime-agent model list` | intended aliases only | stop, repair configuration |
| `WIRE-RESP-01/02` | Standard Responses contract | redacted native metadata probe | `/v1/responses`, model, auth scheme | classify, stop, amend/re-review |
| `WIRE-MSG-01` | Messages/auth contract | direct compatibility plus native metadata | `/v1/messages`, accepted auth/version/stream | stop; amend/defer/adapter change |
| `INFER-01` | Native text inference | isolated exact-sentinel run | exit 0, sentinel, usage, terminal event | provider fails acceptance |
| `STREAM-01` | Stream/reasoning/usage | native stream plus deterministic regressions | no dropped events; observed effective limits | no rollout/source-fix change |
| `TOOL-01` | Tool round trip | disposable worktree marker | externally verified marker/diff | no rollout |
| `SECRET-01` | Credential isolation | internal exact-value/pattern controls | zero leaks, minimal child env | remove evidence/config and stop |
| `ROLLBACK-01` | Exact restoration | isolated HOME apply/restore | zero unexpected metadata/hash differences | no live apply |
| `LIVE-01` | Live transaction | approved preflight/backup/publish/canary | success or automatic rollback | rollback and stop |

## Required Revisions

- [x] Add durable baseline and installer evidence.
- [x] Add stable gate IDs, command/probe shapes, pass criteria, and evidence locations.
- [x] Add explicit standard Responses versus Codex stop/amend/re-review decision.
- [x] Add Giaoduc authentication compatibility and fail-closed decision.
- [x] Add effective output-token semantics rather than equating catalog metadata with request behavior.
- [x] Add isolated touched-surface, secret-boundary, rollback, and live-transaction gates.
- [x] Explain `skip_specs: true` and separate static readiness from operator apply authorization.
- [ ] Receive explicit operator approval (`APPLY-GO`) before installation, live configuration, or provider inference.

## Final Static Re-review

Pi 0.84.1 performed a bounded no-tools/no-extensions re-review of the updated proposal, design, tasks, findings, and retained summaries. Native exit was 0. Verdict: **Static Ready for Apply**. The reviewer confirmed that all prior REQUIRED planning findings were resolved and that `APPLY-GO` correctly remains an unchecked operator-authorization gate.

The final reviewer also confirmed that archival is premature: installation, configuration, native provider acceptance, security checks, rollback/reapply, and final implementation review remain incomplete.

## Readiness Decision

- [x] Ready for apply — static planning/review gates pass; live apply still requires explicit operator approval.
- [ ] Ready only after required planning revisions.
- [ ] Not ready.

This change is not ready to archive. Execution, native acceptance, security verification, rollback/reapply, final review, and closure tasks remain intentionally incomplete.
