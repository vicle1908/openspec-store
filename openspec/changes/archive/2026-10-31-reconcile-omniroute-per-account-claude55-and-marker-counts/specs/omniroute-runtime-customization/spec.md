# Spec Delta: omniroute-runtime-customization

## MODIFIED Requirements

### Requirement: Compatibility Behavior and Patch Retirement Gates
The compatibility ledger SHALL map each local modification in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`3` non-chunk patches and `48` chunk/route replacements = `51` modifications) to its behavior, affected versions, `60` fail-closed markers (`3` non-chunk and `57` chunk markers across `24` compiled files), upstream status, and removal gate. Marker checks SHALL fail closed when any target file is missing or renamed.

#### Scenario: Retiring one upstreamed fix
- **WHEN** a validated upstream release supplies a replacement for a local modification
- **THEN** only that modification SHALL become eligible for retirement after its behavior passes verification, and unrelated modifications SHALL remain accounted for.

#### Scenario: Missing required compatibility state
- **WHEN** a candidate deployment cannot demonstrate a required compatibility condition or a target chunk or server file for any of the 60 required markers (`3` non-chunk and `57` chunk markers across `24` compiled files) is absent or renamed
- **THEN** `/app/container-entrypoint-compat.sh` SHALL fail closed with `[COMPAT_ERROR]` and exit `1` rather than silently skipping verification, and SHALL NOT promote the deployment as compatible.
