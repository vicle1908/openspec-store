# snapshot-store-growth-bounds Specification Delta

## ADDED Requirements

### Requirement: Primary DBOS maintenance workflow evaluates and alerts on snapshot growth bounds

The scheduled DBOS workflow (`shb-schedule` `workstation_update.py`) SHALL invoke `measure-snapshot-growth.py` during daily `apply` execution so any breach of the 1 GiB ceiling on `~/.agentmemory/snapshots` is recorded in `~/Developer/data/updates/YYYY-MM-DD.json` and triggers a degradation alert rather than being bypassed when `workstation-daily-update.sh` delegates to DBOS.

#### Scenario: Snapshot ceiling breach is surfaced during daily DBOS run
- **WHEN** `workstation_update.py` executes and `measure-snapshot-growth.py` reports `Status: EXCEEDED` (such as 11.62 GiB on disk against a 1 GiB ceiling)
- **THEN** the DBOS step SHALL record the loose-versus-packed object split and commit count in the daily JSON telemetry report
- **AND** the run SHALL be marked degraded so the operator is notified

#### Scenario: Non-destructive Git repack reclaims loose snapshot objects
- **WHEN** `~/.agentmemory/snapshots` exceeds its 1 GiB ceiling due to loose Git objects (e.g., 1,764 loose objects totaling 11.60 GiB vs 17.41 MiB packed)
- **THEN** executing `git -C ~/.agentmemory/snapshots -c pack.windowMemory=1g -c pack.threads=2 repack -a -d --window=10 --depth=10` and `git prune-packed` SHALL consolidate loose objects into packfiles without reducing commit history depth
- **AND** post-repack `measure-snapshot-growth.py` SHALL report total size below the 1 GiB ceiling with `git fsck` and `HEAD` commit readability intact

#### Scenario: Fast connectivity-only fsck is used for routine checks while full fsck bounds repack windows
- **WHEN** routine daily snapshot store integrity is verified on a packed multi-thousand-object repository
- **THEN** routine checks SHALL invoke `git -C ~/.agentmemory/snapshots fsck --connectivity-only` to verify commit/tree/blob graph connectivity without re-inflating every packed blob
- **AND** full `git -C ~/.agentmemory/snapshots fsck --no-dangling` SHALL be reserved for pre- and post-repack maintenance windows
