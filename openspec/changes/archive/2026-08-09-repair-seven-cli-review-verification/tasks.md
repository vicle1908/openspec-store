# Tasks: Repair Seven-CLI Review Verification

## 1. Ground truth and repair design
- [x] 1.1 Create the superseding repair change before further verification.
- [x] 1.2 Document defects in the archived verification and define honest classifications.
- [x] 1.3 Establish the Git-tracked `.hermes/skills/` tree as the canonical managed source.
- [x] 1.4 Record current versions and accepted noninteractive flags for all seven CLIs.

## 2. Durable verification harness
- [x] 2.1 Add a persistent compact review fixture under `verification/`.
- [x] 2.2 Add a runner that captures true exit status, separate streams, duration, version, executable identity, hashes, and output sizes.
- [x] 2.3 Add a parser that requires a recognized verdict and substantive review content.
- [x] 2.4 Add durable operating and evidence documentation.

## 3. Round 1 diagnosis
- [x] 3.1 Run Claude, Agy, and Goose concurrently.
- [x] 3.2 Run OpenCode, Codex, and Kimi concurrently.
- [x] 3.3 Run Pi serially.
- [x] 3.4 Consolidate all seven results without deleting the fixture or raw evidence.
- [x] 3.5 Diagnose every non-passing status.

## 4. Skills and configuration repair
- [x] 4.1 Remove incorrect Kimi/model-alias executable references from current operational guides.
- [x] 4.2 Correct masked-exit, premature-timeout, pending, and false-completion guidance.
- [x] 4.3 Update coding-agent and review guides with verified default-model invocations and result checks.
- [x] 4.4 Switch Pi MCP exposure from 77 direct tools to proxy mode without changing provider/model.
- [x] 4.5 Add Pi lifecycle-only flags for bounded no-tool reviews and verify a clean exit.
- [x] 4.6 Synchronize installed copies from the canonical source and retain checksum evidence.
- [x] 4.7 Add an explicit erratum superseding the inaccurate archived conclusions.

## 5. Final verification
- [x] 5.1 Rebuild the fixture after remediation.
- [x] 5.2 Run full Round 6: seven smoke PASS and seven accepted reviews, all return code 0.
- [x] 5.3 Run consecutive full Round 7 with identical fixture and runner hashes.
- [x] 5.4 Verify Round 7: seven smoke PASS and seven accepted reviews, all return code 0.
- [x] 5.5 Reconcile summaries, raw evidence, tasks, canonical guides, and installed checksums.
- [x] 5.6 Run focused and full OpenSpec validation; report unrelated baseline failures separately.
- [x] 5.7 Prepare the validated change for integration and archive.

## Completion evidence
- Round 6 fixture SHA-256: `a5a8551417c662a4dfda064bd885d5cfd1d1729c3daa08685b1e2f50cc45b472`
- Round 7 fixture SHA-256: `a5a8551417c662a4dfda064bd885d5cfd1d1729c3daa08685b1e2f50cc45b472`
- Round 6/7 runner SHA-256: `c59819c09dd99ef37ffb22f95dfaa2657bbd038dc1be63a6c5fbefd59f973793`
- Canonical and installed managed skill copies: checksum-matched.
- Pi provider/model overrides: none.
- Current stale operational references (`fable-5 -p`, false timeouts/pending/EXIT:0): zero in the canonical managed source.
- Focused validation: valid.
- Full-store validation: 346 passed, 1 unrelated pre-existing failure (`align-jti-skill-runtime-contract`).
- Final Round 6/7 findings: dispositioned in `verification/final-findings-disposition.md`; no finding requires changing the verified runner, fixture, Pi setup, or canonical skills.
