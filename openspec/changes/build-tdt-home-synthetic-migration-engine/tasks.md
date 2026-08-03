## 1. Baseline and contract

- [ ] 1.1 Record the provider commit, package version, security-kernel
  capability snapshot, and the exact non-live execution boundary.
- [ ] 1.2 Define the typed value-free plan schema and reject unsafe paths,
  duplicate destinations, root mismatches, and literal secrets.
- [ ] 1.3 Define the journal header, record hash, legal state transitions, and
  redacted evidence format.

## 2. Engine implementation

- [ ] 2.1 Implement plan preparation against retained provider root anchors.
- [ ] 2.2 Implement descriptor-relative staging, synchronization, replacement,
  and post-operation identity verification.
- [ ] 2.3 Implement legal apply, recover, and rollback state transitions.
- [ ] 2.4 Reject unavailable platform capabilities and unsafe journal/object
  identities before mutation.

## 3. Recovery and synthetic verification

- [ ] 3.1 Implement complete-journal validation and tamper/truncation failure.
- [ ] 3.2 Add idempotent replay tests for applied, recovered, and rolled-back
  terminal states.
- [ ] 3.3 Add deterministic fault injection before and after every transaction
  boundary using only temporary, value-free fixtures.
- [ ] 3.4 Verify staging cleanup, descriptor cleanup, containment, and secret
  redaction after every synthetic interruption.

## 4. Release evidence

- [ ] 4.1 Run focused tests, full provider tests, Ruff, strict mypy, and the
  added-lines secret/redaction scan.
- [ ] 4.2 Record the requirement/scenario-to-test/source evidence matrix.
- [ ] 4.3 Run strict OpenSpec validation and preserve the clean worktree
  fingerprint.
- [ ] 4.4 Keep live `~/.tdt`, consumer repositories, deployment state, and
  external databases unchanged; archive only after all evidence is complete.
