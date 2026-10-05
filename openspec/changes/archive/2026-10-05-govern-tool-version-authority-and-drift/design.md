# Design: Govern Tool Version Authority and Drift

## Context

See `proposal.md — Why`. The archived change
`govern-workstation-toolchain-consolidation-and-snapshot-growth` established sanctioned install
locations, the single npm global prefix (`prefix = ~/.npm-global` declared in `~/.npmrc`), and
preferred-source reporting. While that change achieved prefix parity between `npm config get prefix`
and maintenance scripts, it left version authority—the mechanism permitted to advance or pin a
tool's version—uncovered.

A prior planning draft asserted a version-authority downgrade matrix (`codex`, `Claude-Fable`,
and `opencode` drifting; `claude` and `droid` avoiding drift based solely on Homebrew cask
`auto_updates`). Primary-source investigation of upstream package managers, runtime binaries,
and official vendor documentation reveals that model was grounded in inaccurate assumptions:

1. **Homebrew Cask Deferral Semantics**:
   Inspection of local Homebrew source (`/opt/homebrew/Library/Homebrew/cask/cask.rb` lines
   433-454, 819-861; `/opt/homebrew/Library/Homebrew/env_config.rb` lines 661-663, 764-771;
   and `https://docs.brew.sh/Manpage`) shows that in Homebrew's cask outdated logic (`outdated_version`),
   receipt logic can invoke bundle-version comparison under current defaults. Greedy options permit
   including eligible `auto_updates` casks in upgrade considerations, while the quoted guard
   (`auto_updates_bundle_outdated?`) disables bundle-version inspection when `auto_updates` is absent
   or the cask version is latest, rather than acting as a blanket waiver for all upgrades. Thus
   `auto_updates: true` is an internal bundle update indicator, not an exclusive version-control waiver.
   Furthermore, Homebrew cask `claude` (`https://formulae.brew.sh/api/cask/claude.json`) distributes the
   macOS GUI desktop application (`/Applications/Claude.app`), whereas the CLI is Anthropic's Claude
   Code (`https://formulae.brew.sh/api/cask/claude-code.json` or npm `@anthropic-ai/claude-code`). On
   this workstation, the active CLI is a native installation under
   `~/.local/share/claude/versions/2.1.289`, completely independent of cask `claude`.

2. **Updater Dispatch Entrypoints vs. True Version Writers**:
   Inspection of OpenCode v1.18.34 source
   (`https://github.com/anomalyco/opencode/blob/v1.18.34/packages/opencode/src/installation/index.ts`)
   demonstrates that `opencode upgrade` checks its installation context and explicitly delegates
   Homebrew-installed instances to `brew upgrade`. The command entrypoint does not compete with
   Homebrew; both route to the same writer under compatible delegation. The installing manager
   remains the single actual version writer, and delegation is an entrypoint, not a second writer.
   An authority conflict requires configured or scheduled independent writers, not mere dual command
   capability.

3. **Prefix Target Alignment and Codex Source Verification**:
   Inspection of Codex CLI v0.160.0 source
   (`https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/cli/src/main.rs` `run_update_action` /
   `run_update_command` and `tui/src/update_action.rs`) shows that its npm update action executes
   `npm install -g @openai/codex` without an explicit `--prefix` argument. An explicit prefix argument
   is not strictly required if a tool's dispatch reliably targets the active installation root via
   environment, receipt files, or configuration. However, on this workstation, the declared global npm
   prefix is `~/.npm-global`, whereas the active codex executable resolves to
   `/opt/homebrew/lib/node_modules/@openai/codex/bin/codex.js`. Evaluating effective write targets
   across environment variables, package receipts, and updater configuration reveals a structural
   prefix target-misalignment risk `[INFERENCE]`. No updater has been executed, and no stale version or
   downgrade has been observed.

4. **Claude Code Configuration and Vendor Guidance**:
   Current official Claude Code documentation (`https://code.claude.com/docs/en/setup`) defines
   native background auto-updates (`autoUpdatesChannel: "stable"|"latest"`, `DISABLE_AUTOUPDATER`,
   `DISABLE_UPDATES`) and manager-managed updates (`CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE=1`).
   `DISABLE_AUTOUPDATER` affects background auto-updates only (manual native update commands remain
   valid), whereas `DISABLE_UPDATES` blocks all update mutations under user policy. Generic boolean
   assertions like `autoUpdate: true` do not reflect upstream configuration keys.

5. **Binary Identity vs. Display Labels (qoder / Claude-Fable)**:
   In `~/Developer/scripts/workstation-daily-update.sh` (line 198), `qoder:Claude-Fable:update`
   uses `Claude-Fable` purely as an informational display label. The binary is `qoder`, resolving
   to the wrapper script `~/.qoder/entry/qoder`. There is no Homebrew cask named `Claude-Fable`.
   Wrapper locations outside sanctioned paths remain orthogonal location findings under
   `workstation-toolchain-inventory`.

6. **Workstation Pipeline Check Mode and Reporter Defects**:
   In `scripts/workstation-daily-update.sh`, Stage 1 executes `brew update 2>&1 || true`
   unconditionally (lines 329-339) in check mode, and Stage 2 runs `bun upgrade` (lines 344-347)
   without checking `MODE`. Furthermore, Stage 1 (Homebrew) and Stage 3 (global npm packages,
   line 360) perform updates before Stage 5 (Agent CLI updates). In Stage 10 (Agent CLI Coverage),
   `reconcile-agent-cli-coverage.py` returns exit code 1 at line 144 when undeclared installations
   are detected (`return 1 if undeclared else 0`). The runner at lines 471-480 treats any nonzero
   exit as a measurement failure (`AGENT_COVERAGE_MEASURE_FAILED=1`) and leaves
   `AGENT_UNDECLARED_COUNT=0`. A complete valid report matching the documented contract must be
   recognized, and crashes, timeouts, or malformed outputs distinguished.

7. **Status of Existing `evidence.md`**:
   The existing `evidence.md` in the change directory contains prior run claims asserting task 2.5
   was completed. However, those claims do not prove the coverage finding case (e.g. exit code 1
   with undeclared CLIs, which still triggers `AGENT_COVERAGE_MEASURE_FAILED=1` in source) nor
   current non-mutating check-mode behavior. Because the reporter defect is present in source scripts
   and current review is strictly read-only on static logic and standalone reporters without live
   updater execution, task 2.5 must be reopened as `[ ]`. Per OpenSpec write boundaries,
   `evidence.md` is not modified during this planning revision; full evidence reconciliation is
   deferred to the apply phase.

### Existing Patterns to Reuse

- `workstation-toolchain-inventory`: Extends authoritative location rules, npm prefix validation,
  and preferred-source reporting to govern installation-aware version authority.
- `agent-cli-inventory-coverage`: Reuses declared covered (`AGENT_CLI_COVERED`) and declared
  uncovered (`AGENT_CLI_KNOWN_UNCOVERED`) sets, establishing distinct reporting for drift,
  coverage, execution failures, and measurement crashes.
- `workstation-daily-update.sh`: Reuses time-bounded execution (`run_with_timeout`), stage
  structure, and summary reporting patterns.

## Goals / Non-Goals

**Goals:**
- Elect exactly one compatible version authority per tool, preferring tool-native updaters where
  supported for that installation and accepting supported manager paths where native updaters are
  absent or incompatible.
- Recognize compatible updater delegation (e.g. `opencode upgrade` delegating to `brew upgrade`)
  as the same authority, recording the manager as the single actual version writer.
- Identify true version-authority conflicts arising from configured or scheduled independent writers
  or verified incompatible write paths, distinguishing conflict risks from observed drift.
- Ensure update commands explicitly target the authoritative installation directory and prefix,
  mitigating prefix target-misalignment risks by pre-checking effective targets before writes.
- Govern all relevant mutation stages (Stages 1, 2, 3, and 5) consistently so actual version writers
  and target scopes are enforced, permitting compatible native delegators while prohibiting
  unauthorized writes.
- Ensure check mode (`--check`) executes zero update verbs and mutates no installations, configurations,
  or package-manager metadata, while standalone local authority audits run offline.
- Separate coverage status, authority drift findings, update execution outcomes, and reporter
  measurement health into distinct, non-conflated reporting classes.
- Record genuine unverified states as `unknown` with evidence gaps, suppressing automated updates
  for those tools without blocking other known-good tools.

**Non-Goals (design-level):**
- Removing, relocating, or reinstalling installed tools, or forcing all tools onto one package manager.
- Changing declared npm global prefix (`~/.npm-global`), sanctioned location boundaries, credentials,
  or user configuration.
- Forcing every unrelated external network check offline in check mode; the offline guarantee
  applies to standalone local reporters.
- Overriding intentional update-disable, pin, or pause controls (e.g. `DISABLE_UPDATES`); manager
  fallback must never bypass deliberate native update disablement.
- Speculating on future package-manager features or resolving policy questions not grounded in
  current evidence.
- Editing archived changes or modifying the change's existing `evidence.md` during planning.
- Implementing code or executing tool updates during this planning revision.

## Decisions

### Decision 1: Installation-Aware Version Authority vs. Updater Dispatch Entrypoint
- **Rationale**: An updater entrypoint (`opencode upgrade`, `codex update`) that inspects its
  installation context and delegates to the installing package manager does not represent an
  independent writer. It routes to the installing manager under compatible delegation. The installing
  manager is recorded as the single actual version writer. Delegation is an entrypoint, not a second
  writer. True drift requires configured or scheduled independent writers or verified incompatible
  write paths; mere dual capability is not drift.
- **Alternative considered**: Treating any CLI update verb as an independent self-updater. Rejected
  because it creates false-positive drift findings for well-formed delegating CLIs like OpenCode.

### Decision 2: Native-First Update Policy with Supported Manager Fallback
- **Rationale**: Tool-native update commands are preferred when they are compatible with the active
  installation. However, when an installed tool has no compatible supported native update path for its
  installation (e.g. native binary without update subcommand, or package-managed tool whose native
  updater is disabled by design), its installing package manager is accepted as the supported version
  authority. Intentional user update-disable controls (such as `DISABLE_UPDATES`) or channel pins must
  be respected and recorded as-is; manager fallback is never a permission to bypass intentional
  update pauses.
- **Alternative considered**: Forbidding package-manager upgrades for any tool lacking a self-update
  command. Rejected because it would leave tools without native updaters permanently unmanaged,
  violating the main spec's requirement that manager-owned tools update via their owning manager.

### Decision 3: Homebrew Cask `auto_updates` Semantics and Asset Disambiguation
- **Rationale**: Homebrew's source demonstrates that `outdated_version` receipt logic can invoke
  bundle-version comparison under current defaults. Greedy options permit including eligible
  `auto_updates` casks in upgrades, while `auto_updates_bundle_outdated?` disables bundle inspection
  when `auto_updates` is absent or the version is latest. `auto_updates` is an internal bundle update
  indicator, not an exclusive version-control waiver. Furthermore, asset identity must not be conflated:
  cask `claude` installs the desktop GUI app (`/Applications/Claude.app`), whereas the CLI is
  managed independently.
- **Alternative considered**: Relying on `auto_updates` as an absolute version waiver. Rejected
  because it misrepresents Homebrew's upgrade behavior and conflates GUI apps with CLI binaries.

### Decision 4: Active Executable Provenance, Wrapper Chains, and Prefix Target Alignment
- **Rationale**: Governance must evaluate the active executable resolved on `$PATH`, tracing symlink
  chains and wrapper scripts (e.g. `qoder` wrapper at `~/.qoder/entry/qoder`). Verification targets
  the active installation root, publisher, and channel on `$PATH`, recognizing that versioned physical
  paths (e.g. `~/.local/share/claude/versions/2.1.289` advancing to `2.1.290`) change legitimately
  upon update. Effective write targets must be pre-checked across environment, receipts, and config
  BEFORE executing updates. Known misaligned or unverified write actions must be suppressed, and
  authorized updates post-checked to confirm the active executable entrypoint on `$PATH` resolves to
  the current version within the active installation root.
- **Alternative considered**: Relying on binary name or parent directory alone without symlink
  resolution, or freezing versioned physical paths. Rejected because symlinks in `/opt/homebrew/bin`
  frequently point to ecosystem modules, and versioned paths legitimately advance.

### Decision 5: Multilateral Pipeline Stage Governance (Stages 1, 2, 3, and 5)
- **Rationale**: Version authority must govern all mutation stages in `workstation-daily-update.sh`:
  Stage 1 (`brew upgrade`), Stage 2 (`bun upgrade`), Stage 3 (`npm install -g`), and Stage 5
  (Agent CLI updates). Governance enforces the invariant that the same elected actual version writer
  and verified active target scope are maintained across stages. Compatible native frontends that
  delegate to package managers (e.g. `opencode upgrade`) target the same actual writer and do not
  conflict. Authority conflicts occur only when uncoordinated independent writers or misaligned
  scopes operate across stages.
- **Alternative considered**: Banning any native updater command on manager-owned tools. Rejected
  because it would break compatible native frontends that safely delegate to package managers.

### Decision 6: Offline Local Audits and Non-Mutating Check Mode vs. Networked Apply Mode
- **Rationale**: Standalone local authority and coverage reporters run offline without network access.
  In full check mode (`MODE=check`), the pipeline executes zero update verbs and mutates no
  installations, configurations, or package-manager metadata. `brew update` (line 332) and
  `bun upgrade` (line 346) must be guarded so they do not run during check mode. Unrelated read-only
  upstream status queries (such as `brew outdated`) may contact remote endpoints. In apply mode,
  authorized update commands execute with per-tool time bounds and verify post-update currency.
- **Alternative considered**: Forcing every unrelated external network check offline in check mode.
  Rejected because read-only upstream version queries are informational and do not mutate workstation
  state.

### Decision 7: Separation of Domain Findings from Reporter Measurement Failures
- **Rationale**: `reconcile-agent-cli-coverage.py` returning exit code 1 accompanied by a complete,
  valid report matching the documented contract represents a successful measurement with domain
  findings. Classifying any nonzero exit code as `AGENT_COVERAGE_MEASURE_FAILED=1` misinterprets
  valid findings as crashes and drops the undeclared count. Actual crashes, timeouts, missing, or
  malformed outputs set `AGENT_COVERAGE_MEASURE_FAILED=1`, indicating measurement state is degraded
  and unknown without claiming healthy zero findings.
- **Alternative considered**: Treating all nonzero exits as crashes. Rejected because it obscures
  valid domain findings and causes false degradation reports.

### Decision 8: Authoritative Handling Declarations and Orthogonal Status Checks
- **Rationale**: Coverage requires every declared agent CLI to have an authoritative handling
  declaration: covered CLIs declare a verified automated update path (native or delegating);
  uncovered CLIs declare an explicit governing channel or manual status. Declaring a tool uncovered
  satisfies the undeclared-coverage check in Stage 5, but does not waive or mask coexisting version
  drift, execution failures, or missing update paths. The agent stage MUST NOT update uncovered tools;
  all stages MUST NOT update undeclared tools. Location violations and prefix splits remain
  orthogonal findings under `workstation-toolchain-inventory`.
- **Alternative considered**: Requiring every declared tool to have an automated update verb in
  Stage 5. Rejected because it contradicts legitimate earlier-stage manager handling and manual
  governance.

### Decision 9: Audit-as-is for Native Background Auto-Update Configuration
- **Rationale**: Tools with native background auto-updates (such as Claude Code) configure update
  behavior through upstream keys (`autoUpdatesChannel`, `DISABLE_AUTOUPDATER`). The audit inspects
  these settings non-destructively as-is, reporting observed configuration without mutating user
  files or forcing updates on or off.
- **Alternative considered**: Automatically editing tool configuration files to enable or disable
  native auto-updates. Rejected because workstation governance must observe and adapt to user
  settings without unsolicited mutation.

### Decision 10: Unknown Gating for Undetermined Authority States
- **Rationale**: When active provenance, updater dispatch, or version authority cannot be determined
  with high confidence from available evidence, the tool's authority must be recorded as `unknown`
  with explicit evidence gaps. Automated update mutations for that tool must be gated (suppressed)
  while allowing known-good tools to proceed normally.
- **Alternative considered**: Guessing an authority or defaulting to Homebrew. Rejected because
  guessing creates uncoordinated write paths and silent version reversions.

## Transaction boundaries

- **Audit Mode (Check Mode)**: Non-mutating and offline for local reporters. Executes no update
  commands, modifies no package-manager metadata, and alters no configuration files. Unrelated
  read-only upstream status checks may access the network.
- **Apply Mode**: Executes authorized update commands for eligible tools within explicit per-tool
  time bounds. Pre-checks effective write targets before execution, and post-checks active
  entrypoint resolution on `$PATH` within the active installation root.
- **Failure Bounding and Rollback**: External updaters may partially mutate an installation before
  failing or timing out; the pipeline cannot guarantee external commands leave files untouched.
  The runner records the failure, avoids automatic uncoordinated fallback, channel migration,
  removal, or downgrade, and post-observes the safe active path and version (or marks authority/version
  as `unknown` if indeterminate). Version control rollback of maintenance scripts reverts pipeline
  orchestration and reporting configuration, but does not revert physical tool binary modifications;
  recovery of mutated tool installations requires operator-authorized actions.

## Risks / Trade-offs

- **[Risk] Update action lacks explicit prefix override (Codex npm install -g)** → **Mitigation**:
  The inventory evaluates effective write targets across environment, receipts, and config BEFORE
  executing updates. Known misaligned or unverified write actions are suppressed, and authorized
  updates post-checked to confirm the active executable entrypoint on `$PATH` resolves to the intended
  version within the active installation root.
- **[Risk] Upstream CLI modifies its updater dispatch logic across releases** → **Mitigation**:
  Authority detection evaluates the currently installed binary and its dispatch behavior. If
  dispatch becomes ambiguous, authority is recorded as `unknown` with evidence gaps.
- **[Risk] Reporter exit code 1 misinterpreted as execution crash** → **Mitigation**:
  The runner parses the output of `reconcile-agent-cli-coverage.py` to extract `AGENT_UNDECLARED_COUNT`
  when exit code 1 is accompanied by a complete valid report, reserving `AGENT_COVERAGE_MEASURE_FAILED=1`
  for abnormal terminations, timeouts, or malformed reports.
- **[Risk] Early pipeline stages (Stages 1-3) inadvertently update native-governed tools** →
  **Mitigation**: Stage 1 and Stage 3 upgrade commands are constrained or filtered to exclude
  tools whose version authority is elected as native without manager delegation.

## Migration Plan

1. **Reporter Enhancement**: Update `inventory-workstation-toolchain.py` and
   `reconcile-agent-cli-coverage.py` to inspect active executable provenance, symlink targets,
   updater dispatch, and target prefixes.
2. **Reporter Defect Fix in Runner**: Update `workstation-daily-update.sh` Stage 10 to extract
   `AGENT_UNDECLARED_COUNT` from complete valid reports (including exit code 1) and restrict
   `AGENT_COVERAGE_MEASURE_FAILED=1` to actual execution crashes, timeouts, or malformed reports.
3. **Check Mode Hardening**: Guard `brew update` (Stage 1) and `bun upgrade` (Stage 2) behind
   `[[ "${MODE}" != "check" ]]` in `workstation-daily-update.sh`.
4. **Coverage Declaration Alignment**: Reconcile `AGENT_CLI_COVERED` and `AGENT_CLI_KNOWN_UNCOVERED`
   in `workstation-daily-update.sh` to match elected version authorities, authoritative handling
   declarations, and exact binary identities (e.g. `qoder`).
5. **Script Parity and Manifest Verification**: Ensure byte-identical parity between
   `~/Developer/scripts/workstation-daily-update.sh` and its store mirror at
   `platform/openspec-store/scripts/workstation-daily-update.sh`, and verify conditional script
   provenance manifest registration.
6. **Verification and Validation**: Run check mode and apply mode tests; validate the change with
   `openspec validate govern-tool-version-authority-and-drift --strict --json --store openspec-store`.

## Open Questions

None that block implementation. Undetermined authority or dispatch states are handled safely at
runtime by recording authority as `unknown` with explicit evidence gaps, gating automated updates for
the affected tool.
