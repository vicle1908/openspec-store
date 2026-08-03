# Design: TDT_HOME Source Conformance

## Context

The provider foundation establishes the runtime boundary, but consumers own
their imports, path construction, deployment manifests, and compatibility
adapters. A source audit must report those facts without silently taking over
consumer repositories or converting an incomplete inventory into a green
rollout decision.

## Decisions

### Decision 1: Audit syntax and ownership separately

The AST phase identifies direct `~/.tdt` literals, `Path.home()` composition,
ad-hoc dotenv/config/credential reads, and calls that bypass the approved
provider API. It emits file, line, rule id, and confidence only. The ownership
phase reads a participant's value-free manifest and does not infer deployment
facts from source syntax.

### Decision 2: Exceptions are repository-owned and bounded

An exception names the repository, rule, file/symbol scope, reason, owner,
approval reference, and expiry. It cannot contain a secret or suppress a
provider security rule globally. Expired, duplicate, or scope-mismatched
exceptions remain findings.

### Decision 3: Manifests are identity-bound

Each manifest declares the repository identity marker, participant role,
provider version floor, approved import surface, deployment writer/reader
attestation status, and exception list. The audit rejects missing, malformed,
duplicate, or identity-mismatched manifests. It reports “unknown” when a
principal or deployment fact has not been directly attested.

### Decision 4: Reports are deterministic and redacted

Reports sort by repository, path, line, and rule id; use stable relative paths;
and contain no environment values, DSNs, credentials, arbitrary file contents,
or unbounded command output. A strict mode returns non-zero for unresolved
findings, expired exceptions, missing manifests, or unknown required facts.

### Decision 5: Audit is read-only

The audit never writes a source file, deployment manifest, exception file, or
live runtime root. Remediation and adoption are separate changes owned by the
affected repository.

## Evidence Gates

- Rule fixtures cover positive findings, approved provider calls, generated/
  vendor/test boundaries, and ambiguous syntax.
- Manifest fixtures cover missing, malformed, duplicate, expired, and
  identity-mismatched entries.
- A cross-repository report proves deterministic ordering and redaction.
- At least one negative test proves audit execution leaves the target tree
  byte-for-byte unchanged.
- Strict OpenSpec, lint, typing, and secret scans pass before archive.

## Rollback

Removing the audit implementation or restoring its prior artifact has no
consumer or runtime effect because the tool is read-only and does not own
exception or manifest files.
