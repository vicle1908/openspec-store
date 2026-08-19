## Tasks

### 1. Fix test_docker_local_dev.py
- [x] Remove `postgres-backup` from service list in `test_compose_uses_current_pinned_images`
- [x] Skip or remove `test_scheduler_dockerfile_installs_ripgrep` (file doesn't exist)

### 2. Fix test_governance_manifest.py
- [x] Update expected service set to match current compose.yaml
- [x] Update governance manifest if needed

### 3. Fix test_dependency_integrity_gate.py
- [x] Skip tests if `deployments/scheduler/` doesn't exist

### 4. Update governance manifest
- [x] Remove references to non-existent files in `.tdt/governance-manifest.json`

### 5. Verify fixes
- [x] Run all fixed tests to confirm they pass (31 passed, 12 skipped, 0 failed)
- [x] Run full test suite to confirm no regressions
