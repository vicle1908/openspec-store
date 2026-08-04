# Tasks: TDT Home Source Conformance

Each task is one focused work session with a verification gate. Dependency on
`govern-tdt-home-config-and-environment` (provider foundation) is complete.

## 1. Manifest schema and tooling

- [ ] 1.1 Define the `RepositoryManifest` schema (schema_version, repository, role, operations, deployment_owners) aligned with `source_registry.py` validation.
- [ ] 1.2 Create the `tdt config create-manifest` CLI command that generates a `.tdt/governance-manifest.json` scaffold for a given repository.
- [ ] 1.3 Add validation that manifest JSON passes duplicate-key rejection, schema constraints, and matches the registered participant in the provider registry.

## 2. Consumer manifests

- [ ] 2.1 Publish the manifest schema, scaffold, and per-participant checklist;
  do not write consumer repository files from the provider-owned change.
- [ ] 2.2 Review owner-supplied manifests for each of the 15 registered
  consumer repositories and verify repository, role, identity marker, scope,
  deployment ownership, and exception invariants against the provider registry.
- [ ] 2.3 Require each consumer repository to commit its own manifest and
  retain an immutable revision-bound evidence envelope; aggregate only those
  owner-supplied artifacts.

## 3. Source audit tooling

- [ ] 3.1 Implement `tdt config source-audit <workspace-root>` that scans registered repositories for hard-coded `~/.tdt` construction outside approved sites.
- [ ] 3.2 Add structure-aware parser adapters for each supported executable
  language; unsupported executable surfaces produce unresolved findings and
  cannot receive verified-green status from regex matching.
- [ ] 3.3 Output deterministic structured JSON and human-readable text with
  `PASS`, `PASS_WITH_EXCEPTIONS`, and `FAIL` scopes plus redacted rule findings.
- [ ] 3.4 Add strict mode that exits non-zero on any error-level finding.

## 4. Repository-owned exceptions

- [ ] 4.1 Define the exception format for repository-owned legacy sites (file path, pattern, reason, expiry date) inside `.tdt/governance-manifest.json`.
- [ ] 4.2 Integrate exception evaluation into the source audit pipeline so approved patterns are reported as info rather than error.
- [ ] 4.3 Verify exception entries cannot bypass new approved-site checks.

## 5. Verification and documentation

- [ ] 5.1 Run the source audit against immutable, owner-supplied revisions for
  all 15 repositories and record clean, excepted, failed, and unknown results.
- [ ] 5.2 Document the conformance process for new repositories joining the ecosystem.
- [ ] 5.3 Run `openspec validate --all --strict` and `openspec store doctor`.

## Archive gate

Do not archive until every consumer-owned manifest and evidence envelope is
reviewed, supported executable surfaces are parsed or explicitly unresolved,
exceptions are bounded and expiring, and all verification passes. This change
does not rewrite consumer source or dependency metadata.
