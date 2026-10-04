# Tasks

## 1. Measure Version Authority Per Tool

- [ ] 1.1 Implement self-update capability detection that records whether each declared agent CLI exposes an update or upgrade verb; verify it reports `claude`, `codex`, `Claude-Fable`, `opencode`, and `cursor-agent` as self-updating and `droid` as not self-updating
- [ ] 1.2 Implement package-asset version-deferral detection that records whether an installing asset declares it defers version control, keying on `auto_updates` for casks and on formula kind for formulae; verify it reports cask `claude` and cask `droid` as deferring and cask `codex` and cask `Claude-Fable` as not deferring
- [ ] 1.3 Implement the measured version-authority matrix combining both signals; verify it reports `claude` and `droid` as no-drift, and `codex`, `Claude-Fable`, and `opencode` as drift
- [ ] 1.4 Implement `unknown` recording with evidence gaps for a tool whose self-update capability or asset deferral cannot be determined; verify an undeterminable tool is reported unknown and not reconciled
- [ ] 1.5 Document the two signals, the deferral semantics, and the matrix in `docs/` and verify the documented commands reproduce the measured matrix

## 2. Drift Reporting

- [ ] 2.1 Implement version-authority drift detection that reports a self-updating tool whose installing asset pins version, naming both the self-update verb and the pinning manager; verify it reports `codex`, `Claude-Fable`, and `opencode` and reports nothing for `claude` and `droid`
- [ ] 2.2 Record the consequence in each drift finding, that a package-manager upgrade reverts the self-updated version; verify the finding text states the reversion consequence
- [ ] 2.3 Verify drift is reported as a distinct finding class and never as an undeclared-coverage finding or an update failure; verify a run with drift present reports drift and not coverage or failure findings for those CLIs
- [ ] 2.4 Verify a self-updating tool whose asset defers version produces no drift finding; verify `claude` and `droid` produce no drift finding
- [x] 2.5 Implement measurement-failure reporting as a DEGRADED finding with its own flag, separate from the content flag; verify a reporter crash sets the measurement-failure flag and does not set the content flag, so the summary never claims a breach that was not measured
- [ ] 2.6 Document the drift finding, the measurement-failure distinction, and their separation from coverage and failure findings in `docs/` and verify the documented example matches a real run

## 3. Declared Update Verb Follows the Version Authority

- [ ] 3.1 Implement declaration validation that flags a covered CLI whose declared update verb belongs to a manager that does not own its version; verify it flags a declaration pointing `codex` at the installing package manager's upgrade path
- [ ] 3.2 Report the self-update verb a flagged declaration should use instead; verify the report names `codex update` for `codex`
- [ ] 3.3 Update the declared covered set so each entry's update verb matches its version authority; verify a subsequent run reports no inconsistent declarations
- [ ] 3.4 Verify the runner never applies a pinning manager's upgrade path to a self-updating CLI; verify no package-manager upgrade verb is invoked for `codex`, `Claude-Fable`, or `opencode` during a run
- [ ] 3.5 Document the version-authority-to-update-verb mapping and how to declare an entry in `docs/` and verify the documented procedure yields no inconsistent declarations

## 3a. Self-Update Preference and Pipeline Backstop

- [ ] 3a.1 Record each declared CLI's native background auto-update state; verify it records `claude` as enabled (`autoUpdate: true`) and `codex`, `Claude-Fable`, `opencode`, `kilo`, `auggie`, and `pi` as not enabled
- [ ] 3a.2 Invoke the self-update verb as a backstop for every declared CLI that provides one, including tools whose native auto-update is enabled; verify the run's agent-CLI stage invokes each declared self-update verb
- [ ] 3a.3 Verify the backstop is idempotent for an already-current tool; verify invoking an up-to-date CLI succeeds, leaves its version unchanged, and reports no update failure — the observed baseline is `Claude Code is up to date (2.1.289)` with exit status zero
- [ ] 3a.4 Report a declared CLI that provides neither a self-update verb nor native auto-update as having no available update path; verify the report names the CLI and its installation channel and does not substitute a package manager's upgrade path
- [ ] 3a.5 Document the self-update-preference rule, the backstop, and the idempotency expectation in `docs/` and verify the documented commands reproduce the idempotent behaviour

## 4. Documented-Channel Recording

- [ ] 4.1 Implement documented-channel recording that captures every installation channel a tool's official documentation names; verify it records both npm and Homebrew for `codex`
- [ ] 4.2 Verify the channel choice is delegated to the version-authority rule and never resolved by preference alone; verify a tool documented under both channels records both and selects by authority
- [ ] 4.3 Verify an installation bypassing an available documented source is reported; verify installing a tool by a non-documented method raises the finding
- [ ] 4.4 Document the documented-channel record and the tie-break rule in `docs/` and verify the documented examples match `codex` and `claude`

## 5. Pipeline Integration and Integration Verification

- [ ] 5.1 Add the read-only version-authority, drift, and self-update-backstop stages to `~/Developer/scripts/workstation-daily-update.sh`, time-bounded and reported like the existing stages; verify a full run completes and reports all stages
- [ ] 5.2 Verify `~/Developer/scripts/workstation-daily-update.sh` and its recorded mirror at `openspec-store/scripts/workstation-daily-update.sh` remain byte-identical after the change; verify the provenance drift stage reports `drifted=0` for it
- [ ] 5.3 Verify that any new executed script added by this change is registered in `openspec-store/config/script-provenance-manifest.tsv`, because the drift stage is manifest-driven and an unregistered script is invisible to it; verify stage 7 covers every script this change adds
  - **Scope note (verified):** the scripts this change touches are invoked as `python3 "${STORE_DIR}/scripts/<name>.py"`, so the store copy IS the executed copy. The provenance guarantee tracks only the *duplication* case — a script with an executed copy outside the store and a recorded mirror inside it. Store-owned scripts are therefore exempt by construction and need no manifest row (`reconcile-agent-cli-coverage.py` already has none, as does `sync-workspace-agent-skills.py`).
  - **The rule to keep:** if any of these scripts ever gains an executed copy under `~/Developer/scripts/` (a copy step, sync, or shim), it becomes a drift candidate and MUST get a manifest row at that point. No manifest change is expected from this change; re-verify rather than assume.
- [ ] 5.4 Verify the new stages require no network access; verify they complete with networking unavailable
- [ ] 5.5 Verify version-authority drift, a measurement failure, an undeclared CLI, and an update failure are each surfaced distinctly in the run summary; verify a run containing all four reports them as four separate findings
- [ ] 5.6 Verify the pipeline reports the baseline cleanly when no drift, no measurement failure, no undeclared CLI, and no update failure exists; verify the summary reports no findings in that state
- [ ] 5.7 Run `openspec validate --all --store openspec-store` and verify it reports zero failures after the specs are archived
