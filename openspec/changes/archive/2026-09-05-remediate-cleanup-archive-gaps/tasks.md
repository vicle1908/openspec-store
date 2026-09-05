## 1. Evidence Preparation

- [x] 1.1 Create a timestamped value-blind verification manifest for both target archives; verify the manifest contains paths, booleans, hashes, modes, sizes, and no credential-shaped literals.
- [x] 1.2 Build the authoritative 19-repository inventory from `/Users/androidteam/Developer/AGENTS.md:365-368` plus `tdt-scheduler`, then record one result row per repository covering branch/status classification and unrelated dirty paths; verify the row count equals 19, store the ordered list and its sha256 digest, and do not delete or promote unrelated dirty paths as evidence.
- [x] 1.3 Record one result row per repository for worktree count, virtual-environment presence, and tdt-scheduler embedded-copy comparison; verify the inventory covers all 19 repositories with command identity and outcome, and that the earlier 10-repository sample is not promoted into the evidence manifest.
- [x] 1.4 Record AutoForward Messages and Nicegram plist presence, executable existence, nonzero byte size, and executable mode; verify executable checks are distinct from wrapper metadata checks and record the gate as currently resolved only if both binaries verify.
- [x] 1.5 Record read-only application evidence for the five Homebrew cask apps (VS Code, Ollama, Google Chrome, Postman, Warp): bundle Info.plist presence, declared CFBundleExecutable, and actual executable existence; verify each app's declared executable is present and nonzero, nonempty, and executable mode.
- [x] 1.6 Record read-only Stably AI Orca evidence: bundle Info.plist presence, CFBundleIdentifier equal to com.stablyai.orca, CFBundleShortVersionString, main executable existence, and Caskroom `.upgrading` state; verify identity and version without mutating the installation.
- [x] 1.7 Run `brew doctor` read-only and record whether it reports Caskroom metadata or `.upgrading` warnings for the six brew-managed apps; run an executable-aware final scan over `/Applications` and record any app missing its expected plist/executable metadata.

## 2. Integrity and Blockers

- [x] 2.1 Record that archived cleanup directories remain unchanged; verify archive paths are absent from the corrective change's modified-file set.
- [x] 2.2 Record the manual sideload reinstall gate conditionally: if the executable verification fails, keep it blocked as user-owned; if both binaries verify, record the gate resolved/currently unnecessary with existence, nonzero size, and executable-mode evidence, without claiming reinstall provenance.
- [x] 2.3 Record the Cline/provider archive invalidation and accepted-risk follow-up as historical context only; verify no credential or provider configuration is changed.

## 3. Validation and Closure

- [x] 3.1 Review the evidence manifest for completeness and secret-shape absence; verify all target claims have an explicit verified, unverified, or blocked status.
- [x] 3.2 Run `openspec validate remediate-cleanup-archive-gaps --strict --json`; verify the change is structurally valid.
- [x] 3.3 Run the strict archive-readiness validator for this active change; verify it remains blocked until all evidence tasks and any user-owned gate are genuinely resolved.
- [x] 3.4 Record final scope and commit readiness without archiving; verify no archived files are edited and no destructive action occurred.
