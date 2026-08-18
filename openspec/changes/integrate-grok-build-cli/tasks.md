# Tasks: Integrate Grok Build CLI

Every evidence file SHALL contain the command, native exit status, expected assertion, observed result, evidence class, and redaction status. Never print environment values, raw authorization headers, API keys, or complete request bodies.

## 1. Baseline and official-source lock

- [ ] 1.1 Capture pre-change user state without secrets.
  - Record presence, mode, and SHA-256 where applicable for `~/.grok/`, `~/.grok/config.toml`, `~/.zshrc`, `~/.bashrc`, and `~/.config/fish/config.fish`; record `command -v grok` and only presence/absence of the three credential variables.
  - Pass: no secret value appears; protected config hashes for `~/.tdt/config.yaml` and `~/.hermes/config.yaml` are recorded for later stability checks.
- [ ] 1.2 Re-fetch `https://x.ai/cli/stable`, `https://x.ai/cli/install.sh`, `https://docs.x.ai/build/overview`, and the relevant `xai-org/grok-build` source at a recorded commit.
  - Pass: stable confirmed at `1.0.3` (installed); official fields/commands used by this plan remain present. Otherwise stop and amend the change.
- [ ] 1.3 Record the current authenticated provider catalogs using metadata-only requests.
  - Pass: `fable-5`, `Advance`, `gpt-5.6-sol`, and `gpt-5.6-luna` are present; missing IDs fail closed before mutation.

## 2. Installer review and pinned installation

- [ ] 2.1 Review the downloaded installer and produce a touched-surface manifest.
  - Include binary/download paths, symlinks, completions, `~/.grok/config.toml`, and installer-delimited shell blocks.
  - Pass: no unexpected path, credential collection, or unrelated mutation is present.
- [ ] 2.2 Reconcile installed version `1.0.3` against the pinned plan version; record artifact URL, architecture, installed path, and executable SHA-256 for the 1.0.3 binary already present.
  - Use the official installer's version evidence and capture native installer status.
  - Pass: installed executable runs; artifact URL, architecture, installed path, and executable SHA-256 are retained. Verify an official checksum/signature if one is published; otherwise record the limitation.
- [ ] 2.3 Capture installed CLI interfaces from `grok --version`, `grok --help`, and help for every planned subcommand.
  - Pass: version is exactly `1.0.3`; later commands are used only when confirmed by installed help/source.
- [ ] 2.4 Compare pre/post user state and shell files.
  - Pass: every change matches the manifest and no protected surface changed.

## 3. Configuration transaction

- [ ] 3.1 Back up pre-existing Grok state with restrictive permissions.
  - Pass: backup path, mode, and hash are recorded; absence is recorded explicitly.
- [x] 3.2 Reconcile the live five-alias config (adds `cockpit-terra`) against the approved four aliases from `design.md`; decide keep or drop `cockpit-terra` and record the decision.
  - Pass: TOML parses; credential form matches the §3.5 remediation decision; unrelated pre-existing entries are preserved.
  - Decision: **keep `cockpit-terra`** — it is functional in the live config with upstream model `gpt-5.6-terra`, the default model, and was added during a prior grok upgrade. No plan reason to remove it.
- [ ] 3.3 Run installed native config inspection and model listing using confirmed commands.
  - Pass: all aliases resolve to the exact upstream IDs; no unknown/invalid-entry warning; no session credential is selected for custom endpoints.
- [x] 3.4 Scan configuration, process arguments, logs, and retained output for secret leakage.
  - Pass: zero `pmv_`/`agt_`/`sk-` matches in config.toml after migration. The sole remaining literal is `MCPR_TOKEN` (prefix `mcpr_`, len 37) in `[mcp_servers.mcp-router.env]` — accepted exception per §3.5 decision.
- [ ] 3.5 Credential-form remediation decision. Live config holds literal `api_key` values (shopapikey `pmv_…`, giaoduc `pmv_…`, cockpit `agt_…`) and a literal `MCPR_TOKEN`, contradicting the env-only claim. Decide and record one:
  - (a) migrate each provider to `env_key = "HERMES_CUSTOM_*_API_KEY"` and `MCPR_TOKEN` to `${VAR}` expansion (grok supports `env_key` and `${VAR}`; the vars are SET), then re-run 3.4's secret scan to zero; or
  - (b) formally accept literal keys and amend proposal/design to drop the "environment-only"/"no literal key" claims.
  Do not archive until this decision and its evidence are recorded.

## 4. URL and authentication shape probes

- [ ] 4.1 Observe shopapikey Responses metadata through a redacted local request observer.
  - Pass: final URL is exactly the intended `/v1/responses`; model ID is `fable-5`; authorization value is not retained.
- [ ] 4.2 Observe Giaoduc Messages metadata.
  - Pass: final URL is exactly the intended `/v1/messages`; model ID is `Advance`; accepted header name/scheme is recorded without value; no duplicate credential header is emitted.
- [ ] 4.3 Observe cockpit-sol Responses metadata.
  - Pass: final URL is the intended `/v1/responses`; model ID is `gpt-5.6-sol`.
- [ ] 4.4 Observe cockpit-luna Responses metadata.
  - Pass: final URL is the intended `/v1/responses`; model ID is `gpt-5.6-luna`.
- [ ] 4.5 Reconcile base URLs with observed joining behavior.
  - Pass: no missing `/v1`, duplicated `/v1/v1`, unexpected query parameter, or trailing-slash divergence. Any configuration adjustment is reflected in design evidence before inference.

## 5. Native bounded inference

- [ ] 5.1 Run `shopapikey-fable-5` with exact sentinel `SHOPAPIKEY_OK`.
- [ ] 5.2 Run `giaoduc-advance` with exact sentinel `GIAODUC_OK`.
- [ ] 5.3 Run `cockpit-sol` with exact sentinel `COCKPIT_SOL_OK`.
- [ ] 5.4 Run `cockpit-luna` with exact sentinel `COCKPIT_LUNA_OK`.
  - For 5.1–5.4: run serially, one turn, tools disabled, small output limit where supported, 60-second external timeout, structured output if supported, and configured default provider/model overrides only through the alias.
  - Pass: native exit 0, exact sentinel, intended alias/upstream ID, usage metadata when available, and no secret leakage.

## 6. Workspace instruction and skill discovery

- [ ] 6.1 Create a disposable git worktree under `~/Developer/` with synthetic content and no credentials.
  - Pass: worktree and cleanup commands are retained; original repo status is unchanged.
- [ ] 6.2 Run native Grok inspection in the disposable worktree.
  - Pass: intended workspace/repository `AGENTS.md` sources and canonical shared Agent Skills are identified from native output; unsupported discovery is recorded honestly.
- [ ] 6.3 Confirm Grok did not create a competing maintained skill tree or modify source.
  - Pass: only documented user runtime state changes; outside-root and protected-surface checks remain clean.

## 7. MCP and ACP

- [ ] 7.1 Determine the exact installed Grok MCP configuration/list/doctor interfaces from help/source.
  - Pass: commands and config keys are retained; unsupported assumptions are removed.
- [ ] 7.2 Configure only the existing mcp-router aggregate bridge if Grok supports it.
  - Pass: no downstream server is registered directly; before/after MCP inventory proves the sole allowed addition.
- [ ] 7.3 Run a read-only mcp-router canary.
  - Pass: a harmless list/schema/health-style call returns through the aggregate route with no memory write or external mutation.
- [ ] 7.4 Verify ACP with the exact installed interface.
  - Pass: bounded stdio handshake succeeds, or the capability is marked `UNSUPPORTED` with native evidence and removed from completion claims.

## 8. Agent isolation and concurrency

- [ ] 8.1 Run one bounded read-only repository explanation in the disposable worktree.
  - Pass: no file change and clean exit.
- [ ] 8.2 Run one synthetic edit/test operation only if the installed permission model can confine writes to the disposable worktree.
  - Pass: expected synthetic diff/test result, zero outside-root changes, then remove the worktree.
- [ ] 8.3 Run a non-mutating concurrency smoke with one existing agent and Grok.
  - Pass: no config corruption, lock conflict, or cockpit port conflict. This does not add Grok to mandatory orchestration.

## 9. Rollback rehearsal and retained state

- [ ] 9.1 Rehearse the complete install/config/rollback transaction in an isolated temporary HOME.
  - Pass: the pre-state is restored by hash/mode and only manifest-owned files are removed.
- [ ] 9.2 Execute and verify rollback against user state after native tests.
  - Pass: exact backup restore or targeted block removal, shell block removal, binary/symlink/completion cleanup, PATH check, protected-surface hash stability, and no added aliases.
- [ ] 9.3 Reapply the approved integration if Grok is to remain installed.
  - Pass: repeat native config/provider smoke evidence without reintroducing unrelated changes.

## 10. Review, validation, and closure

- [x] 10.1 Run three native CLI plan reviews, maximum three concurrently.
  - Evidence: Claude Code 2.1.226, Codex 0.147.0, and Pi 0.84.1 completed substantive reviews; findings are reconciled in `review-findings.md`.
- [ ] 10.2 Re-run final review after implementation evidence is added.
  - Pass: no unresolved BLOCKER/MAJOR finding for the implemented slice.
- [ ] 10.3 Run `openspec validate integrate-grok-build-cli --store openspec-store`, `openspec validate --all --store openspec-store`, `git diff --check`, and intended-status checks.
  - Pass: focused change valid; full-store failures, if any, are classified; obsolete `integrate-fable-5` path absent; unrelated `ecosystem-standardization/` work remains untouched.
- [ ] 10.4 Commit only this change and sanitized review/evidence artifacts with a corrective conventional subject.
  - Pass: clean intended status and verified commit contents. Do not archive until implementation and rollback gates pass.
