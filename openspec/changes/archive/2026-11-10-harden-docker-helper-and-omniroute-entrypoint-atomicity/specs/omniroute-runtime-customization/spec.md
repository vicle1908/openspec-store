# omniroute-runtime-customization Delta Specification

## MODIFIED Requirements

### Requirement: Compatibility Behavior and Patch Retirement Gates
The compatibility ledger SHALL map each local modification in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`3` non-chunk patches and `7` chunk replacements = `10` modifications in `v3.8.53+`) to its behavior, `15` fail-closed markers across `6` server chunks, and removal gate. Modifications SHALL use atomic sibling temp-file renames (`fs.renameSync`), `ensure-muse-wire-compat.sh` SHALL wait for PID 1 entrypoint completion, and missing markers SHALL fail closed.

#### Scenario: Retiring one upstreamed fix
- **WHEN** a validated upstream release supplies a replacement for a local modification
- **THEN** only that modification SHALL become eligible for retirement after its behavior passes verification, and unrelated modifications SHALL remain accounted for.

#### Scenario: Missing required compatibility state
- **WHEN** a candidate deployment cannot demonstrate a required compatibility condition or a target chunk or server file for any of the 15 required markers (`3` non-chunk and `12` chunk markers across `6` compiled server chunk files) is absent or renamed
- **THEN** `/app/container-entrypoint-compat.sh` SHALL fail closed with `[COMPAT_ERROR]` and exit `1` rather than silently skipping verification, and SHALL NOT promote the deployment as compatible.

#### Scenario: Atomic compatibility file writes and entrypoint readiness serialization
- **WHEN** `/app/container-entrypoint-compat.sh` patches `/app/peer-stamp.mjs`, Next.js server route files, or server chunks, or when `~/Omniroute/scripts/ensure-muse-wire-compat.sh` verifies container runtime patches after `docker compose up -d`
- **THEN** `/app/container-entrypoint-compat.sh` SHALL write modified contents via `atomicWriteFileSync` (sibling `.tmp-<pid>-<ts>` write followed by `fs.renameSync`) so interruption or concurrent inspection can never leave a 0-byte truncated file in the container writable layer
- **AND** `ensure-muse-wire-compat.sh` SHALL poll up to 15 seconds until no `container-entrypoint-compat.sh` process is running inside the container before invoking `/app/container-entrypoint-compat.sh --patch-only`.
