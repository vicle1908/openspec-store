# workstation-remote-and-agent-permissions Spec Delta

## ADDED Requirements

### Requirement: TCC provenance verifier SHALL maintain unified target resolution without dead tables or duplicated error payloads

The TCC provenance verifier SHALL resolve explicit and default target lists through a unified resolution pipeline without dead role tables or duplicated error-result literals while preserving all native `Security.framework` `csreq` checks and public return keys.

#### Scenario: Default and explicit binary sets execute through a single target-resolution loop
- **WHEN** `build_required_targets()` is invoked with `binaries=None` or with an explicit `binaries` list
- **THEN** both paths SHALL resolve canonical CLIs and shared Python automation identities through one shared loop without duplicate branch logic
- **AND** `verify_tcc_provenance()` SHALL return `status: "CLEAN"` across all 9 workstation identities when all required services and `csreq` signatures are valid

#### Scenario: Error and drift results preserve public contract keys via shared constructor
- **WHEN** `verify_tcc_provenance()` encounters non-Darwin skip, missing/unreadable `TCC.db`, empty target list, or helper failure
- **THEN** the returned dictionary SHALL contain `status`, `reason`, `verified_binaries`, `missing_binaries`, `records`, and `errors` constructed via a single helper function
