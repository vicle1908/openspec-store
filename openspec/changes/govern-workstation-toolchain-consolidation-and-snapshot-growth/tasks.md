# Tasks

## 1. Snapshot Store Growth Reporting

- [ ] 1.1 Declare a size ceiling and an owner repack command for `~/.agentmemory/snapshots` in a workstation configuration file, and verify the declaration is readable without executing a repack
- [ ] 1.2 Implement a read-only snapshot-store measurement that reports total size, loose-object size, packed size, object count, commit count, and oldest/newest commit dates; verify it reports the measured baseline of 9.67 GiB loose against 17.41 MiB packed
- [ ] 1.3 Implement ceiling evaluation that classifies a store as within-bounds or exceeded with the loose-versus-packed split; verify it reports the current store as exceeded and a small store as within bounds
- [ ] 1.4 Implement the reclaimable-by-repack classification that names the owner command and refuses to propose direct Git object deletion; verify the classification output contains the owner command and contains no `rm` of an object path
- [ ] 1.5 Document the snapshot-store measurement and its ceiling in `docs/` and verify the documented command reproduces the same measurements

## 2. Snapshot Repack and Integrity Verification

- [ ] 2.1 Run the owner repack command against `~/.agentmemory/snapshots`, recording before-and-after measurements; verify the loose-object count drops and the commit count of 862 is preserved
- [ ] 2.2 Verify the store remains readable after the repack by running `git log --oneline -1` and `git fsck` in the store; verify both exit zero
- [ ] 2.3 Verify the owning `agentmemory` tool still opens the store and that its newest snapshot is retrievable; verify the retrieval succeeds
- [ ] 2.4 Implement a repack failure path that leaves existing objects intact and MUST NOT fall back to filesystem deletion; verify a simulated failure leaves the store readable
- [ ] 2.5 Document the repack command and the recoverability check in `docs/` and verify the documented steps match the executed ones

## 3. Tool Install-Location Inventory

- [ ] 3.1 Define the sanctioned install locations (the declared npm global prefix, `~/.local/share/home-toolchain`, the system package-manager prefix, `~/.local/share`) in a configuration file and verify each declared location is inspected
- [ ] 3.2 Implement effective-prefix reconciliation that compares `npm config get prefix` against the prefix the maintenance pipeline passes to `npm install -g` and against the declared prefix; verify it reports the current split (`/opt/homebrew` vs `~/.npm-global`) with the tree each `npm install -g` would target
- [ ] 3.3 Implement authoritative-copy detection that records the resolved executable path for each tool by name; verify it reports `gitnexus` resolving to `~/.local/bin/gitnexus` and `codex` to `/opt/homebrew/bin/codex`
- [ ] 3.4 Implement duplication detection that reports each copy, its measured size, and its owning manager; verify it reports the three `gitnexus` copies and the two `@openai/codex` copies with matching sizes
- [ ] 3.5 Implement Homebrew-adjacency detection that reports an executable under the package manager's `bin` directory which resolves through a symlink into another manager's module directory as owned by that other manager; verify it reports `codex`, `qoder`, `qodercli`, and `prime-agent` as npm-owned despite living in `/opt/homebrew/bin`
- [ ] 3.6 Implement preferred-source detection that reports the available Homebrew formula or cask where one exists; verify it reports cask `codex` for `codex`, cask `claude` for `claude`, and formula `hermes-agent` for `hermes-agent`, and reports none for `Claude-Fable`, `kilo`, `auggie`, `cce`, `pi`, `prime-agent`, and `happy`
- [ ] 3.7 Implement name-collision recording; verify it records that Homebrew's `Anthropic` formula is a different tool and that the `opencode` formula originates from a third-party tap shadowing `homebrew/core`, and verify no replacement is proposed for either
- [ ] 3.8 Implement unsanctioned-location reporting for installations outside the sanctioned set; verify it reports an installation placed in a temporary unscoped directory
- [ ] 3.9 Verify the inventory proposes no deletion and requires explicit authorization for each duplicate; verify the output contains no removal action for any duplicated tool
- [ ] 3.10 Document the sanctioned locations, the declared prefix, the preferred-source table, and the two name collisions in `docs/` and verify the documented values match the configuration file and the measured Homebrew availability

## 4. Duplicate Reclamation Verification Gate

- [ ] 4.1 Implement a post-reclamation execution check that runs each tool's entry point and requires exit status zero; verify it passes for `gitnexus` and `bru` at their authoritative locations
- [ ] 4.2 Implement restoration on a failed execution check and verify a simulated failure restores the reclaimed copy
- [ ] 4.3 Record the per-tool reclaimable estimate as an estimate rather than a guarantee in the inventory output; verify the output labels the figure an estimate

## 4a. npm Global Prefix Reconciliation

- [ ] 4a.1 Declare the chosen npm global prefix in `~/.npmrc` and verify `npm config get prefix` equals the declared prefix and the prefix the maintenance pipeline passes to `npm install -g`
- [ ] 4a.2 After declaring the prefix, verify `npm install -g <probe>` places the package into the declared prefix and NOT into `/opt/homebrew/lib/node_modules`; then uninstall the probe
- [ ] 4a.3 Verify `npm prefix` run from a repository directory still resolves to that directory and not to `$HOME`; verify the earlier home-manifest hijack has not been reintroduced
- [ ] 4a.4 Verify the package-manager-owned tools (`cursor-agent`, `droid`, `opencode`) remain package-manager-managed and are unaffected by the prefix declaration; verify each still resolves into the package manager's cellar or caskroom
- [ ] 4a.5 Document the declared prefix, the reconciliation check, and the rollback (the single `~/.npmrc` line) in `docs/` and verify the documented rollback restores the previous effective prefix

## 5. Agent CLI Coverage Reconciliation

- [ ] 5.1 Implement reconciliation between the declared covered set, the declared uncovered set, and the discovered installed agent CLIs; verify it reports `happy`, `cursor-agent`, `hermes-agent`, `buzz`, and `cce` as undeclared given the current declarations
- [ ] 5.2 Verify reconciliation executes no update verb for an undeclared CLI and removes none; verify an undeclared CLI's update verb is not invoked and the CLI remains on the path during a run
- [ ] 5.3 Record each declared CLI's installation source (package manager, ecosystem manager, or vendor download) and its matching update verb; verify `cursor-agent`, `droid`, and `opencode` record a package-manager source and `Claude-Fable`, `kilo`, `auggie`, `cce`, `pi`, `prime-agent`, `happy` record an ecosystem source
- [ ] 5.4 Verify an update verb is never applied through a manager that does not own the CLI; verify the runner does not apply an ecosystem update verb to a package-manager-owned CLI
- [ ] 5.5 Report the declared covered and uncovered sets before executing any update, requiring no network access; verify the report appears before the first update invocation and succeeds with networking unavailable
- [ ] 5.6 Verify a covered updater failure is reported as a CLI failure and not as an undeclared-coverage finding; verify a simulated updater failure produces the failure outcome only
- [ ] 5.7 Declare each currently undeclared agent CLI as covered or uncovered; verify a subsequent reconciliation run reports no undeclared installations and every installed CLI remains available
- [ ] 5.8 Document the covered/uncovered declarations, the source-to-update-verb mapping, and how to add an entry in `docs/` and verify the documented procedure results in a clean reconciliation

## 6. Storage-Hygiene Integration

- [ ] 6.1 Extend the storage-hygiene audit classification with the tool-duplication and snapshot-object categories, reusing the existing four-class safety model; verify the audit classifies both new categories without altering existing classifications
- [ ] 6.2 Verify the new categories carry an owning-tool command and no direct filesystem deletion; verify the audit output names the owner command for each and proposes no `rm` for a duplicated install or a Git object
- [ ] 6.3 Verify a retention-policy exclusion still prohibits cleanup of a protected path after the extension; verify a `PROTECTED` snapshot path and a `PROTECTED` install path are both excluded

## 7. Pipeline Integration and Integration Verification

- [ ] 7.1 Add the read-only snapshot-growth, duplication-reporting, and coverage-reconciliation stages to `~/Developer/scripts/workstation-daily-update.sh`, time-bounded and reported like the existing stages; verify a full run completes and reports all three stages, with no `script-provenance-manifest.tsv` change required because that script is already registered
- [ ] 7.2 Verify `~/Developer/scripts/workstation-daily-update.sh` and its recorded mirror remain byte-identical after the change; verify the provenance drift stage reports `drifted=0` for it
- [ ] 7.3 Verify the new stages require no network access; verify they complete with networking unavailable
- [ ] 7.4 Verify a snapshot store exceeding its ceiling, an unreconciled npm prefix, and an undeclared agent CLI are each surfaced in the run summary; verify the summary contains all three findings
- [ ] 7.5 Verify the pipeline reports the baseline cleanly when no store exceeds bounds, the prefix is reconciled, and no CLI is undeclared; verify the summary reports no findings in that state
- [ ] 7.6 Run `openspec validate --all --store openspec-store` and verify it reports zero failures after the specs are archived
