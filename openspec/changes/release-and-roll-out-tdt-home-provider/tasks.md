## 1. Release candidate

- [ ] 1.1 Record provider source HEAD, distribution version, wheel hash, lock
  closure, build tool identity, and clean artifact inventory.
- [ ] 1.2 Build and install the candidate in a fresh environment with no
  checkout and no `PYTHONPATH`.
- [ ] 1.3 Run base CLI, packaged-resource, doctor, contract, version-equality,
  lint, type, and secret/redaction gates.

## 2. Staging gate

- [ ] 2.1 Identify the disposable/staging target, package source, configuration
  owner, writer principal, and health endpoint.
- [ ] 2.2 Install the immutable candidate and record provider-only startup and
  redacted health evidence.
- [ ] 2.3 Verify staging does not open or mutate the real `~/.tdt`, consumer
  repositories, databases, or deployment state.

## 3. Approval and rollback

- [ ] 3.1 Define the approval record and explicit distinction between provider,
  consumer, deployment, and live-root readiness.
- [ ] 3.2 Retain the exact pre-change artifact and execute a rollback rehearsal
  in staging, or record an explicitly approved bounded deferral.
- [ ] 3.3 Record failure handling, operator escalation, and evidence retention
  without exposing credentials or raw configuration.

## 4. Final validation

- [ ] 4.1 Run strict OpenSpec validation and provider/release repository gates.
- [ ] 4.2 Recheck the release worktree and classify all dirty paths as owned or
  unrelated before any archive or deployment action.
- [ ] 4.3 Leave consumer adoption, deployment restart, and live-root cutover
  unchecked until their successor changes supply evidence.
