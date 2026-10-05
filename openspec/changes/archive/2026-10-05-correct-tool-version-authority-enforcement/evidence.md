# Verification Evidence: Correct Tool Version Authority Enforcement

## 1. Archive Immutability & Reconciled Claims

Prior change `govern-tool-version-authority-and-drift` was archived at `openspec/changes/archive/2026-10-05-govern-tool-version-authority-and-drift/`. In accordance with `skill://openspec-immutable-archive-correction`, the archive directory is strictly immutable and was not modified during this corrective change:

```bash
git -C /Users/androidteam/Developer/platform/openspec-store diff --name-only HEAD -- openspec/changes/archive
# (output: empty — zero bytes modified in archived changes)
```

### Stale Historical Claims vs. Reconciled Live Findings

1. **Shared Updater Registry (`toolchain_updater_registry.py`)**:
   - *Archived State*: Ad-hoc dictionaries and tool-specific if/elif statements diverged across scripts.
   - *Corrective Finding*: Created canonical shared module `toolchain_updater_registry.py` defining `SUPPORTED_UPDATER_REGISTRY` keyed by `(tool, source_type)`. Strictly distinguishes `brew-cask` from `brew-formula` so formula update verbs are never authorized for cask assets. Both `inventory-workstation-toolchain.py` and `reconcile-agent-cli-coverage.py` enforce this shared data model across all covered tools, failing closed (`updater_dispatch='none'`, `update_verb=None`, `drift_status='unknown'`) if the registry is cleared or tool/source is unsupported.
2. **Cellar Node-Backed Formulas (Newman)**:
   - *Archived State*: `inventory-workstation-toolchain.py` flagged `/opt/homebrew/bin/newman` as `is_homebrew_adjacent = True` because its resolved path `/opt/homebrew/Cellar/newman/6.2.2/libexec/lib/node_modules/newman/bin/newman.js` contained `node_modules`.
   - *Corrective Finding*: Evaluating `Cellar` prior to `node_modules` and checking `Cellar not in target.parts` correctly reports `newman` as `brew-formula`, not homebrew-adjacent (`is_homebrew_adjacent: false`).
3. **Authoritative Primary Copy at Index 0 in Duplication**:
   - *Archived State*: When duplicates were found in `~/.local/share/home-toolchain/node_modules/newman`, the authoritative primary copy `/opt/homebrew/Cellar/newman/...` was omitted from `copies`, reporting `has_duplication: false`.
   - *Corrective Finding*: Pop and insert logic ensures the active authoritative copy is strictly at index 0 (`copies[0]`), followed by duplicate copies, accurately reporting `has_duplication: true` and calculating reclaimable space.
4. **Qoder Wrapper Target Inheritance**:
   - *Archived State*: `qoder` was hardcoded to `drift_status: "clean"`, requiring an ad-hoc shell exception in `workstation-daily-update.sh` to prevent updating through its misaligned target `qodercli`.
   - *Corrective Finding*: `qoder` dynamically inherits its target's attributes; because its target resolves under `/opt/homebrew/lib/node_modules/@qoder-ai/qodercli` instead of declared prefix `~/.npm-global`, `qoder` directly reports `target_misalignment`. The ad-hoc shell exception was removed.
5. **Prime-Agent Package Provenance**:
   - *Archived State*: Classified as `authority: "package-wrapper"`, `writer: "package-manager"` or "official Mach-O channel" despite lacking any Homebrew formula or cask receipt.
   - *Corrective Finding*: Climbed parent hierarchy to detect `package.json` at `/opt/homebrew/lib/prime-agent`. Reconciled consistently across both reporters as an npm bundle (`authority: "npm-global"`, `writer: "npm"`, `updater_dispatch: "none"`, `drift_status: "target_misalignment"`, `orthogonal_findings: "Unmanaged package bundle in /opt/homebrew/lib/prime-agent (lacks Homebrew receipt)"`). In coverage reporter, `classify_source` accurately identifies it as `("ecosystem_manager", "npm")`.
6. **Kilo Supported Command (`kilo upgrade`)**:
   - *Archived State*: `inventory-workstation-toolchain.py` reported `update_verb: "kilo update"`.
   - *Corrective Finding*: Upstream CLI documentation and runtime evaluation show the command is `kilo upgrade`. The command is recorded as `kilo upgrade` with `updater_dispatch: "none"` and declared in `AGENT_CLI_KNOWN_UNCOVERED` because its local updater fails.
7. **Scoped NPM Package Deny Filter**:
   - *Archived State*: `awk -F: '{print $4}'` matched `@openai/codex@1.2.3` with version suffixes, causing exact anchored filters `^@openai/codex$` to fail to match and allowing denied packages into `npm install -g`.
   - *Corrective Finding*: Stripping trailing version suffixes via `sub(/@[^@]*$/, "", pkg)` preserves scoped prefixes `@openai/codex` and correctly excludes denied packages.
8. **Independent Homebrew Formula & Cask Rosters**:
   - *Archived State*: Any cask misalignment suppressed all Homebrew upgrades, including unrelated formulae.
   - *Corrective Finding*: Preflight parsing separates `DENY_ROSTER_BREW_FORMULAE` and `DENY_ROSTER_BREW_CASKS`, gating them independently.
9. **Global Pause Policy Enforcement**:
   - *Archived State*: Pause flags only affected Claude in Stage 5.
   - *Corrective Finding*: Centralized pause truthiness parsing (`is_truthy_pause`, `is_global_pause_active`) pauses all mutation stages (Stages 1-5: Homebrew, Bun, npm, uv, and all agent CLIs in Stage 5; plus Stages 6 and 11 apply-mode mutations) while preserving read-only check mode and audit stages. In `reconcile-agent-cli-coverage.py`, `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` is excluded from pause detection. In `workstation-daily-update.sh`, `toolchain_updater_registry` functions are imported directly via `sys.argv[1]` with normalized bash fallback, correctly handling `"TRUE"`, `" true "`, and `"enabled"`.
10. **Crontab Secret Redaction & Macro Handling**:
    - *Archived State*: Crontab inspection captured inline environment variable assignments (e.g. `API_KEY=secret`) into `cmd_baseline`, leaking secret values into reports, and omitted macro lines (`@reboot`).
    - *Corrective Finding*: Parsed inline `KEY=VALUE` assignments to extract variable names into `env_keys` while strictly redacting all secret values, isolated executable basename, and added support for macro triggers (`@reboot`, `@daily`).
11. **Word-Boundary Scheduled Writer Association**:
    - *Archived State*: Substring matching caused short tokens like `pi` to match unrelated jobs (`pip`, `api`).
    - *Corrective Finding*: Word-boundary regex matching (`\b{kw}\b`) ensures tools are only associated with matching background jobs.
12. **Idempotence vs. Channel Currency**:
    - *Archived State*: Unchanged versions (`v_before == v_after`) were claimed as `(idempotent/current)` and "already up to date".
    - *Corrective Finding*: Replaced wording with `update completed; local version unchanged (...) (idempotent, currency unverified)`, reserving `currency verified` for authenticated upstream channel API queries.

---

## 2. Upgraded Regression Test Suite Execution

A dedicated 23-test regression suite was executed via `test-version-authority-governance.py`:

```text
Ran 23 tests in 2.333s
OK
```

All focus areas tested against production functions:
- `test_cellar_node_modules_evaluated_as_brew_formula`: PASS
- `test_caskroom_evaluated_as_brew_cask`: PASS
- `test_npm_global_scoped_evaluated_as_npm`: PASS
- `test_prime_agent_bundle_detected_via_package_json`: PASS
- `test_vendor_download_local_share`: PASS
- `test_production_newman_duplication_has_authoritative_copy_first`: PASS (invokes `inv.inventory_tools()`)
- `test_qoder_inherits_target_misalignment_from_qodercli`: PASS (invokes `inv.evaluate_authority_and_drift()`)
- `test_prime_agent_evaluated_truthfully_without_fabricated_cask`: PASS
- `test_kilo_records_kilo_upgrade_verb_with_none_dispatch`: PASS
- `test_covered_tools_registered_with_verified_commands`: PASS
- `test_unregistered_tool_fails_closed`: PASS
- `test_coverage_evaluator_rejects_source_mismatches`: PASS
- `test_cleared_registry_fails_closed_in_inventory`: PASS (proves inventory enforces registry for all tools)
- `test_crontab_inline_env_secrets_redacted_and_macros_handled`: PASS (proves secret tokens never leak)
- `test_word_boundary_prevents_pi_false_matching_pip_or_api`: PASS
- `test_delegation_flag_does_not_pause_coverage`: PASS (proves CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE does not pause)
- `test_truthiness_normalization`: PASS
- `test_global_pause_active_from_env_or_config`: PASS
- `test_preflight_splits_formulae_and_casks`: PASS
- `test_strip_trailing_version_preserves_scope`: PASS
- `test_deny_filter_matches_scoped_package_and_variants`: PASS
- `test_zero_exit_error_detected`: PASS
- `test_runner_output_wording_does_not_claim_unproven_currency`: PASS

---

## 3. Maintenance Script Parity & Check Mode Verification

1. **Mirror Parity**:
   ```bash
   cmp /Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh /Users/androidteam/Developer/scripts/workstation-daily-update.sh
   # (exit: 0, zero byte diff)
   ```
2. **SHA-256 Digest Equality**:
   Both copies compute to identical digest: `e4bacb6ae26b27a6b45fee010d483fdb4b9408e662e19257d1ee1308c911ff5b`
3. **Provenance Drift Check (Stage 7)**:
   ```text
   checked=7 drifted=0 missing_record=0
   No script drift found: every executed script matches its recorded mirror.
   ```
4. **Non-Mutating Check Mode (Stage 1-5)**:
   Executed `workstation-daily-update.sh --check`:
   - Stage 1 Homebrew updates: suppressed.
   - Stage 2 Bun upgrades: suppressed.
   - Stage 5 Agent CLI updates: suppressed.
   - Zero background metadata or repository mutations occurred.

---

## 4. Lint and Static Syntax Validation

- `shellcheck /Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh`: Clean (0 issues).
- `bash -n /Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh`: Clean.
- `ruff check platform/openspec-store/scripts/{inventory-workstation-toolchain.py,reconcile-agent-cli-coverage.py,toolchain_updater_registry.py,test-version-authority-governance.py,validate-archive-readiness.py}`: All checks passed!

---

## 5. Value-Blind Scheduled-Writer Discovery Evidence

`audit_scheduled_writers()` discovered candidate LaunchAgents structurally:
- Scanned: `~/Library/LaunchAgents`, `/Library/LaunchAgents`, `crontab -l`
- Extracted: labels, executable baselines, schedule frequencies, and environment variable key names.
- Linked: matching candidate background jobs are recorded in `orthogonal_findings` on individual tool items using word boundary matching.
- Redacted: all environment variable values, credentials, tokens, and personal parameters.
- Boundaries: root `/Library/LaunchDaemons`, container engines, and script indirection explicitly noted as bounded non-goals.
