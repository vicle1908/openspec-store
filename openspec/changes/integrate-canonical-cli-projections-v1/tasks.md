# Tasks: integrate-canonical-cli-projections-v1

## Phase 1: Canonical provider-selection design (COMPLETE)

- [x] 1.1 Write `design.md` with field-source matrix, selection algorithm, multi-provider scenario.
- [x] 1.2 Write `proposal.md` with scope boundaries and risks.

## Phase 2: Public tdt-core selection API (NOT STARTED)

- [ ] 2.1 Write RED tests for `select_canonical_cli_provider()`:
  - independent Claude/Codex selection from one canonical catalog
  - default alias selection
  - explicit alias selection
  - provider/alias mismatch rejection
  - unsupported CLI provider
  - unsupported effort
  - unsupported limit
  - no credential values
  - immutable output
  - provenance retention
  - legacy-only compatibility
  - disabled/missing provider behavior
- [ ] 2.2 Implement `CanonicalCLISelection` dataclass in `tdt-core`
- [ ] 2.3 Implement `select_canonical_cli_provider()` in `tdt-core`
- [ ] 2.4 Run gates: focused tests, full tdt-core suite, ruff, mypy, diff-check, detect-changes
- [ ] 2.5 Commit the public contract separately

## Phase 3: Correct ai-harness-skills bridge (NOT STARTED)

- [ ] 3.1 Rebase `phase6/tdt-core-projection` onto new tdt-core contract
- [ ] 3.2 Replace local field guessing with `select_canonical_cli_provider()`
- [ ] 3.3 Write RED runtime-composition tests (10 minimum)
- [ ] 3.4 Wire into `build_runtime()` (CRITICAL risk, 16 symbols — user approved)
- [ ] 3.5 Run repository-required gates (ruff, mypy, full suite, detect-changes)
- [ ] 3.6 Commit separately, keep generated metadata out of product commits

## Phase 4: ai-review integration (NOT STARTED)

- [ ] 4.1 Fresh GitNexus analysis and impact assessment
- [ ] 4.2 Integrate public selector at reviewer subprocess-launch boundary
- [ ] 4.3 Write RED tests for Claude, Codex, Kimi, Pi
- [ ] 4.4 Handle capability differences (aliases/effort support)
- [ ] 4.5 Classify existing pytest session issue
- [ ] 4.6 Run gates and commit

## Phase 5: Registry retirement decision (NOT STARTED)

- [ ] 5.1 Record decision: retain registry for legacy aliases and CLI capability metadata
- [ ] 5.2 Permit new-schema `auth_env` to remain direct and provider-local
- [ ] 5.3 Document that registry is not removed until every legacy consumer has migrated

## Phase 6: Downstream + live CLI matrix (NOT STARTED)

- [ ] 6.1 Full tdt-core suite
- [ ] 6.2 Full ai-harness-skills suite
- [ ] 6.3 Full ai-review suite
- [ ] 6.4 Existing downstream consumers without PYTHONPATH
- [ ] 6.5 Clean-install dependency checks
- [ ] 6.6 Real native CLI calls through each consumer boundary
- [ ] 6.7 Recorded: provider, alias, wire model, duration, command, SHA

## Phase 7: OpenSpec closure + archive (NOT STARTED)

- [ ] 7.1 Update Phase 5/6/9 checkboxes in v2
- [ ] 7.2 Replace "not implemented" scenarios with implemented scenarios
- [ ] 7.3 Update exact SHAs and final test counts
- [ ] 7.4 Validate focused change
- [ ] 7.5 Validate entire store
- [ ] 7.6 Run git diff --check
- [ ] 7.7 Archive following normal OpenSpec workflow
- [ ] 7.8 Synchronize canonical specs
