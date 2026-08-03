# Tasks: TDT Home Source Conformance

Each task is one focused work session with a verification gate. Dependency on
`govern-tdt-home-config-and-environment` (provider foundation) is complete.

## 1. Manifest schema and tooling

- [ ] 1.1 Define the `RepositoryManifest` schema (schema_version, repository, role, operations, deployment_owners) aligned with `source_registry.py` validation.
- [ ] 1.2 Create the `tdt config create-manifest` CLI command that generates a `.tdt/governance-manifest.json` scaffold for a given repository.
- [ ] 1.3 Add validation that manifest JSON passes duplicate-key rejection, schema constraints, and matches the registered participant in the provider registry.

## 2. Consumer manifests

- [ ] 2.1 Create `.tdt/governance-manifest.json` for each of the 15 registered consumer repositories (excluding `tdt-core` which is the provider).
- [ ] 2.2 Verify each manifest matches the provider registry participant entry (repository name, role, identity_marker).
- [ ] 2.3 Commit all manifests as a single atomic change per repository or as a coordinated workspace commit.

## 3. Source audit tooling

- [ ] 3.1 Implement `tdt config source-audit <workspace-root>` that scans registered repositories for hard-coded `~/.tdt` construction outside approved sites.
- [ ] 3.2 Support both AST-based (Python `ast.parse`) and regex-based detection for non-Python files.
- [ ] 3.3 Output findings as structured JSON or human-readable text with severity levels (error for approved-site violations, warning for legacy patterns).
- [ ] 3.4 Add strict mode that exits non-zero on any error-level finding.

## 4. Drift allowlist

- [ ] 4.1 Define an allowlist format for approved legacy sites (file path, pattern, reason, expiry date).
- [ ] 4.2 Integrate allowlist evaluation into the source audit pipeline so approved patterns are reported as info rather than error.
- [ ] 4.3 Verify allowlist entries cannot bypass new approved-site checks.

## 5. Verification and documentation

- [ ] 5.1 Run source audit across all 15 repositories and record baseline findings.
- [ ] 5.2 Document the conformance process for new repositories joining the ecosystem.
- [ ] 5.3 Run `openspec validate --all --strict` and `openspec store doctor`.

## Archive gate

Do not archive until all consumer manifests are committed, source audit produces
clean baseline, allowlist is documented, and all verification passes.
