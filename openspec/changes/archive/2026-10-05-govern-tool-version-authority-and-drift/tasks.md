# Tasks

## 1. Measure Version Authority Per Tool

- [x] 1.1 Implement active executable provenance and updater command detection; verify it resolves the real path, wrapper chains (e.g. `qoder` at `~/.qoder/entry/qoder`), and update verbs for declared agent CLIs
- [x] 1.2 Implement package-asset and updater dispatch analysis; verify it distinguishes compatible manager delegation (e.g. `opencode upgrade` delegating to Homebrew) from independent competing writers, and recognizes bundle self-update flags (`auto_updates`) without treating them as blanket waivers
- [x] 1.3 Implement installation-aware version authority determination; verify it correctly elects native authority where supported, accepts manager authority when no compatible native updater exists, and flags prefix target-misalignment risks without hardcoding unverified drift sets
- [x] 1.4 Implement `unknown` authority recording with explicit evidence gaps; verify an unverified or ambiguous tool is recorded as unknown and suppressed from automated mutation without blocking other tools
- [x] 1.5 Document the active provenance detection, updater dispatch classification, and version-authority model in `docs/` and verify documented commands run as written

## 2. Drift Reporting

- [x] 2.1 Implement version-authority conflict and drift detection that identifies configured or scheduled independent writers or verified incompatible write paths, naming the active command and conflicting manager; verify it reports genuine conflicts and produces no drift finding for compatible delegation
- [x] 2.2 Record the specific consequence in each conflict finding (e.g. uncoordinated overwrite or target prefix divergence); verify finding text articulates the exact risk or measured outcome
- [x] 2.3 Verify drift is reported as an independent finding class, distinct from undeclared coverage and execution failures; verify a run reports drift without falsely asserting coverage or execution defects
- [x] 2.4 Verify compatible delegation and aligned single-writer configurations produce zero drift findings; verify compliant installations report clean authority status
- [x] 2.5 Implement measurement-failure reporting as a DEGRADED finding with its own flag, distinct from domain findings; verify a clean report (exit 0) records zero undeclared, a complete valid domain report (exit 1 matching contract) records the undeclared count without setting measurement-failure, and an abnormal exit, crash, timeout, or malformed output sets AGENT_COVERAGE_MEASURE_FAILED=1
- [x] 2.6 Document the drift finding criteria, the domain-finding versus measurement-failure distinction, and reporter exit code handling in `docs/` and verify documented examples match live reporter behavior

## 3. Declared Update Verb Follows the Version Authority

- [x] 3.1 Implement declaration validation in the inventory reporter that checks covered CLI update declarations against elected version authority and active target prefix; verify it flags declarations targeting uncoordinated managers or misaligned prefixes
- [x] 3.2 Report the compatible update command and target scope an inconsistent declaration should use instead; verify the report names the correct native command or verified manager delegation path
- [x] 3.3 Update declared covered set in `workstation-daily-update.sh` so each entry's update verb and binary identity (e.g. `qoder`) correspond to verified authority; verify subsequent check reports no declaration inconsistencies
- [x] 3.4 Verify the runner enforces version authority across all relevant mutation stages (Stages 1, 2, 3, and 5); verify actual writers and target scopes are respected, permitting compatible native entrypoints that delegate to the selected manager while prohibiting unauthorized or wrong-target writes
- [x] 3.5 Document the version authority mapping, declaration schema, and cross-stage mutation guards in `docs/` and verify documented procedures yield zero declaration defects

## 3a. Self-Update Preference and Pipeline Backstop

- [x] 3a.1 Audit native background auto-update settings non-destructively as-is (e.g. Claude Code `autoUpdatesChannel`, `DISABLE_AUTOUPDATER`); verify it records observed configuration without mutating user settings
- [x] 3a.2 Invoke the declared update path in apply mode as an idempotent backstop for eligible covered CLIs; verify apply mode executes authorized backstops while check mode suppresses all update execution
- [x] 3a.3 Verify the backstop is idempotent for an already-current tool and verifies post-update currency; verify invoking an up-to-date CLI succeeds, leaves its version unchanged, and verifies the active executable on `$PATH` within its active installation root
- [x] 3a.4 Report a declared CLI that has no compatible supported native update path and no supported manager path as lacking an update path; verify the report identifies the tool and channel rather than executing a guessed update verb
- [x] 3a.5 Document the native-first preference, apply backstop execution, and idempotency verification in `docs/` and verify documented commands reproduce expected behavior

## 4. Documented-Channel Recording

- [x] 4.1 Implement documented-channel recording that captures verified installation channels from official documentation and active provenance; verify it records both npm and Homebrew for `codex` and distinguishes native vs manager installs for `claude`
- [x] 4.2 Verify channel selection is resolved by installation-aware version authority and active provenance rather than blanket preference; verify multi-channel tools select authority matching their active installation
- [x] 4.3 Verify an installation bypassing an available documented source or residing outside sanctioned locations is reported as an orthogonal finding; verify unsanctioned wrappers or downloads raise appropriate inventory findings
- [x] 4.4 Document channel recording, selection precedence, and orthogonal location checks in `docs/` and verify documented examples match verified tool channels

## 5. Pipeline Integration and Integration Verification

- [x] 5.1 Integrate read-only version authority, drift detection, and guarded update stages into `~/Developer/scripts/workstation-daily-update.sh`; verify a full check run and apply run execute expected stages without regression
- [x] 5.2 Verify `~/Developer/scripts/workstation-daily-update.sh` and `openspec-store/scripts/workstation-daily-update.sh` maintain byte-identical parity; verify Stage 7 provenance check reports `drifted=0`
- [x] 5.3 Verify script provenance manifest registration scope: confirm store-owned scripts invoked directly from the store need no manifest entry, and verify any new executed script duplicated under `~/Developer/scripts/` is registered in `openspec-store/config/script-provenance-manifest.tsv`
- [x] 5.4 Verify standalone local authority and coverage reporters require no network access; verify check mode (`--check`) executes zero update verbs and mutates no installations, configurations, or package-manager metadata, while guarding Stage 1 `brew update` and Stage 2 `bun upgrade`
- [x] 5.5 Verify version authority drift, reporter measurement failure, undeclared CLI findings, and update execution failures are surfaced distinctly in the run summary; verify simulated multi-defect states report separate summary lines
- [x] 5.6 Verify clean baseline reporting when no drift, measurement failures, undeclared CLIs, or update failures exist; verify summary reports all stages healthy
- [x] 5.7 Run `openspec validate govern-tool-version-authority-and-drift --strict --json --store openspec-store` and verify all change artifacts pass strict schema validation before declaring readiness
