# Tasks: Prime Agent Three-Provider Integration

All apply tasks remain approval-gated. Static readiness does not authorize installation, live configuration, or provider inference. Evidence SHALL be sanitized and retained under `evidence/<gate-id>/` with command, revision/version, native exit status, expected assertion, observed result, evidence class, and redaction status.

## 1. Planning, review, and durable baseline

- [x] 1.1 `PLAN-01` Create proposal, design, executable tasks, and canonical `skip_specs: true` configuration.
  - Evidence: `.openspec.yaml`, `proposal.md`, `design.md`, and `tasks.md` in this change.
- [x] 1.2 `PLAN-02` Pin the evaluated Prime Agent stable release and retain source identity.
  - Commands: `git -C /Users/androidteam/Developer/prime-agent rev-parse v0.7.1^{}` and `git -C /Users/androidteam/Developer/prime-agent rev-parse HEAD`.
  - Pass: stable commit is `95afd319a78ae017a41241d50b013d656a0685ce`; current HEAD is separately identified.
  - Evidence: `evidence/research/baseline.md`.
- [x] 1.3 `PLAN-03` Record gateways, endpoint references, model IDs, protocol assumptions, and credential-variable names without values.
  - Pass: three credentials are presence-only; catalogs return HTTP 200 JSON; `/models` is classified as discovery only.
  - Evidence: `evidence/research/baseline.md`.
- [x] 1.4 `PLAN-04` Record static source validation and dependency-audit limitations.
  - Commands: `npm ci`, `npm run check`, and production-only `npm audit --omit=dev --audit-level=high` against the recorded checkout.
  - Pass: install/check native status recorded; audit findings retained as risk, not blindly repaired.
  - Evidence: `evidence/research/baseline.md`.
- [x] 1.5 `PLAN-05` Run independent CLI-agent reviews and reconcile required findings.
  - Reviewers: Claude Code 2.1.226, Antigravity 1.1.11, Pi 0.84.1; Codex 0.147.0 and Kimi 0.34.0 attempts are recorded as incomplete/non-substantive and are not counted as approvals.
  - Pass: required findings have dispositions and no unresolved planning blocker remains.
  - Evidence: `review-findings.md` and `evidence/reviews/review-summary.md`.
- [x] 1.6 `APPLY-GO` Obtain explicit operator approval for live apply.
  - Pass: operator provides an explicit instruction to execute this change after reviewing the final artifacts.
  - Failure action: stop; static readiness alone is not authorization.

## 2. Installation and isolation

- [x] 2.1 `INSTALL-01` Capture the pre-install touched-surface manifest.
  - Inspect with `lstat` semantics: Prime Agent binary resolution, `~/.prime/agent`, auth/models/settings/session/log/kernel state, daemon socket/worker state, relevant shell startup files, and protected Hermes/TDT configs.
  - Retain existence, type, current-user ownership, mode, hash, and symlink target; never retain credential values.
  - Evidence: `evidence/INSTALL-01/pre-state.md`.
- [x] 2.2 `INSTALL-02` Verify the retained official installer.
  - Command: `shasum -a 256 evidence/research/install.sh`.
  - Expected reviewed digest: `38d14a1be73b325652c7ce8342e3bf19335721837192855a7907732caf8e6d04` for the retained bytes fetched on 2026-08-09.
  - Re-fetch before apply; if bytes or stable channel changed, stop, inspect, update the digest/design, and re-review before execution.
  - Evidence: `evidence/INSTALL-02/installer-provenance.md`.
- [x] 2.3 `INSTALL-03` Rehearse pinned installation in an isolated temporary HOME with a minimal environment.
  - Preconditions: Node.js `>=22.8.0`; reviewed installer bytes/digest; fixed version `0.7.1`; explicit HOME/PATH/temp/session/daemon paths; unrelated credentials and proxy controls excluded.
  - Pass: version, installed path, binary hash, touched paths, and installer status match the manifest.
  - Evidence: `evidence/INSTALL-03/`.
- [x] 2.4 `INSTALL-04` Install or select the approved stable runtime for live apply.
  - Use the exact retained/reviewed installation method; do not use moving `npm update -g prime-agent`.
  - Pass: `prime-agent --version` reports `0.7.1`; `prime-agent --help`, `prime-agent status --json`, and `prime-agent doctor --json` complete without `--fix`.
  - Evidence: `evidence/INSTALL-04/`.
- [x] 2.5 `ISOLATE-01` Create isolated config, session, kernel, and daemon boundaries for acceptance.
  - Confirm exact variable/flag names from installed `--help` and pinned source before running.
  - Pass: explicit agent/session directories and daemon socket are in the isolated root; no real user session/auth/log state is touched.
  - Evidence: `evidence/ISOLATE-01/`.

## 3. Credential-free provider configuration

- [x] 3.1 `CONFIG-01` Materialize the reviewed credential-free `models.json` template in the isolated agent directory.
  - Pass: JSON parses; provider/model entries match `design.md`; file/directory modes are restrictive; no literal credential exists.
  - Evidence: `evidence/CONFIG-01/`.
- [x] 3.2 `CONFIG-02` Verify model registry loading.
  - Command shape: `PRIME_AGENT_CODING_AGENT_DIR=<isolated-agent-dir> prime-agent model list`.
  - Pass: exactly the approved aliases appear and no unintended provider is available to acceptance runs.
  - Evidence: `evidence/CONFIG-02/model-list.txt`.
- [x] 3.3 `SECRET-01` Verify credential isolation before provider calls.
  - Launch through a minimal child-environment allowlist containing only named runtime/locale variables and the one provider credential needed by that probe.
  - Scan tracked/retained evidence, process arguments, config, sessions, and logs for exact secret values internally plus secret-pattern categories; report names/categories/counts only.
  - Pass: no value leak, no unrelated ambient credential reaches the child, and all positive/negative scanner controls behave as expected.
  - Evidence: `evidence/SECRET-01/`.

## 4. Protocol decision gates

- [x] 4.1 `WIRE-RESP-01` Observe standard Responses metadata for `shopapikey/fable-5` through Prime Agent.
  - Retain only method, final path, model ID, status, content type, header names/schemes, and response-event types; discard values and bodies.
  - Pass: intended `/v1/responses` behavior and standard Bearer authentication.
  - Failure action: classify per `design.md`; stop for amendment/re-review before trying Codex or an adapter.
  - Evidence: `evidence/WIRE-RESP-01/`.
- [x] 4.2 `WIRE-RESP-02` Observe standard Responses metadata for all retained cockpit models.
  - Same pass/failure rules as `WIRE-RESP-01`.
  - Evidence: `evidence/WIRE-RESP-02/`.
- [x] 4.3 `WIRE-MSG-01` Verify Giaoduc Messages path and authentication.
  - First perform direct compatibility probes without retaining values: `/v1/messages` with `X-Api-Key` plus required version header, and separately Bearer if needed.
  - Then observe Prime Agent's native request metadata.
  - Pass: native request uses an authentication form the gateway accepts, correct version header, intended model, and compatible streaming format.
  - Failure action: if native `X-Api-Key` fails but Bearer succeeds, stop and amend/re-review; do not silently add `authHeader` or source changes. If neither succeeds, remove/defer Giaoduc or create a separate provider-adapter change.
  - Evidence: `evidence/WIRE-MSG-01/`.

## 5. Native provider acceptance

- [x] 5.1 `INFER-01` Run isolated no-tool exact-sentinel probes for every retained alias.
  - Confirm exact installed flags before use; expected shape is `prime-agent --provider <provider> --model <id> --no-session --no-tools --no-skills --no-extensions --mode json -p <sentinel>`.
  - Run serially with an external timeout and minimal child environment.
  - Pass: native exit 0, exact sentinel, intended alias/upstream ID, nonzero usage, clean terminal event, no embedded provider error, and no secret leakage.
  - Evidence: `evidence/INFER-01/<provider-model>/`.
- [x] 5.2 `STREAM-01` Verify text, terminal, reasoning, and usage events.
  - Include explicit regressions for open issue #995 and effective output-limit behavior from #755.
  - Pass: no dropped terminal/text event, reasoning separated from visible text, nonnegative usage, and actual effective limit recorded rather than inferred from config.
  - Evidence: `evidence/STREAM-01/`.
- [x] 5.3 `TOOL-01` Verify tool-call argument reconstruction and tool-result replay in a disposable worktree.
  - Pass: exact marker artifact verified externally, clean process exit, expected diff only, and zero outside-root mutation.
  - Evidence: `evidence/TOOL-01/`.
- [x] 5.4 `ERROR-01` Verify invalid auth, unsupported model, timeout, rate limit, malformed stream, interruption, and context overflow.
  - Use deterministic local fixtures where a real gateway condition cannot be safely induced.
  - Pass: each failure is structured, non-successful, redacted, and does not corrupt config/session state.
  - Evidence: `evidence/ERROR-01/`.
- [x] 5.5 `HANDOFF-01` Verify at least one cross-provider session handoff.
  - Pass: prior text/tool history is converted without transcript corruption or secret propagation.
  - Evidence: `evidence/HANDOFF-01/`.

## 6. Workspace and optional interfaces

- [x] 6.1 `WORKSPACE-01` Inspect and verify context/resources in a trusted disposable worktree.
  - Confirm `AGENTS.md`, `CLAUDE.md`, project `.prime/agent` resources, packages, extensions, and canonical shared skills before startup.
  - Pass: intended instructions/skills discovered, no duplicate maintained skill tree, no unexpected package install, and original repository status unchanged.
  - Evidence: `evidence/WORKSPACE-01/`.
- [x] 6.2 `MCP-01` Verify only the existing mcp-router aggregate route if supported.
  - Pass: no downstream MCP duplication and one read-only list/schema/health canary with no persistence or external mutation.
  - Evidence: `evidence/MCP-01/`.
- [x] 6.3 `ACP-01` Verify ACP from installed help/source if supported.
  - Pass: bounded stdio handshake, or explicit `UNSUPPORTED` disposition removed from completion claims.
  - Evidence: `evidence/ACP-01/`.

## 7. Rollback, review, and closure

- [x] 7.1 `ROLLBACK-01` Rehearse complete install/config/rollback in isolated HOME.
  - Restore every manifest-owned surface byte-for-byte or remove only proven change-owned additions; verify owner/mode/hash/symlink identity and no protected-surface delta.
  - Pass: zero unexpected post-rollback differences.
  - Evidence: `evidence/ROLLBACK-01/`.
- [x] 7.2 `LIVE-01` Apply to real user state only after `APPLY-GO` and isolated gates pass.
  - Transaction: all-target preflight, restrictive backup, atomic config publication, native canaries, and automatic rollback on any failure before completion.
  - Evidence: `evidence/LIVE-01/`.
- [x] 7.3 `REAPPLY-01` Verify rollback and reapply if Prime Agent is to remain installed.
  - Pass: final version/binary/config identities, protected surfaces, and provider canaries match approved evidence.
  - Evidence: `evidence/REAPPLY-01/`.
- [x] 7.4 `FINAL-REVIEW` Run final native CLI reviews against implemented evidence and disposition every finding.
  - Pass: no unresolved BLOCKER/REQUIRED finding for the implemented slice.
  - Evidence: `evidence/FINAL-REVIEW/`.
- [x] 7.5 `CLOSE-01` Run focused/full OpenSpec validation, `git diff --check`, secret scan, staged-byte verification, and scoped commit.
  - Preserve unrelated `ecosystem-standardization/` work.
  - Archive only after all required tasks are complete and live/rollback evidence is honest.

## Evidence rule

Discovery, source inspection, model listing, and direct HTTP compatibility are lower evidence classes. None satisfies native inference, stream, tool, error, workspace, security, live transaction, or rollback gates.
