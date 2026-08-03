## 1. Audit contract

- [ ] 1.1 Record the provider registry version, participant inventory, source
  roots, and explicit generated/vendor/test scan policy.
- [ ] 1.2 Define AST rule ids, approved provider entry points, confidence
  classes, and stable relative-path evidence.
- [ ] 1.3 Define the value-free participant manifest and exception schemas.

## 2. Read-only implementation

- [ ] 2.1 Implement AST detection for hard-coded roots and provider-boundary
  bypasses without evaluating application code.
- [ ] 2.2 Implement manifest identity, role, version-floor, and required-field
  validation against the packaged participant registry.
- [ ] 2.3 Implement bounded exception matching with owner, approval, and expiry
  checks; security rules cannot be suppressed.
- [ ] 2.4 Implement deterministic text/JSON reports with redacted findings and
  strict exit semantics.

## 3. Verification and adoption handoff

- [ ] 3.1 Add rule fixtures for compliant, violating, ambiguous, and excluded
  source forms.
- [ ] 3.2 Add manifest/exception fixtures for missing, malformed, duplicate,
  expired, and identity-mismatched cases.
- [ ] 3.3 Prove audit repeatability, redaction, and byte-for-byte read-only
  behavior across all fixtures.
- [ ] 3.4 Produce one evidence report per participant; keep remediation in the
  participant-owned successor change.

## 4. Release evidence

- [ ] 4.1 Run focused tests, full provider gates, strict typing/lint/format, and
  added-lines secret scanning.
- [ ] 4.2 Run strict OpenSpec validation and classify every participant result
  as compliant, excepted, unresolved, or unknown.
- [ ] 4.3 Do not modify consumer source, deployment state, or live `~/.tdt`; the
  audit is not a cutover approval by itself.
