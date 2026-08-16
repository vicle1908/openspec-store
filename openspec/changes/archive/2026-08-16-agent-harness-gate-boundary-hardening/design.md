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


## 5. Authority invariant enforcement

### Current behavior (misleading)

```python
class AuthorityConfig(BaseModel):
    allowed_shell: bool = Field(default=False, description="Must remain False")
    allowed_code_execution: bool = Field(default=False, description="Must remain False")
    allowed_external_mutation: bool = Field(default=False, description="Must remain False")
    allowed_source_write: bool = Field(default=False, description="Must remain False")
    model_config = {"extra": "forbid"}
```

The `description` says "Must remain False" but Pydantic's `Field(default=...)` only sets the default value — it does not constrain the type. Construction with `True`, `1`, `"true"`, or `"1"` succeeds silently. Nested YAML overlays containing truthy values also pass validation.

### Proposed fix

```python
from typing import Literal
from pydantic import ConfigDict

class AuthorityConfig(BaseModel):
    allowed_shell: Literal[False] = False
    allowed_code_execution: Literal[False] = False
    allowed_external_mutation: Literal[False] = False
    allowed_source_write: Literal[False] = False

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
```

`Literal[False]` restricts the accepted value to only `False`. Pydantic rejects `True`, `1`, `"true"`, `"1"`, and any other coercion candidate. `validate_assignment=True` also blocks post-construction reassignment.

### Jira/GitLab structural boundaries (not config fields)

Jira mutation prevention is enforced structurally by `JiraTool` exposing only `get_ticket`, `search`, `get_links`. GitLab has no mutation implementation. These are code-design guarantees — adding unused `allowed_jira_mutation` fields would provide misleading false assurance.

### Implementation plan

1. Add parametrized RED tests in `tests/test_authority.py` covering all four fields, nested `HarnessConfig`, coercion rejection, assignment rejection.
2. Implement `Literal[False]` and `validate_assignment=True` in `AuthorityConfig`.
3. Verify all four fields reject coercion candidates: `True`, `1`, `"true"`, `"1"`.
4. Verify `False` remains accepted.
5. Verify post-construction assignment raises `ValidationError`.

## 6. Stage composition authority boundary

`StageCompositionContext` is a public harness composition boundary. The harness currently exposes only read-only toolsets and must not accept caller-supplied high-authority capability policy. Its `__post_init__` SHALL reject any non-empty filesystem, shell, network, runtime-authoring, or grant allowlist and SHALL reject disabled audit mode. The default empty policy remains valid. This is a harness-owned deny-only boundary; agent-core remains responsible for general capability-policy validation for consumers that explicitly opt into high-authority capabilities.
