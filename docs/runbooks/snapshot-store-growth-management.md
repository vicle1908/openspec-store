# Runbook: Snapshot Store Growth Measurement and Repack Management

## Overview
Workstation Git-backed snapshot stores (primarily `~/.agentmemory/snapshots`) record long-term agent state across sessions. Because snapshots are appended continuously without routine garbage collection, loose objects accumulate and can outweigh packed history by several orders of magnitude (measured baseline: ~9.7 GiB loose vs ~17 MiB packed).

## 1. Growth Bounds & Ceilings
The size ceiling and owner repack commands are declared in `config/snapshot-store-bounds.tsv`:
```tsv
# store_path	size_ceiling	owner_repack_command	owner_tool
~/.agentmemory/snapshots	1G	git -C ~/.agentmemory/snapshots -c pack.windowMemory=1g -c pack.threads=2 repack -a -d --window=10 --depth=10 && git -C ~/.agentmemory/snapshots prune-packed	agentmemory
```

## 2. Measurement Command
To measure snapshot growth, loose-vs-packed split, commit depth, and bounds evaluation:
```bash
python3 scripts/measure-snapshot-growth.py
```
For machine-readable JSON:
```bash
python3 scripts/measure-snapshot-growth.py --json
```

## 3. Repack Execution & Integrity Verification
Loose objects are bounded by repack, **never by direct filesystem deletion** (`rm -rf .git/objects` is strictly prohibited).

1. **Execute Owner Repack**:
   ```bash
   git -C ~/.agentmemory/snapshots -c pack.windowMemory=1g -c pack.threads=2 repack -a -d --window=10 --depth=10 && git -C ~/.agentmemory/snapshots prune-packed
   ```
2. **Prune Dereferenced Loose Objects**:
   ```bash
   git -C ~/.agentmemory/snapshots prune --expire=now
   ```
3. **Verify Integrity**:
   ```bash
   git -C ~/.agentmemory/snapshots log --oneline -1
   # Routine check (<1s):
   git -C ~/.agentmemory/snapshots fsck --connectivity-only
   # Repack maintenance window deep check:
   git -C ~/.agentmemory/snapshots fsck --no-dangling
   ```
4. **Verify Owning Tool Access**:
   Ensure `agentmemory` opens the store and retrieves the newest snapshot.
