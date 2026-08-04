# Tasks: TDT Home Source Conformance

Each task is one focused work session with a verification gate. Dependency on
`govern-tdt-home-config-and-environment` (provider foundation) is complete.

## 1. Manifest schema and tooling

- [x] 1.1 Define the strict `RepositoryManifest` schema aligned with `source_registry.py` validation: contract identity (`schema_version`, `audit_contract_version`), participant identity and role, owning team, repository-relative source and deployment-definition scope, explicit library/deployable classification, deployment owners/principals, and repository-owned exceptions, while preserving the existing operations/deployment-owners compatibility fields.
- [x] 1.2 Create the `tdt config create-manifest` CLI command that emits a `.tdt/governance-manifest.json` scaffold to stdout by default or to an explicitly requested new output path; it MUST never overwrite an existing manifest or implicitly write a consumer repository.
- [x] 1.3 Add validation that manifest JSON passes duplicate-key rejection, strict schema/path/ownership/exception constraints, and matches the registered participant identity and role in the provider registry.

## 2. Consumer manifests

- [x] 2.1 Publish the manifest schema, scaffold, and per-participant checklist;
  do not write consumer repository files from the provider-owned change.
- [ ] 2.2 Review owner-supplied manifests for each of the 15 registered
  consumer repositories and verify repository, role, identity marker, scope,
  deployment ownership, and exception invariants against the provider registry.
- [ ] 2.3 Require each consumer repository to commit its own manifest and
  retain an immutable revision-bound evidence envelope; aggregate only those
  owner-supplied artifacts.

## 3. Source audit tooling

- [x] 3.1 Implement `tdt config source-audit <workspace-root>` that scans registered repositories for hard-coded `~/.tdt` construction outside approved sites.
- [x] 3.2 Add structure-aware parser adapters for each supported executable
  language; unsupported executable surfaces produce unresolved findings and
  cannot receive verified-green status from regex matching.
- [x] 3.3 Output deterministic structured JSON and human-readable text with
  `PASS`, `PASS_WITH_EXCEPTIONS`, and `FAIL` scopes plus redacted rule findings.
- [x] 3.4 Add strict mode that exits non-zero on any error-level finding.

## 4. Repository-owned exceptions

- [x] 4.1 Define the exception format for repository-owned legacy sites (file path, pattern, reason, expiry date) inside `.tdt/governance-manifest.json`.
- [x] 4.2 Integrate exception evaluation into the source audit pipeline so approved patterns are reported as info rather than error.
- [x] 4.3 Verify exception entries cannot bypass new approved-site checks.

## 5. Verification and documentation

- [x] 5.1 Run the source audit against immutable, owner-supplied revisions for
  all 15 repositories and record clean, excepted, failed, and unknown results.
- [x] 5.2 Document the conformance process for new repositories joining the ecosystem.
- [x] 5.3 Run `openspec validate --all --strict` and `openspec store doctor`.

## Archive gate

Do not archive until every consumer-owned manifest and evidence envelope is
reviewed, supported executable surfaces are parsed or explicitly unresolved,
exceptions are bounded and expiring, and all verification passes. This change
does not rewrite consumer source or dependency metadata.

## Evidence boundary

The provider-owned schema, scaffold, parser audit, deterministic report, and
exception policy are implemented and verified in the dedicated `tdt-core`
worktree. Tasks 2.2, 2.3, and 5.1 intentionally remain open: no owner-supplied
consumer manifests or immutable evidence envelopes are present in the current
workspace, so the provider must not invent those facts or mark the aggregate
ready. The live workspace audit reports the 15 registered participants as
missing manifests until each consumer repository contributes its own governed
file and revision-bound report.
