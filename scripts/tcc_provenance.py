#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.15"
# dependencies = []
# ///
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

CANONICAL_TCC_BUNDLES: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "org.python.python": ("Python.app", "shared_host_python_bundle_automation", ALL_THREE_TCC_SERVICES),
    "com.stablyai.orca": ("/Applications/Orca.app", "orchestrator_bundle", ALL_THREE_TCC_SERVICES),
    "com.trycua.driver": ("/Applications/CuaDriver.app", "computer_use_driver", ALL_THREE_TCC_SERVICES),
    "com.electron.goose": ("/Applications/Goose.app", "canonical_agent_bundle", ALL_THREE_TCC_SERVICES),
    "ai.opencode.desktop": ("/Applications/OpenCode.app", "canonical_agent_bundle", ("kTCCServiceAccessibility", FULL_DISK_ACCESS_SERVICE)),
    "com.openai.codex": ("/Applications/ChatGPT.app", "canonical_agent_bundle", ALL_THREE_TCC_SERVICES),
    "com.nousresearch.hermes": ("/Applications/Hermes.app", "host_agent_bundle", ALL_THREE_TCC_SERVICES),
    "org.p0deje.Maccy": ("/Applications/Maccy.app", "utility_bundle", ("kTCCServiceAccessibility", "kTCCServicePostEvent")),
}

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


class NativeSecurityError(RuntimeError):
    """Raised when macOS CoreFoundation or Security frameworks cannot be initialized."""


@dataclass
class TCCRecordAudit:
    name: str
    role: str
    client: str
    client_type: int  # 0 = bundle identifier, 1 = absolute path
    target_path: str | None
    executable_path: str | None
    required_services: list[str]
    granted_services: list[str] = field(default_factory=list)
    missing_services: list[str] = field(default_factory=list)
    signature_valid: bool = False
    verified: bool = False
    failure_reasons: list[str] = field(default_factory=list)
    resolution_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("resolution_error", None)
        return data


TCCTargetSpec = TCCRecordAudit

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


def _create_static_code(
    target_p: Path, cf: ctypes.CDLL, sec: ctypes.CDLL
) -> tuple[int | None, ctypes.c_void_p, int]:
    """Create CFURL and SecStaticCode for `target_p`. Caller must CFRelease non-null handles."""
    fs_bytes = os.fsencode(str(target_p))
    fs_buf = ctypes.create_string_buffer(fs_bytes, len(fs_bytes))
    cf_url = cf.CFURLCreateFromFileSystemRepresentation(
        None,
        ctypes.cast(fs_buf, ctypes.c_void_p),
        len(fs_bytes),
        target_p.is_dir(),
    )
    static_code = ctypes.c_void_p(0)
    if not cf_url:
        return None, static_code, -1
    st_code = int(sec.SecStaticCodeCreateWithPath(cf_url, 0, ctypes.byref(static_code)))
    return cf_url, static_code, st_code


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

        cf_url, static_code, st_code = _create_static_code(target_p, cf, sec)
        if not cf_url:
            return False, "cfurl_create_failed"
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
        cf_url, static_code, st_code = _create_static_code(target_p, cf, sec)
        if not cf_url:
            raise RuntimeError(f"CFURLCreateFromFileSystemRepresentation failed for {target_p}")
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
) -> list[TCCRecordAudit]:
    """Construct the ordered list of required TCC target identities and role policies."""
    eff_path = search_path if search_path is not None else STANDARD_PATH
    specs: list[TCCRecordAudit] = []

    if binaries is None:
        include_py = True if include_python_automation is None else bool(include_python_automation)
        raw_items = [*CANONICAL_TCC_CLIS, *([SHARED_PYTHON_AUTOMATION_BINARY] if include_py else [])]
    else:
        include_py = bool(include_python_automation)
        raw_items = [str(item).strip() for item in binaries]

    for raw_item in raw_items:
        if not raw_item:
            specs.append(
                TCCRecordAudit(
                    name="<empty>",
                    role="canonical_agent_cli",
                    client="<empty>",
                    client_type=1,
                    target_path=None,
                    executable_path=None,
                    required_services=list(REQUIRED_TCC_SERVICES),
                    resolution_error="empty_binary_spec",
                )
            )
            continue

        if raw_item.startswith("org.python.python="):
            bundle_real = os.path.realpath(raw_item.split("=", 1)[1].strip())
            specs.append(
                TCCRecordAudit(
                    name="org.python.python",
                    role="shared_host_python_bundle_automation",
                    client="org.python.python",
                    client_type=0,
                    target_path=bundle_real,
                    executable_path=str(Path(bundle_real) / "Contents" / "MacOS" / "Python"),
                    required_services=list(ALL_THREE_TCC_SERVICES),
                )
            )
            continue

        if raw_item.startswith("bundle:"):
            b_spec = raw_item[7:].strip()
            if "=" in b_spec:
                b_id, b_path_str = b_spec.split("=", 1)
                b_id = b_id.strip()
                app_p = Path(os.path.realpath(b_path_str.strip()))
            else:
                b_id = b_spec
                app_hint = CANONICAL_TCC_BUNDLES.get(b_id, (f"/Applications/{b_id}.app",))[0]
                app_p = Path(app_hint)
            exec_name = app_p.stem
            info_p = app_p / "Contents" / "Info.plist"
            if info_p.is_file():
                try:
                    data = plistlib.loads(info_p.read_bytes())
                    exec_name = data.get("CFBundleExecutable") or exec_name
                except Exception:
                    pass
            exec_p = app_p / "Contents" / "MacOS" / exec_name
            role = CANONICAL_TCC_BUNDLES.get(b_id, ("", "canonical_agent_bundle", REQUIRED_TCC_SERVICES))[1]
            svcs = CANONICAL_TCC_BUNDLES.get(b_id, ("", "", REQUIRED_TCC_SERVICES))[2]
            specs.append(
                TCCRecordAudit(
                    name=b_id,
                    role=role,
                    client=b_id,
                    client_type=0,
                    target_path=str(app_p),
                    executable_path=str(exec_p),
                    required_services=list(svcs),
                )
            )
            continue

        if raw_item in CANONICAL_TCC_BUNDLES and raw_item != "org.python.python":
            app_hint, b_role, svcs = CANONICAL_TCC_BUNDLES[raw_item]
            app_p = Path(app_hint)
            if app_p.is_dir():
                exec_name = app_p.stem
                info_p = app_p / "Contents" / "Info.plist"
                if info_p.is_file():
                    try:
                        data = plistlib.loads(info_p.read_bytes())
                        exec_name = data.get("CFBundleExecutable") or exec_name
                    except Exception:
                        pass
                exec_p = app_p / "Contents" / "MacOS" / exec_name
                specs.append(
                    TCCRecordAudit(
                        name=raw_item,
                        role=b_role,
                        client=raw_item,
                        client_type=0,
                        target_path=str(app_p),
                        executable_path=str(exec_p),
                        required_services=list(svcs),
                    )
                )
                continue

        if raw_item == "org.python.python":
            py_which = shutil.which(SHARED_PYTHON_AUTOMATION_BINARY, path=eff_path)
            bundle_info = (
                resolve_python_framework_bundle(os.path.realpath(py_which)) if py_which else None
            )
            if bundle_info is None:
                specs.append(
                    TCCRecordAudit(
                        name="org.python.python",
                        role="shared_host_python_bundle_automation",
                        client="org.python.python",
                        client_type=0,
                        target_path=None,
                        executable_path=None,
                        required_services=list(ALL_THREE_TCC_SERVICES),
                        resolution_error="unresolved_bundle:org.python.python",
                    )
                )
            else:
                b_id, b_app, b_exec = bundle_info
                specs.append(
                    TCCRecordAudit(
                        name=b_id,
                        role="shared_host_python_bundle_automation",
                        client=b_id,
                        client_type=0,
                        target_path=str(b_app),
                        executable_path=str(b_exec),
                        required_services=list(ALL_THREE_TCC_SERVICES),
                    )
                )
            continue

        if "/" not in raw_item and (binaries is None or not Path(raw_item).exists()):
            resolved_which = shutil.which(raw_item, path=eff_path)
            if not resolved_which:
                role, svcs = _classify_cli_role_and_services(raw_item)
                specs.append(
                    TCCRecordAudit(
                        name=raw_item,
                        role=role,
                        client=raw_item,
                        client_type=1,
                        target_path=None,
                        executable_path=None,
                        required_services=list(svcs),
                        resolution_error=f"unresolved_binary:{raw_item}",
                    )
                )
                continue
            real_bin = os.path.realpath(resolved_which)
        else:
            real_bin = os.path.realpath(raw_item)

        role, svcs = _classify_cli_role_and_services(raw_item, real_bin)
        specs.append(
            TCCRecordAudit(
                name=Path(raw_item).name or real_bin,
                role=role,
                client=real_bin,
                client_type=1,
                target_path=real_bin,
                executable_path=real_bin,
                required_services=list(svcs),
            )
        )
        if include_py and role == "shared_host_python_automation":
            bundle_info = resolve_python_framework_bundle(real_bin)
            if bundle_info is not None:
                b_id, b_app, b_exec = bundle_info
                specs.append(
                    TCCRecordAudit(
                        name=b_id,
                        role="shared_host_python_bundle_automation",
                        client=b_id,
                        client_type=0,
                        target_path=str(b_app),
                        executable_path=str(b_exec),
                        required_services=list(ALL_THREE_TCC_SERVICES),
                    )
                )

    return specs


def _tcc_result(
    status: str,
    *,
    reason: str | None = None,
    verified_binaries: list[str] | None = None,
    missing_binaries: list[str] | None = None,
    records: list[dict[str, Any]] | None = None,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    res: dict[str, Any] = {"status": status}
    if reason is not None:
        res["reason"] = reason
    res["verified_binaries"] = verified_binaries if verified_binaries is not None else []
    res["missing_binaries"] = missing_binaries if missing_binaries is not None else []
    res["records"] = records if records is not None else []
    res["errors"] = errors if errors is not None else ([reason] if reason and status != "SKIPPED" else [])
    return res


def verify_tcc_provenance(
    tcc_db_path: Path | None = None,
    binaries: list[str] | None = None,
    *,
    search_path: str | None = None,
    include_python_automation: bool | None = None,
    bundles: bool = False,
) -> dict[str, Any]:
    """Verify active canonical coding agent CLIs and shared Python automation identities in TCC.db."""
    if sys.platform != "darwin":
        return _tcc_result("SKIPPED", reason="TCC provenance check only applies on darwin")

    tcc_db = Path(tcc_db_path) if tcc_db_path is not None else DEFAULT_TCC_DB_PATH
    if not tcc_db.exists():
        return _tcc_result("ERROR", reason=f"TCC.db not present: {tcc_db}")
    if not tcc_db.is_file() or not os.access(tcc_db, os.R_OK):
        return _tcc_result("ERROR", reason=f"TCC.db not readable: {tcc_db}")

    target_binaries = binaries
    if bundles and target_binaries is None:
        target_binaries = list(CANONICAL_TCC_BUNDLES.keys())

    specs = build_required_targets(
        binaries=target_binaries,
        search_path=search_path,
        include_python_automation=include_python_automation,
    )
    if not specs:
        return _tcc_result("DRIFT", reason="Empty target binary set for TCC provenance check")

    try:
        _get_security_frameworks()
    except NativeSecurityError as exc:
        return _tcc_result("ERROR", reason=str(exc))

    try:
        conn = sqlite3.connect(f"file:{tcc_db}?mode=ro", uri=True)
        try:
            cursor = conn.cursor()
            verified_binaries: list[str] = []
            missing_binaries: list[str] = []
            records: list[dict[str, Any]] = []
            errors: list[str] = []

            for audit in specs:
                if audit.resolution_error:
                    audit.missing_services = list(audit.required_services)
                    audit.failure_reasons.append(audit.resolution_error)
                    missing_binaries.append(audit.client)
                    errors.append(f"{audit.client}: {audit.resolution_error}")
                    records.append(audit.to_dict())
                    continue

                if (
                    not audit.target_path
                    or not audit.executable_path
                    or not Path(audit.target_path).exists()
                    or not Path(audit.executable_path).is_file()
                    or not os.access(audit.executable_path, os.X_OK)
                ):
                    reason = f"missing_or_non_executable_target({audit.executable_path or audit.target_path})"
                    audit.missing_services = list(audit.required_services)
                    audit.failure_reasons.append(reason)
                    missing_binaries.append(audit.client)
                    errors.append(f"{audit.client}: {reason}")
                    records.append(audit.to_dict())
                    continue

                placeholders = ",".join("?" for _ in audit.required_services)
                cursor.execute(
                    f"SELECT service, client_type, auth_value, csreq FROM access "  # noqa: S608
                    f"WHERE client = ? AND service IN ({placeholders})",
                    (audit.client, *audit.required_services),
                )
                rows_by_service: dict[str, list[tuple[Any, Any, Any]]] = {}
                for svc, c_type, auth_val, csreq_blob in cursor.fetchall():
                    rows_by_service.setdefault(str(svc), []).append((c_type, auth_val, csreq_blob))

                all_sigs_ok = True
                for req_svc in audit.required_services:
                    svc_rows = rows_by_service.get(req_svc, [])
                    if not svc_rows:
                        audit.missing_services.append(req_svc)
                        audit.failure_reasons.append(f"{req_svc}:missing_grant")
                        all_sigs_ok = False
                        continue

                    type_matched_rows = [r for r in svc_rows if r[0] == audit.client_type]
                    if not type_matched_rows:
                        observed_types = sorted({r[0] for r in svc_rows})
                        audit.missing_services.append(req_svc)
                        audit.failure_reasons.append(
                            f"{req_svc}:wrong_client_type(got={observed_types},expected={audit.client_type})"
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

                    svc_sig_ok = False
                    svc_sig_reason = "missing_csreq"
                    for _c_type, _auth_val, csreq_blob in allowed_rows:
                        sig_ok, sig_reason = evaluate_csreq_against_path(audit.target_path, csreq_blob)
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

                audit.signature_valid = all_sigs_ok and len(audit.granted_services) == len(audit.required_services)
                if not audit.failure_reasons and audit.signature_valid:
                    audit.verified = True
                    verified_binaries.append(audit.client)
                else:
                    audit.verified = False
                    missing_binaries.append(audit.client)
                    errors.append(f"{audit.client}: {', '.join(audit.failure_reasons)}")

                records.append(audit.to_dict())

            status = "CLEAN" if (verified_binaries and not missing_binaries and not errors) else "DRIFT"
            return _tcc_result(
                status,
                verified_binaries=verified_binaries,
                missing_binaries=missing_binaries,
                records=records,
                errors=errors,
            )
        finally:
            conn.close()
    except NativeSecurityError as exc:
        return _tcc_result("ERROR", reason=f"Native Security verification failed: {exc}")
    except (sqlite3.Error, OSError) as exc:
        return _tcc_result("ERROR", reason=f"TCC.db read failed: {exc}")


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
    parser.add_argument(
        "--bundles",
        action="store_true",
        help="Verify canonical client_type=0 bundle identities rather than ephemeral CLI realpaths.",
    )
    args = parser.parse_args(argv)

    result = verify_tcc_provenance(
        tcc_db_path=Path(args.db),
        binaries=args.binaries,
        include_python_automation=not args.no_python_automation if args.binaries is None else None,
        bundles=args.bundles,
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
