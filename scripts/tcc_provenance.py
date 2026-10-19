#!/usr/bin/env python3
"""Read-only macOS TCC provenance and code-signing requirement verifier.

Evaluates active canonical coding agent CLIs and shared host Python automation
identities against `/Library/Application Support/com.apple.TCC/TCC.db` (`mode=ro`):
- Verifies target executables exist on disk and are executable (`os.X_OK`).
- Enforces role-specific TCC service policies (`kTCCServiceAccessibility`,
  `kTCCServiceScreenCapture`, and `kTCCServiceSystemPolicyAllFiles` where required)
  and expected `client_type` (`1` for absolute paths, `0` for bundle identifiers).
- Evaluates each record's stored `csreq` blob against the target executable or
  application bundle using native macOS `Security.framework` APIs
  (`SecRequirementCreateWithData`, `SecStaticCodeCreateWithPath`,
  `SecStaticCodeCheckValidity`) with deterministic `CFRelease` cleanup.
- Strictly read-only: never modifies `TCC.db`, never prompts for consent, and
  never alters system state.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import plistlib
import shutil
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

CANONICAL_TCC_CLIS: tuple[str, ...] = (
    "omp",
    "node",
    "opencode",
    "goose",
    "claude",
    "kimi",
    "herdr",
)
REQUIRED_TCC_SERVICES: tuple[str, ...] = (
    "kTCCServiceAccessibility",
    "kTCCServiceScreenCapture",
)
FULL_DISK_ACCESS_SERVICE = "kTCCServiceSystemPolicyAllFiles"
ALL_THREE_TCC_SERVICES: tuple[str, ...] = (
    "kTCCServiceAccessibility",
    "kTCCServiceScreenCapture",
    FULL_DISK_ACCESS_SERVICE,
)
FDA_REQUIRED_TCC_CLIS: tuple[str, ...] = ("herdr", "omp")
SHARED_PYTHON_AUTOMATION_BINARY = "python3"
DEFAULT_TCC_DB_PATH = Path("/Library/Application Support/com.apple.TCC/TCC.db")

STANDARD_PATH = (
    "/opt/homebrew/bin:/opt/homebrew/sbin:"
    "/opt/homebrew/opt/libpq/bin:"
    f"{Path.home()}/.kimi-code/bin:"
    f"{Path.home()}/.qoder/entry:"
    f"{Path.home()}/.pi/agent/bin:"
    f"{Path.home()}/.npm-global/bin:"
    f"{Path.home()}/.local/bin:"
    f"{Path.home()}/.bun/bin:"
    "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
)

ROLE_POLICY_DESCRIPTIONS: dict[str, str] = {
    "supervisor_multiplexer": (
        "Herdr LaunchAgent PTY supervisor; responsible process for interactive "
        "shells and coding agents inside Herdr panes (requires AX, ScreenCapture, FDA)."
    ),
    "host_automation_agent_cli": (
        "Primary host computer-use and TCC audit coding agent CLI "
        "(requires AX, ScreenCapture, FDA)."
    ),
    "canonical_agent_cli": (
        "Canonical coding agent CLI or runtime (requires AX and ScreenCapture)."
    ),
    "shared_host_python_automation": (
        "Shared host Python automation executable (requires AX, ScreenCapture, FDA; "
        "retained as host automation privilege, not required by herdr-notifier.py)."
    ),
    "shared_host_python_bundle_automation": (
        "Shared host Python framework application bundle identity org.python.python "
        "(requires AX, ScreenCapture, FDA; retained as host automation privilege, "
        "not required by herdr-notifier.py)."
    ),
}


class NativeSecurityError(RuntimeError):
    """Raised when macOS CoreFoundation or Security frameworks cannot be initialized."""


@dataclass(frozen=True)
class TCCTargetSpec:
    name: str
    role: str
    client: str
    client_type: int  # 0 = bundle identifier, 1 = absolute path
    target_path: str | None
    executable_path: str | None
    required_services: tuple[str, ...]
    resolution_error: str | None = None


@dataclass
class TCCRecordAudit:
    name: str
    role: str
    client: str
    client_type: int
    target_path: str | None
    executable_path: str | None
    required_services: list[str]
    granted_services: list[str] = field(default_factory=list)
    missing_services: list[str] = field(default_factory=list)
    signature_valid: bool = False
    verified: bool = False
    failure_reasons: list[str] = field(default_factory=list)


_CF_LIB: ctypes.CDLL | None = None
_SEC_LIB: ctypes.CDLL | None = None


def _get_security_frameworks() -> tuple[ctypes.CDLL, ctypes.CDLL]:
    """Load and configure CoreFoundation and Security ctypes bindings on Darwin."""
    global _CF_LIB, _SEC_LIB
    if _CF_LIB is not None and _SEC_LIB is not None:
        return _CF_LIB, _SEC_LIB

    try:
        cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
        sec = ctypes.CDLL("/System/Library/Frameworks/Security.framework/Security")

        cf.CFDataCreate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
        cf.CFDataCreate.restype = ctypes.c_void_p

        cf.CFDataGetLength.argtypes = [ctypes.c_void_p]
        cf.CFDataGetLength.restype = ctypes.c_long

        cf.CFDataGetBytePtr.argtypes = [ctypes.c_void_p]
        cf.CFDataGetBytePtr.restype = ctypes.c_void_p

        cf.CFURLCreateFromFileSystemRepresentation.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_long,
            ctypes.c_bool,
        ]
        cf.CFURLCreateFromFileSystemRepresentation.restype = ctypes.c_void_p

        cf.CFRelease.argtypes = [ctypes.c_void_p]
        cf.CFRelease.restype = None

        sec.SecRequirementCreateWithData.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        sec.SecRequirementCreateWithData.restype = ctypes.c_int32

        sec.SecStaticCodeCreateWithPath.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        sec.SecStaticCodeCreateWithPath.restype = ctypes.c_int32

        sec.SecStaticCodeCheckValidity.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        sec.SecStaticCodeCheckValidity.restype = ctypes.c_int32

        sec.SecCodeCopyDesignatedRequirement.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        sec.SecCodeCopyDesignatedRequirement.restype = ctypes.c_int32

        sec.SecRequirementCopyData.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        sec.SecRequirementCopyData.restype = ctypes.c_int32
    except Exception as exc:
        raise NativeSecurityError(f"Failed to load macOS Security/CoreFoundation frameworks: {exc}") from exc

    _CF_LIB = cf
    _SEC_LIB = sec
    return cf, sec


def evaluate_csreq_against_path(
    target_path: str | Path,
    csreq_blob: bytes | bytearray | memoryview | None,
) -> tuple[bool, str]:
    """Validate that `target_path` satisfies the binary `csreq_blob` via Security.framework.

    Returns `(is_valid, reason)`. Raises `NativeSecurityError` only if the macOS
    Security/CoreFoundation libraries themselves cannot be initialized.
    """
    if csreq_blob is None:
        return False, "missing_csreq"
    raw_csreq = bytes(csreq_blob)
    if not raw_csreq:
        return False, "missing_csreq"

    target_p = Path(target_path)
    if not target_p.exists():
        return False, "missing_target_path"

    cf, sec = _get_security_frameworks()
    cf_data: int | None = None
    cf_url: int | None = None
    sec_req = ctypes.c_void_p(0)
    static_code = ctypes.c_void_p(0)

    try:
        csreq_buf = ctypes.create_string_buffer(raw_csreq, len(raw_csreq))
        cf_data = cf.CFDataCreate(None, ctypes.cast(csreq_buf, ctypes.c_void_p), len(raw_csreq))
        if not cf_data:
            return False, "cfdata_create_failed"

        st_req = int(sec.SecRequirementCreateWithData(cf_data, 0, ctypes.byref(sec_req)))
        if st_req != 0 or not sec_req.value:
            return False, f"malformed_csreq(OSStatus={st_req})"

        fs_bytes = os.fsencode(str(target_p))
        fs_buf = ctypes.create_string_buffer(fs_bytes, len(fs_bytes))
        cf_url = cf.CFURLCreateFromFileSystemRepresentation(
            None,
            ctypes.cast(fs_buf, ctypes.c_void_p),
            len(fs_bytes),
            target_p.is_dir(),
        )
        if not cf_url:
            return False, "cfurl_create_failed"

        st_code = int(sec.SecStaticCodeCreateWithPath(cf_url, 0, ctypes.byref(static_code)))
        if st_code != 0 or not static_code.value:
            return False, f"static_code_invalid(OSStatus={st_code})"

        st_val = int(sec.SecStaticCodeCheckValidity(static_code.value, 0, sec_req.value))
        # Ad-hoc signed framework app bundles (such as Homebrew's Python.app wrapper)
        # have no sealed resources directory, causing default resource validation to return
        # errSecCSReqFailed (-67056). If default validation reports -67056 on a directory/bundle,
        # re-check with kSecCSDoNotValidateResources (0x04) per CSCommon.h to test the code
        # signature and requirement without failing on absent resources.
        if st_val == -67056 and target_p.is_dir():
            st_val = int(sec.SecStaticCodeCheckValidity(static_code.value, 4, sec_req.value))

        if st_val != 0:
            return False, f"csreq_mismatch(OSStatus={st_val})"

        return True, "valid"
    finally:
        if static_code.value:
            cf.CFRelease(static_code.value)
        if sec_req.value:
            cf.CFRelease(sec_req.value)
        if cf_url:
            cf.CFRelease(cf_url)
        if cf_data:
            cf.CFRelease(cf_data)


def copy_designated_csreq_blob(target_path: str | Path) -> bytes:
    """Extract the binary designated requirement (`csreq` blob) for a signed Mach-O or bundle."""
    target_p = Path(target_path)
    if not target_p.exists():
        raise FileNotFoundError(f"Target path does not exist: {target_p}")

    cf, sec = _get_security_frameworks()
    cf_url: int | None = None
    static_code = ctypes.c_void_p(0)
    sec_req = ctypes.c_void_p(0)
    cf_data = ctypes.c_void_p(0)

    try:
        fs_bytes = os.fsencode(str(target_p))
        fs_buf = ctypes.create_string_buffer(fs_bytes, len(fs_bytes))
        cf_url = cf.CFURLCreateFromFileSystemRepresentation(
            None,
            ctypes.cast(fs_buf, ctypes.c_void_p),
            len(fs_bytes),
            target_p.is_dir(),
        )
        if not cf_url:
            raise RuntimeError(f"CFURLCreateFromFileSystemRepresentation failed for {target_p}")

        st_code = int(sec.SecStaticCodeCreateWithPath(cf_url, 0, ctypes.byref(static_code)))
        if st_code != 0 or not static_code.value:
            raise RuntimeError(f"SecStaticCodeCreateWithPath failed for {target_p}: OSStatus={st_code}")

        st_req = int(sec.SecCodeCopyDesignatedRequirement(static_code.value, 0, ctypes.byref(sec_req)))
        if st_req != 0 or not sec_req.value:
            raise RuntimeError(f"SecCodeCopyDesignatedRequirement failed for {target_p}: OSStatus={st_req}")

        st_data = int(sec.SecRequirementCopyData(sec_req.value, 0, ctypes.byref(cf_data)))
        if st_data != 0 or not cf_data.value:
            raise RuntimeError(f"SecRequirementCopyData failed for {target_p}: OSStatus={st_data}")

        length = int(cf.CFDataGetLength(cf_data.value))
        ptr = cf.CFDataGetBytePtr(cf_data.value)
        if length <= 0 or not ptr:
            raise RuntimeError(f"Empty designated csreq data for {target_p}")
        return ctypes.string_at(ptr, length)
    finally:
        if cf_data.value:
            cf.CFRelease(cf_data.value)
        if sec_req.value:
            cf.CFRelease(sec_req.value)
        if static_code.value:
            cf.CFRelease(static_code.value)
        if cf_url:
            cf.CFRelease(cf_url)


def resolve_python_framework_bundle(python_executable: str | Path) -> tuple[str, Path, Path] | None:
    """Resolve `(bundle_id, bundle_app_path, bundle_exec_path)` if `python_executable`
    resides inside a macOS Framework containing `Resources/Python.app/Contents/Info.plist`.
    Returns `None` for non-framework Python installations.
    """
    p = Path(python_executable)
    candidates: list[Path] = []
    for base in (p, p.resolve() if p.exists() else p):
        app_candidate = base.parent.parent / "Resources" / "Python.app"
        if app_candidate not in candidates:
            candidates.append(app_candidate)

    for app_dir in candidates:
        info_plist = app_dir / "Contents" / "Info.plist"
        if not info_plist.is_file():
            continue
        try:
            plist_data = plistlib.loads(info_plist.read_bytes())
            bundle_id = str(plist_data.get("CFBundleIdentifier", "")).strip()
            exec_name = str(plist_data.get("CFBundleExecutable", "Python")).strip() or "Python"
            if not bundle_id:
                continue
            bundle_exec = app_dir / "Contents" / "MacOS" / exec_name
            return bundle_id, app_dir, bundle_exec
        except Exception:
            continue
    return None


def _classify_cli_role_and_services(raw_name: str, resolved_path: str | None = None) -> tuple[str, tuple[str, ...]]:
    names = {Path(raw_name).name.lower()}
    if resolved_path:
        names.add(Path(resolved_path).name.lower())

    if "herdr" in names:
        return "supervisor_multiplexer", ALL_THREE_TCC_SERVICES
    if "omp" in names:
        return "host_automation_agent_cli", ALL_THREE_TCC_SERVICES
    if any(n == "python" or n.startswith("python3") for n in names):
        return "shared_host_python_automation", ALL_THREE_TCC_SERVICES
    return "canonical_agent_cli", REQUIRED_TCC_SERVICES


def build_required_targets(
    binaries: list[str] | None = None,
    *,
    search_path: str | None = None,
    include_python_automation: bool | None = None,
) -> list[TCCTargetSpec]:
    """Construct the ordered list of required TCC target identities and role policies."""
    eff_path = search_path if search_path is not None else STANDARD_PATH
    specs: list[TCCTargetSpec] = []

    if binaries is not None:
        for item in binaries:
            raw_item = str(item).strip()
            if not raw_item:
                specs.append(
                    TCCTargetSpec(
                        name="<empty>",
                        role="canonical_agent_cli",
                        client="<empty>",
                        client_type=1,
                        target_path=None,
                        executable_path=None,
                        required_services=REQUIRED_TCC_SERVICES,
                        resolution_error="empty_binary_spec",
                    )
                )
                continue

            if raw_item.startswith("org.python.python="):
                bundle_raw = raw_item.split("=", 1)[1].strip()
                bundle_real = os.path.realpath(bundle_raw)
                exec_path = str(Path(bundle_real) / "Contents" / "MacOS" / "Python")
                specs.append(
                    TCCTargetSpec(
                        name="org.python.python",
                        role="shared_host_python_bundle_automation",
                        client="org.python.python",
                        client_type=0,
                        target_path=bundle_real,
                        executable_path=exec_path,
                        required_services=ALL_THREE_TCC_SERVICES,
                    )
                )
                continue

            if raw_item == "org.python.python":
                py_which = shutil.which(SHARED_PYTHON_AUTOMATION_BINARY, path=eff_path)
                bundle_info = (
                    resolve_python_framework_bundle(os.path.realpath(py_which))
                    if py_which
                    else None
                )
                if bundle_info is None:
                    specs.append(
                        TCCTargetSpec(
                            name="org.python.python",
                            role="shared_host_python_bundle_automation",
                            client="org.python.python",
                            client_type=0,
                            target_path=None,
                            executable_path=None,
                            required_services=ALL_THREE_TCC_SERVICES,
                            resolution_error="unresolved_bundle:org.python.python",
                        )
                    )
                else:
                    b_id, b_app, b_exec = bundle_info
                    specs.append(
                        TCCTargetSpec(
                            name=b_id,
                            role="shared_host_python_bundle_automation",
                            client=b_id,
                            client_type=0,
                            target_path=str(b_app),
                            executable_path=str(b_exec),
                            required_services=ALL_THREE_TCC_SERVICES,
                        )
                    )
                continue

            if "/" not in raw_item and not Path(raw_item).exists():
                resolved_which = shutil.which(raw_item, path=eff_path)
                if not resolved_which:
                    role, svcs = _classify_cli_role_and_services(raw_item)
                    specs.append(
                        TCCTargetSpec(
                            name=raw_item,
                            role=role,
                            client=raw_item,
                            client_type=1,
                            target_path=None,
                            executable_path=None,
                            required_services=svcs,
                            resolution_error=f"unresolved_binary:{raw_item}",
                        )
                    )
                    continue
                real_bin = os.path.realpath(resolved_which)
            else:
                real_bin = os.path.realpath(raw_item)

            role, svcs = _classify_cli_role_and_services(raw_item, real_bin)
            specs.append(
                TCCTargetSpec(
                    name=Path(raw_item).name or real_bin,
                    role=role,
                    client=real_bin,
                    client_type=1,
                    target_path=real_bin,
                    executable_path=real_bin,
                    required_services=svcs,
                )
            )
            if include_python_automation and role == "shared_host_python_automation":
                bundle_info = resolve_python_framework_bundle(real_bin)
                if bundle_info is not None:
                    b_id, b_app, b_exec = bundle_info
                    specs.append(
                        TCCTargetSpec(
                            name=b_id,
                            role="shared_host_python_bundle_automation",
                            client=b_id,
                            client_type=0,
                            target_path=str(b_app),
                            executable_path=str(b_exec),
                            required_services=ALL_THREE_TCC_SERVICES,
                        )
                    )
        return specs

    include_py = True if include_python_automation is None else include_python_automation
    for cli_name in CANONICAL_TCC_CLIS:
        role, svcs = _classify_cli_role_and_services(cli_name)
        bin_path = shutil.which(cli_name, path=eff_path)
        if not bin_path:
            specs.append(
                TCCTargetSpec(
                    name=cli_name,
                    role=role,
                    client=cli_name,
                    client_type=1,
                    target_path=None,
                    executable_path=None,
                    required_services=svcs,
                    resolution_error=f"unresolved_binary:{cli_name}",
                )
            )
            continue
        real_bin = os.path.realpath(bin_path)
        specs.append(
            TCCTargetSpec(
                name=cli_name,
                role=role,
                client=real_bin,
                client_type=1,
                target_path=real_bin,
                executable_path=real_bin,
                required_services=svcs,
            )
        )

    if include_py:
        py_bin = shutil.which(SHARED_PYTHON_AUTOMATION_BINARY, path=eff_path)
        if not py_bin:
            specs.append(
                TCCTargetSpec(
                    name=SHARED_PYTHON_AUTOMATION_BINARY,
                    role="shared_host_python_automation",
                    client=SHARED_PYTHON_AUTOMATION_BINARY,
                    client_type=1,
                    target_path=None,
                    executable_path=None,
                    required_services=ALL_THREE_TCC_SERVICES,
                    resolution_error=f"unresolved_binary:{SHARED_PYTHON_AUTOMATION_BINARY}",
                )
            )
        else:
            real_py = os.path.realpath(py_bin)
            specs.append(
                TCCTargetSpec(
                    name=SHARED_PYTHON_AUTOMATION_BINARY,
                    role="shared_host_python_automation",
                    client=real_py,
                    client_type=1,
                    target_path=real_py,
                    executable_path=real_py,
                    required_services=ALL_THREE_TCC_SERVICES,
                )
            )
            bundle_info = resolve_python_framework_bundle(real_py)
            if bundle_info is not None:
                b_id, b_app, b_exec = bundle_info
                specs.append(
                    TCCTargetSpec(
                        name=b_id,
                        role="shared_host_python_bundle_automation",
                        client=b_id,
                        client_type=0,
                        target_path=str(b_app),
                        executable_path=str(b_exec),
                        required_services=ALL_THREE_TCC_SERVICES,
                    )
                )

    return specs


def verify_tcc_provenance(
    tcc_db_path: Path | None = None,
    binaries: list[str] | None = None,
    *,
    search_path: str | None = None,
    include_python_automation: bool | None = None,
) -> dict[str, Any]:
    """Verify active canonical coding agent CLIs and shared Python automation identities in TCC.db."""
    if sys.platform != "darwin":
        return {
            "status": "SKIPPED",
            "reason": "TCC provenance check only applies on darwin",
            "verified_binaries": [],
            "missing_binaries": [],
            "records": [],
            "errors": [],
        }

    tcc_db = Path(tcc_db_path) if tcc_db_path is not None else DEFAULT_TCC_DB_PATH
    if not tcc_db.exists():
        msg = f"TCC.db not present: {tcc_db}"
        return {
            "status": "ERROR",
            "reason": msg,
            "verified_binaries": [],
            "missing_binaries": [],
            "records": [],
            "errors": [msg],
        }
    if not tcc_db.is_file() or not os.access(tcc_db, os.R_OK):
        msg = f"TCC.db not readable: {tcc_db}"
        return {
            "status": "ERROR",
            "reason": msg,
            "verified_binaries": [],
            "missing_binaries": [],
            "records": [],
            "errors": [msg],
        }

    specs = build_required_targets(
        binaries=binaries,
        search_path=search_path,
        include_python_automation=include_python_automation,
    )
    if not specs:
        msg = "Empty target binary set for TCC provenance check"
        return {
            "status": "DRIFT",
            "reason": msg,
            "verified_binaries": [],
            "missing_binaries": [],
            "records": [],
            "errors": [msg],
        }

    try:
        _get_security_frameworks()
    except NativeSecurityError as exc:
        msg = str(exc)
        return {
            "status": "ERROR",
            "reason": msg,
            "verified_binaries": [],
            "missing_binaries": [],
            "records": [],
            "errors": [msg],
        }

    try:
        conn = sqlite3.connect(f"file:{tcc_db}?mode=ro", uri=True)
        try:
            cursor = conn.cursor()
            verified_binaries: list[str] = []
            missing_binaries: list[str] = []
            records: list[dict[str, Any]] = []
            errors: list[str] = []

            for spec in specs:
                audit = TCCRecordAudit(
                    name=spec.name,
                    role=spec.role,
                    client=spec.client,
                    client_type=spec.client_type,
                    target_path=spec.target_path,
                    executable_path=spec.executable_path,
                    required_services=list(spec.required_services),
                )

                if spec.resolution_error:
                    audit.missing_services = list(spec.required_services)
                    audit.failure_reasons.append(spec.resolution_error)
                    missing_binaries.append(spec.client)
                    errors.append(f"{spec.client}: {spec.resolution_error}")
                    records.append(asdict(audit))
                    continue

                if (
                    not spec.target_path
                    or not spec.executable_path
                    or not Path(spec.target_path).exists()
                    or not Path(spec.executable_path).is_file()
                    or not os.access(spec.executable_path, os.X_OK)
                ):
                    reason = f"missing_or_non_executable_target({spec.executable_path or spec.target_path})"
                    audit.missing_services = list(spec.required_services)
                    audit.failure_reasons.append(reason)
                    missing_binaries.append(spec.client)
                    errors.append(f"{spec.client}: {reason}")
                    records.append(asdict(audit))
                    continue

                placeholders = ",".join("?" for _ in spec.required_services)
                cursor.execute(
                    f"SELECT service, client_type, auth_value, csreq FROM access "  # noqa: S608
                    f"WHERE client = ? AND service IN ({placeholders})",
                    (spec.client, *spec.required_services),
                )
                rows = cursor.fetchall()
                rows_by_service: dict[str, list[tuple[Any, Any, Any]]] = {}
                for svc, c_type, auth_val, csreq_blob in rows:
                    rows_by_service.setdefault(str(svc), []).append((c_type, auth_val, csreq_blob))

                all_sigs_ok = True
                for req_svc in spec.required_services:
                    svc_rows = rows_by_service.get(req_svc, [])
                    if not svc_rows:
                        audit.missing_services.append(req_svc)
                        audit.failure_reasons.append(f"{req_svc}:missing_grant")
                        all_sigs_ok = False
                        continue

                    type_matched_rows = [r for r in svc_rows if r[0] == spec.client_type]
                    if not type_matched_rows:
                        observed_types = sorted({r[0] for r in svc_rows})
                        audit.missing_services.append(req_svc)
                        audit.failure_reasons.append(
                            f"{req_svc}:wrong_client_type(got={observed_types},expected={spec.client_type})"
                        )
                        all_sigs_ok = False
                        continue

                    allowed_rows = [r for r in type_matched_rows if r[1] == 2]
                    if not allowed_rows:
                        observed_auth = sorted({r[1] for r in type_matched_rows})
                        audit.missing_services.append(req_svc)
                        audit.failure_reasons.append(
                            f"{req_svc}:denied_or_pending(auth_value={observed_auth})"
                        )
                        all_sigs_ok = False
                        continue

                    # Evaluate stored csreq for the allowed row(s)
                    svc_sig_ok = False
                    svc_sig_reason = "missing_csreq"
                    for _c_type, _auth_val, csreq_blob in allowed_rows:
                        sig_ok, sig_reason = evaluate_csreq_against_path(spec.target_path, csreq_blob)
                        if sig_ok:
                            svc_sig_ok = True
                            svc_sig_reason = "valid"
                            break
                        svc_sig_reason = sig_reason

                    if not svc_sig_ok:
                        audit.missing_services.append(req_svc)
                        audit.failure_reasons.append(f"{req_svc}:{svc_sig_reason}")
                        all_sigs_ok = False
                    else:
                        audit.granted_services.append(req_svc)

                audit.signature_valid = all_sigs_ok and len(audit.granted_services) == len(spec.required_services)
                if not audit.failure_reasons and audit.signature_valid:
                    audit.verified = True
                    verified_binaries.append(spec.client)
                else:
                    audit.verified = False
                    missing_binaries.append(spec.client)
                    errors.append(f"{spec.client}: {', '.join(audit.failure_reasons)}")

                records.append(asdict(audit))

            status = "CLEAN" if (verified_binaries and not missing_binaries and not errors) else "DRIFT"
            return {
                "status": status,
                "verified_binaries": verified_binaries,
                "missing_binaries": missing_binaries,
                "records": records,
                "errors": errors,
            }
        finally:
            conn.close()
    except NativeSecurityError as exc:
        msg = f"Native Security verification failed: {exc}"
        return {
            "status": "ERROR",
            "reason": msg,
            "verified_binaries": [],
            "missing_binaries": [],
            "records": [],
            "errors": [msg],
        }
    except (sqlite3.Error, OSError) as exc:
        msg = f"TCC.db read failed: {exc}"
        return {
            "status": "ERROR",
            "reason": msg,
            "verified_binaries": [],
            "missing_binaries": [],
            "records": [],
            "errors": [msg],
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify macOS TCC provenance and stored csreq signatures.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    parser.add_argument(
        "--db",
        default=str(DEFAULT_TCC_DB_PATH),
        help="Path to TCC.db (opened strictly read-only with mode=ro).",
    )
    parser.add_argument(
        "--binary",
        action="append",
        dest="binaries",
        help="Explicit binary path/name or org.python.python[=/path/to/Python.app] to verify.",
    )
    parser.add_argument(
        "--no-python-automation",
        action="store_true",
        help="Exclude shared host Python automation identities when --binary is not specified.",
    )
    args = parser.parse_args(argv)

    result = verify_tcc_provenance(
        tcc_db_path=Path(args.db),
        binaries=args.binaries,
        include_python_automation=not args.no_python_automation if args.binaries is None else None,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = result.get("status", "ERROR")
        if status == "SKIPPED":
            print(f"      - {result.get('reason', 'skipped')}")
            return 0
        if status == "ERROR":
            print(f"      - ERROR: {result.get('reason', 'TCC verification failed')}")
            return 2
        for rec in result.get("records", []):
            client = rec.get("client", "")
            name = rec.get("name", Path(client).name if client else "unknown")
            role = rec.get("role", "")
            if rec.get("verified"):
                svcs = ", ".join(rec.get("granted_services", []))
                print(f"      - {name} ({role}): verified ({svcs}; csreq=valid) [{client}]")
            else:
                reasons = ", ".join(rec.get("failure_reasons", []))
                print(f"      - {name} ({role}): DRIFT ({reasons}) [{client}]")

    status = result.get("status", "ERROR")
    if status in ("CLEAN", "SKIPPED"):
        return 0
    if status == "DRIFT":
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
