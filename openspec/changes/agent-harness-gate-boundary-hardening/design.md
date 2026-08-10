# Design: agent-harness-gate-boundary-hardening

## 1. Symlink validation fix

### Current behavior (broken)

```python
def validate_artifact_root(artifact_root: str) -> Path:
    expanded = Path(os.path.expandvars(artifact_root)).expanduser().resolve()
    for index in range(1, len(expanded.parts) + 1):
        candidate = Path(*expanded.parts[:index])
        if candidate.exists() and candidate.is_symlink():
            raise ValueError(...)
    return expanded
```

`resolve()` on macOS converts `/var` to `/private/var` before the scan, so the symlink at `/var` is invisible.

### Proposed fix

```python
def validate_artifact_root(artifact_root: str) -> Path:
    expanded = Path(os.path.expandvars(artifact_root)).expanduser()
    if not expanded.is_absolute():
        raise ValueError(f"Artifact root must be absolute: {artifact_root}")
    # Scan BEFORE resolve — detects user-supplied symlinks
    for index in range(1, len(expanded.parts) + 1):
        candidate = Path(*expanded.parts[:index])
        if candidate.exists() and candidate.is_symlink():
            raise ValueError(f"Artifact root contains symlink component: {candidate}")
    return expanded.resolve()
```

### Platform-safe policy

Reject ALL symlinks in the expanded path, including platform aliases. This means:
- `/var/tmp/artifacts` IS rejected (`/var` is a symlink to `/private/var` on macOS)
- `/private/var/tmp/artifacts` is accepted (no symlinks in this path)

This is a strict security policy: callers must use canonical paths. The removed macOS test `test_validate_artifact_root_allows_platform_symlink_ancestor` confirms this is intentional.

### TOCTOU caveat

A symlink could be created between the component scan and the `resolve()` call. This is a best-effort defense. For production use, artifact stores should use descriptor-relative operations. Document this limitation.

## 2. GraphifyTool containment

`GraphifyTool._load()` calls `Path(self.graph_path).resolve()` before containment check. Since the tool is read-only on pre-generated artifacts, containment-after-resolve is an accepted bounded residual risk. Add tests for edge cases (missing file, oversized, malformed JSON, outside roots) and document the TOCTOU caveat.

## 3. Authorization tests

`ConfigFileResolver` already fails closed. Add tests proving:
1. `unavailable_gate_resolver()` rejects even with valid assertion
2. `unavailable_gate_resolver()` ignores environment identity
3. Separation of duties is enforced (initiator cannot approve own gate)

## 4. Generated artifact cleanup

`.graphify_labels.json` and `.graphify_labels.json.sig` are regenerable with no consumers. Remove from tracking, add to `.gitignore`.
