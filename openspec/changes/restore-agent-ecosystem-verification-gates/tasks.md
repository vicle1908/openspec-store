## 1. Baseline, ownership, and archived-claim ledger

- [x] 1.1 Create one dedicated worktree/branch for each affected repository, read its closest AGENTS.md, record toolchain commands, and refuse overlapping write ownership.
- [x] 1.2 Capture each repository's HEAD, branch, sorted dirty-path inventory, and production-relevant content fingerprint before edits; re-check identity before every claim.
- [x] 1.3 Build a corrective ledger linking the archived agent-ecosystem-hardening, agent-ecosystem-hardening-cleanup, close-agent-ecosystem-hardening-verification-gaps, and close-three-repo-e2e-verification-gaps claims to current source, owner, command, result, and closure evidence.
- [x] 1.4 Classify graphify-out/, the untracked agent-docs-sync/doc-sync/SKILL.md scaffold, tracked report history, active OpenSpec changes, and the android-scanner host/profile finding as unrelated or separately owned; do not delete, stage, or use them as passing evidence.
- [x] 1.5 Run GitNexus impact analysis before any production symbol edit; if all repairs remain test/documentation-only, record that no production symbol was changed and preserve the stop-and-revise rule for contract drift.

## 2. Make agent-core tests hermetic

- [x] 2.1 Reproduce and record the nine provider-construction failures with provider credentials unset and network disabled, preserving the exact test names and failure boundaries.
- [x] 2.2 Update the affected model-loading, CLI-model, characterization, and rollback fixtures to use explicit Pydantic AI test providers/models or an injected provider factory; do not set global credentials or call a live provider.
- [x] 2.3 Reproduce and record the five HTTP-tool DNS failures (six HTTP test cases total; five depend on public DNS resolution — the private IP case resolves to itself). Add deterministic getaddrinfo fixtures around the existing destination-validation boundary while retaining blocked-host, private/reserved-address, redirect, and response-limit assertions. The _mock_getaddrinfo fixture intercepts socket.getaddrinfo to return a deterministic public IP (93.184.216.34) for non-private hosts while preserving private IP detection for 127.0.0.1/10.x. The negative coverage suite adds 10 new test cases: OSError → dns_resolution_failed, empty resolver → dns_resolution_failed, 5 blocked IP classes (loopback, private, link-local, reserved, multicast) → blocked_destination, HTTPS redirect with DNS revalidation (redirects_followed=1), blocked redirect fails closed, and response truncation with metadata[truncated] assertion.
- [x] 2.4 Run the complete agent-core gates from its worktree: locked dependency resolution, format check, Ruff, mypy src tests --strict, full pytest, declared per-repository coverage/security gates, and CLI subprocess probes; retain exact exit status, skips, and source identity.

## 3. Restore strict consumer typing

- [x] 3.1 In agent-harness, correct the nine strict-mypy failures in test fixtures and supported model-boundary usage; prefer "test" identifiers where HarnessServices.model is declared as str | None, and do not add broad ignores or relax strictness.
- [x] 3.2 Run agent-harness format, Ruff, mypy src tests --strict, full pytest, declared coverage/security gates, and CLI subprocess probes; record the six prerequisite skips separately from pass/fail.
- [x] 3.3 In agent-docs-sync, add the missing annotation at tests/test_state_lifecycle.py's alternate-TDT-home fixture boundary without changing production behavior.
- [x] 3.4 Run agent-docs-sync format, Ruff, mypy src tests --strict, full pytest, declared coverage/security gates, and CLI subprocess probes; retain the one prerequisite skip and four deprecation warnings as evidence.

## 4. Reconcile documentation and evidence

- [x] 4.1 Regenerate test, import, symbol, coverage, and prerequisite counts for all three repositories from the final source identities; update only owned README/AGENTS.md/SPEC_INDEX.md statements and preserve adapter-specific instruction surfaces.
- [x] 4.2 Add the corrective evidence ledger and final per-repository manifests to the owning planning/evidence location without editing archived OpenSpec history.
- [x] 4.3 Verify the tracked canonical .agents/skills/doc-sync/SKILL.md remains byte-stable and document the untracked root scaffold's ownership decision separately; do not populate or delete the scaffold without an identified owner.

## 5. Cross-repository verification and review

- [x] 5.1 Freeze the three implementation worktree commits and rerun all required gates against those exact commits, including dependency locks, format, Ruff, strict source-plus-test typing, full tests, coverage, secret scanning, CLI probes, and dirty-state fingerprints.
- [x] 5.2 Run focused strict OpenSpec validation for this change and full local-store validation; report unrelated active-change failures separately and never mark them fixed by this change. (349/350 pass; sole failure is unrelated align-jti-skill-runtime-contract)
- [x] 5.3 Run git diff --check, inspect every owned diff for accidental credentials/debug output/API changes, and obtain an independent review of test isolation and security-negative-path coverage.
- [x] 5.4 Confirm unavailable Docker, PostgreSQL, provider, scanner, deployed scheduler, and Graphify/GitNexus refresh prerequisites remain explicitly classified as blocked or unverified rather than converted into passing evidence.
- [x] 5.5 Review rollback by reverting each repository's test/documentation commit in a disposable worktree, confirm unrelated dirty paths and archived artifacts remain unchanged, and retain the rollback result. **Complete disposable-clone evidence:** Core rollback at detached `863715abdeb64ad98f0985bdd7d9a7b9d5d1b698`: (1) revert docs `d3b42af343e15a767780bdc565b2a79180f458f8` — clean; only AGENTS/README/SPEC_INDEX changed; 6 HTTP cases still pass; (2) revert DNS fixture `863715abdeb64ad98f0985bdd7d9a7b9d5d1b698` — clean; exactly **5** DNS-dependent cases fail while private-IP case passes; (3) revert provider fixture `3b17fb493e7dd440fca8c2767374854e9c2a05bc` — clean; full network-restricted result: 14 failed, 660 passed, 20 skipped (= 9 provider failures + 5 DNS failures). Kimi independently verified disposable docs-then-implementation rollbacks for harness and docs-sync: both sequences apply cleanly; harness restores 9 strict-mypy errors in 4 files, docs-sync restores 1 strict-mypy error, runtime tests remain green.

## Frozen Commits

| Repository | Implementation | Docs | Branch | Dirty | Integration |
|---|---|---|---|---|---|
| agent-core | `ca7d2fb5300557eee9278f95a66f7823c30d742c` | `d3b42af343e15a767780bdc565b2a79180f458f8` | restore-ecosystem-agent-core | 0 | Integrated to main |
| agent-harness | `d9ebe3e6e6ee660ee2fa8b433b5b93166490c482` | `bcb946da76723017f641f88b90547e1cf1a4892c` | main (fast-forwarded) | 4 (graphify-out, worktree clean) | Integrated by codex-1 |
| agent-docs-sync | `778aef09f2b6656b9c1968286d26f000fc885eff` | `ede62bdf9df8e7aa35a01b44fa4cc347b37e4959` | main | 5 (graphify-out, untracked scaffold) | Integrated |

## Evidence Summary

| Repo | Tests | Skipped | MyPy | Ruff | Coverage | Tool Versions |
|---|---|---|---|---|---|---|
| agent-core | 704 pass (host) / 684 pass + 20 skip (scanner unavail) | 0 (host) / 20 (restricted) | 176 files clean | clean | 85% | uv 0.12.3, Python 3.14.5, pytest 9.1.1, mypy 2.3.0, ruff 0.16.1 |
| agent-harness | 323 pass | 6 prereq | 85 files clean | clean | 89.27% | uv 0.12.3, Python 3.14.5, pytest 9.1.1, mypy 2.3.0, ruff 0.16.1 |
| agent-docs-sync | 206 pass (Docker avail) / 205 pass + 1 skip (Docker unavail) | 0 or 1 | 91 files clean | clean | N/A | uv 0.12.3, Python 3.14.5, pytest 9.1.1, mypy 2.3.0, ruff 0.16.1 |

**Cross-repo testing:** Consumer repos require `PYTHONPATH=/Users/androidteam/Developer/.worktrees/restore-ecosystem-agent-core/src` (pinned to core `ca7d2fb5300557eee9278f95a66f7823c30d742c`) to use frozen agent-core commit.

**OpenSpec change:** Committed and integrated into openspec workspace. Change is archive-ready pending owner authorization.
