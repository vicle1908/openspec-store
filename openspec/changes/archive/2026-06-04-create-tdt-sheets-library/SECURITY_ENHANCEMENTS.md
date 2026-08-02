# Security Enhancements for tdt-sheets

**Date**: 2026-06-03  
**Status**: Proposed enhancements to OpenSpec  
**Priority**: MEDIUM (security hardening, not blocking for v0.1.0)

---

## Overview

Based on authentication analysis of 4 existing implementations, these security enhancements should be added to the tdt-sheets library to improve credential handling, cache management, and operational security.

---

## 1. File Permission Validation

### Problem
Service account JSON files may be world-readable (permissions 644 or 666), exposing private keys to all system users.

### Current State
No implementations validate file permissions before reading credentials.

### Proposed Solution

```python
# tdt_sheets/auth.py

import stat
from pathlib import Path

def _validate_file_permissions(path: Path) -> None:
    """Warn if service account JSON has unsafe permissions.
    
    Checks for world-readable or world-writable permissions.
    Does not fail (graceful degradation) but logs warning.
    """
    mode = path.stat().st_mode
    
    # Check if world-readable (o+r) or world-writable (o+w)
    if mode & (stat.S_IROTH | stat.S_IWOTH):
        logger.warning(
            "service_account_insecure_permissions",
            extra={
                "path": str(path),
                "mode": oct(mode)[-3:],
                "recommendation": "chmod 600"
            }
        )
```

**When to call**: In `ServiceAccountAuth.from_env()` after resolving path, before loading credentials.

**Severity**: WARNING (not error) — allows operation but alerts operator.

---

## 2. Cache Invalidation on File Modification

### Problem
If service account JSON is rotated (replaced), cached credentials remain stale until service restart. This can cause:
- Old credentials used after rotation
- Unable to test new credentials without restart
- Silent failures if old credentials revoked

### Current State
Cache key is file path only: `str(credentials_path)`

### Proposed Solution

```python
# tdt_sheets/auth.py

def _credentials_cache_key(path: Path) -> str:
    """Generate cache key including file modification time.
    
    If file is modified (e.g., credential rotation), cache is invalidated
    automatically without requiring service restart.
    """
    mtime = path.stat().st_mtime
    return f"{path}:{mtime}"
```

**Benefits**:
- Automatic cache invalidation on credential rotation
- No service restart required
- Testable credential updates

**Trade-offs**:
- Additional `stat()` syscall on each auth request (negligible performance impact)
- Cache miss on every file touch (even if content unchanged)

**Recommendation**: Implement for v0.1.0 — improves operational safety significantly.

---

## 3. Credential JSON Structure Validation

### Problem
If service account JSON is corrupted, incomplete, or invalid, authentication fails with cryptic error messages from google-auth internals.

### Current State
No validation — passes file directly to `service_account.Credentials.from_service_account_file()`.

### Proposed Solution

```python
# tdt_sheets/auth.py

import json

REQUIRED_SA_FIELDS = {
    "type",
    "project_id", 
    "private_key_id",
    "private_key",
    "client_email",
    "client_id",
    "auth_uri",
    "token_uri"
}

def _validate_service_account_json(path: Path) -> None:
    """Validate service account JSON structure before auth.
    
    Raises:
        ValueError: If JSON is invalid or missing required fields.
    """
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in service account file: {exc}") from exc
    
    if not isinstance(data, dict):
        raise ValueError("Service account JSON must be an object")
    
    missing = REQUIRED_SA_FIELDS - set(data.keys())
    if missing:
        raise ValueError(f"Service account JSON missing fields: {missing}")
    
    if data.get("type") != "service_account":
        raise ValueError(f"Expected type='service_account', got '{data.get('type')}'")
```

**When to call**: In `ServiceAccountAuth.from_env()` after resolving path, before loading credentials.

**Benefits**:
- Clear error messages for invalid credentials
- Fast-fail on configuration errors
- Easier troubleshooting for operators

**Trade-offs**:
- Additional file read (mitigated by subsequent caching)
- Duplicate JSON parsing (once for validation, once by google-auth)

**Recommendation**: Implement for v0.1.0 — significantly improves developer experience.

---

## 4. Configurable Scopes

### Problem
Different projects need different API scopes:
- jira-epic-report: `spreadsheets` + `drive` (creates folders)
- jira-daily-reports: `spreadsheets` + `drive` (shares files)
- android-scan-agent: `spreadsheets` only (write-only)

Hard-coding scopes prevents fine-grained permission control.

### Current State (OpenSpec)
```python
_SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
```

### Proposed Solution

```python
# tdt_sheets/auth.py

from typing import Sequence

DEFAULT_SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
)

class ServiceAccountAuth:
    """Google service account authentication for Sheets API."""
    
    def __init__(
        self,
        credentials_path: Path,
        scopes: Sequence[str] | None = None,
    ):
        self.credentials_path = credentials_path
        self.scopes = tuple(scopes) if scopes else DEFAULT_SCOPES
        self._credentials = None
    
    @classmethod
    def from_env(
        cls,
        scopes: Sequence[str] | None = None,
    ) -> ServiceAccountAuth:
        """Create auth from environment variables.
        
        Args:
            scopes: API scopes (default: spreadsheets + drive).
        
        Returns:
            ServiceAccountAuth instance.
        
        Raises:
            ValueError: If no credentials found.
        """
        path = cls._resolve_credentials_path()
        return cls(credentials_path=path, scopes=scopes)
```

**Usage**:
```python
# android-scan-agent: spreadsheets only
auth = ServiceAccountAuth.from_env(
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

# jira-epic-report: default (spreadsheets + drive)
auth = ServiceAccountAuth.from_env()
```

**Benefits**:
- Principle of least privilege
- Explicit scope requirements
- Easier security auditing

**Recommendation**: Implement for v0.1.0 — minimal code change, significant security improvement.

---

## 5. Credential Rotation Procedure Documentation

### Problem
No documented procedure for rotating service account credentials in production.

### Proposed Documentation

```markdown
## Credential Rotation

Google service accounts should be rotated periodically (recommended: every 90 days).

### Rotation Procedure

1. **Create new service account key** in GCP Console:
   - Navigate to IAM & Admin → Service Accounts
   - Select service account
   - Keys → Add Key → Create New Key (JSON)
   - Download new key JSON

2. **Update credential file**:
   ```bash
   # Backup current credentials
   cp ~/.tdt/google-service-account.json ~/.tdt/google-service-account.json.backup
   
   # Replace with new credentials
   cp ~/Downloads/new-service-account.json ~/.tdt/google-service-account.json
   chmod 600 ~/.tdt/google-service-account.json
   ```

3. **Verify new credentials** (with tdt-sheets >=0.1.0):
   ```python
   from tdt_sheets import ServiceAccountAuth
   auth = ServiceAccountAuth.from_env()
   # Cache invalidates automatically on file mtime change
   ```

4. **No service restart required** (tdt-sheets >=0.1.0 with mtime-based caching).

5. **Revoke old credentials** in GCP Console:
   - IAM & Admin → Service Accounts → Keys
   - Delete old key (wait 24h for propagation)

6. **Remove backup** after verification:
   ```bash
   rm ~/.tdt/google-service-account.json.backup
   ```

### Emergency Rotation

If credentials are compromised:

1. **Immediately revoke** old key in GCP Console
2. Create and deploy new key (steps 1-3 above)
3. Audit access logs in GCP for unauthorized usage
4. Update credential in CI/CD secrets if applicable
```

**Recommendation**: Include in library README.md and docs/.

---

## 6. Logging and Observability

### Problem
Authentication failures produce generic warnings with minimal context for debugging.

### Proposed Enhancement

```python
# tdt_sheets/auth.py

import logging
from typing import Any

logger = logging.getLogger(__name__)

class ServiceAccountAuth:
    
    def get_credentials(self) -> Any:
        """Get or refresh credentials.
        
        Returns:
            google.oauth2.service_account.Credentials
        
        Raises:
            RuntimeError: If authentication fails.
        """
        cache_key = _credentials_cache_key(self.credentials_path)
        cached = _CREDENTIALS_CACHE.get(cache_key)
        
        if cached is not None:
            # Check expiry
            if hasattr(cached, "expiry") and cached.expiry:
                remaining = cached.expiry.timestamp() - time.time()
                if remaining > 60:
                    logger.debug(
                        "credentials_cache_hit",
                        extra={
                            "path": str(self.credentials_path),
                            "expires_in": f"{remaining:.0f}s"
                        }
                    )
                    return cached
                
                # Token expiring soon — refresh
                try:
                    logger.info(
                        "credentials_refresh_start",
                        extra={"path": str(self.credentials_path)}
                    )
                    cached.refresh(AuthRequest())
                    logger.info(
                        "credentials_refresh_success",
                        extra={"path": str(self.credentials_path)}
                    )
                    return cached
                except Exception as exc:
                    logger.warning(
                        "credentials_refresh_failed",
                        extra={
                            "path": str(self.credentials_path),
                            "error": str(exc)
                        }
                    )
                    # Fall through to create new
        
        # Create new credentials
        logger.info(
            "credentials_create_start",
            extra={"path": str(self.credentials_path)}
        )
        
        try:
            creds = service_account.Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=list(self.scopes),
            )
            creds.refresh(AuthRequest())
            _CREDENTIALS_CACHE[cache_key] = creds
            
            logger.info(
                "credentials_create_success",
                extra={
                    "path": str(self.credentials_path),
                    "project_id": creds.project_id,
                    "service_account": creds.service_account_email
                }
            )
            
            return creds
        except Exception as exc:
            logger.error(
                "credentials_create_failed",
                extra={
                    "path": str(self.credentials_path),
                    "error": str(exc),
                    "error_type": type(exc).__name__
                },
                exc_info=True
            )
            raise RuntimeError(f"Failed to create credentials: {exc}") from exc
```

**Benefits**:
- Structured logging for monitoring/alerting
- Clear distinction between cache hit, refresh, and create
- Troubleshooting context (project_id, service_account_email)
- Error categorization

**Recommendation**: Implement for v0.1.0 — essential for production observability.

---

## 7. Thread Safety

### Problem
Module-level `_CREDENTIALS_CACHE` dict is shared across threads without locking.

### Current State
```python
_CREDENTIALS_CACHE: dict[str, Any] = {}

# Potential race condition:
cached = _CREDENTIALS_CACHE.get(cache_key)  # Thread A reads
# ... Thread B writes to same key here
return cached  # Thread A returns stale
```

### Risk Assessment
**LOW** — google-auth credentials are immutable after creation, and concurrent refreshes are idempotent. However, cache corruption is theoretically possible.

### Proposed Solution (if needed)

```python
# tdt_sheets/auth.py

import threading

_CREDENTIALS_CACHE: dict[str, Any] = {}
_CACHE_LOCK = threading.RLock()

def get_credentials(self) -> Any:
    cache_key = _credentials_cache_key(self.credentials_path)
    
    with _CACHE_LOCK:
        cached = _CREDENTIALS_CACHE.get(cache_key)
        # ... rest of logic
```

**Recommendation**: **Defer to v0.2.0** — not critical for single-threaded CLIs (all 4 current projects). Document thread-safety status in v0.1.0.

---

## Implementation Priority

### v0.1.0 (Must-Have)
1. ✅ **Cache invalidation on file mtime** — critical for credential rotation
2. ✅ **Configurable scopes** — security best practice
3. ✅ **Credential JSON validation** — improves DX significantly
4. ✅ **Structured logging** — essential for production debugging

### v0.1.0 (Should-Have)
5. ⚠️ **File permission validation** — security hardening (warning only, non-blocking)

### v0.2.0 (Nice-to-Have)
6. 📋 **Thread safety** — document limitations in v0.1.0, implement in v0.2.0
7. 📋 **Credential rotation docs** — can be added post-v0.1.0 in README

---

## Testing Requirements

Each enhancement requires specific tests:

```python
# tests/test_auth_security.py

def test_file_permission_warning(tmp_path, caplog):
    """Test warning logged for world-readable credentials."""
    sa_file = tmp_path / "sa.json"
    sa_file.write_text('{"type": "service_account", ...}')
    sa_file.chmod(0o644)  # World-readable
    
    auth = ServiceAccountAuth(credentials_path=sa_file)
    auth.get_credentials()
    
    assert "service_account_insecure_permissions" in caplog.text


def test_cache_invalidation_on_file_change(tmp_path):
    """Test cache invalidates when file is modified."""
    sa_file = tmp_path / "sa.json"
    sa_file.write_text('{"type": "service_account", "project_id": "old"}')
    
    auth = ServiceAccountAuth(credentials_path=sa_file)
    creds1 = auth.get_credentials()
    
    # Modify file
    time.sleep(0.1)  # Ensure mtime changes
    sa_file.write_text('{"type": "service_account", "project_id": "new"}')
    
    creds2 = auth.get_credentials()
    assert creds2.project_id == "new"
    assert creds1 is not creds2  # Different object


def test_invalid_json_raises_clear_error(tmp_path):
    """Test clear error message for invalid JSON."""
    sa_file = tmp_path / "sa.json"
    sa_file.write_text("{invalid json")
    
    auth = ServiceAccountAuth(credentials_path=sa_file)
    
    with pytest.raises(ValueError, match="Invalid JSON"):
        auth.get_credentials()


def test_missing_required_fields_raises_error(tmp_path):
    """Test error for incomplete service account JSON."""
    sa_file = tmp_path / "sa.json"
    sa_file.write_text('{"type": "service_account"}')  # Missing fields
    
    auth = ServiceAccountAuth(credentials_path=sa_file)
    
    with pytest.raises(ValueError, match="missing fields"):
        auth.get_credentials()


def test_configurable_scopes():
    """Test custom scopes are used."""
    auth = ServiceAccountAuth.from_env(
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    
    assert auth.scopes == ("https://www.googleapis.com/auth/spreadsheets",)
```

---

## Summary

These enhancements improve tdt-sheets security posture without blocking v0.1.0 release:

- **4 critical enhancements** for v0.1.0 (cache invalidation, scopes, validation, logging)
- **1 security hardening** for v0.1.0 (file permission warning)
- **2 deferred enhancements** for v0.2.0 (thread safety, docs)

All enhancements maintain backward compatibility with existing authentication patterns while adding production-ready operational safety.
