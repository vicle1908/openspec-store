"""Behavioral tests for ~/.local/bin/omniroute host CLI bridge.

Verifies:
1. `omniroute status` queries live remote daemon health (`/api/monitoring/health`
   and `/api/omniroute/status`), resolves package version from `/Users/androidteam/Omniroute`,
   normalizes `localhost` and trailing `/v1`, and never reports the ephemeral local
   bridge SQLite DB as daemon proof.
2. `omniroute status` fails closed when the daemon is unreachable (exit 3),
   unauthorized (exit 4), degraded (exit 1), or invoked with unsupported flags/output
   formats (exit 2).
3. `omniroute keys list` queries canonical `/api/providers?limit=5000`, preserves
   upstream provider-key semantics (`authType == "apikey"` with stored credential),
   never conflates gateway API keys (`/api/keys`), and strictly masks credentials
   even if a remote server returns unmasked or short keys.
4. `omniroute keys list` fails closed when `/api/providers` is unsupported (HTTP 404 -> exit 2)
   or when the daemon is offline (exit 3) instead of falling back to the empty
   ephemeral local SQLite database.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

BRIDGE_PATH = Path.home() / ".local" / "bin" / "omniroute"
OMNIROUTE_ROOT = Path("/Users/androidteam/Omniroute")


class _MockOmniRouteServer:
    def __init__(self) -> None:
        self.requests: list[tuple[str, str, dict[str, str]]] = []
        self.health_status_code = 200
        self.health_payload: dict[str, Any] = {
            "status": "healthy",
            "version": "3.8.51",
            "uptime": 1234.5,
            "setupComplete": True,
            "system": {
                "version": "3.8.51",
                "nodeVersion": "v26.10.0",
                "uptime": 1234.5,
                "pid": 27,
                "platform": "linux",
            },
            "providerSummary": {
                "catalogCount": 358,
                "configuredCount": 3,
                "activeCount": 2,
                "monitoredCount": 2,
            },
            "circuitBreakers": {"open": 0, "halfOpen": 0, "closed": 2, "total": 2},
        }
        self.omniroute_status_code = 200
        self.omniroute_status_payload: dict[str, Any] = {
            "generatedAt": "2026-10-19T05:00:00.000Z",
            "liveRequestExecuted": False,
            "gateway": "healthy",
            "catalog": {"available": True},
            "providers": {
                "configured": 3,
                "active": 2,
                "healthy": 2,
                "disabled": 1,
                "connections": [],
            },
            "pools": {"count": 1, "allocations": 2, "items": []},
            "circuits": {"open": 0, "halfOpen": 0, "closed": 2},
        }
        self.providers_status_code = 200
        self.providers_payload: dict[str, Any] = {
            "total": 5,
            "connections": [
                {
                    "id": "conn-11111111",
                    "provider": "openrouter",
                    "name": "main-or",
                    "authType": "apikey",
                    "isActive": True,
                    "apiKey": "sk-or-v1****99aa",
                },
                {
                    "id": "conn-22222222",
                    "provider": "voyage-ai",
                    "name": "unmasked-server-test",
                    "authType": "apikey",
                    "isActive": False,
                    "apiKey": "pa-raw-secret-value-1234567890abcd",
                },
                {
                    "id": "conn-33333333",
                    "provider": "jina-ai",
                    "name": "short-key-test",
                    "authType": "apikey",
                    "isActive": True,
                    "apiKey": "shortkey****tkey",
                },
                {
                    "id": "conn-44444444",
                    "provider": "empty-apikey-provider",
                    "name": "no-key",
                    "authType": "apikey",
                    "isActive": True,
                },
                {
                    "id": "conn-55555555",
                    "provider": "codex",
                    "name": "oauth-conn",
                    "authType": "oauth",
                    "isActive": True,
                },
            ],
        }

        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                headers = {k.lower(): v for k, v in self.headers.items()}
                outer.requests.append((self.command, self.path, headers))
                if self.path.startswith("/api/monitoring/health"):
                    self._send_json(outer.health_status_code, outer.health_payload)
                elif self.path.startswith("/api/omniroute/status"):
                    self._send_json(
                        outer.omniroute_status_code, outer.omniroute_status_payload
                    )
                elif self.path.startswith("/api/providers"):
                    self._send_json(outer.providers_status_code, outer.providers_payload)
                elif self.path.startswith("/api/health"):
                    self._send_json(200, {"status": "ok"})
                else:
                    self._send_json(404, {"error": "Not found"})

            def _send_json(self, status: int, data: dict[str, Any]) -> None:
                raw = json.dumps(data).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def log_message(self, fmt: str, *args: object) -> None:
                return

        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    def __enter__(self) -> _MockOmniRouteServer:
        self._thread.start()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        self._thread.join(timeout=2)


def _find_unused_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _run_bridge(
    args: list[str],
    *,
    cwd: Path | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("OMNIROUTE_CONTEXT", None)
    env["OMNIROUTE_API_KEY"] = "test-management-token"
    env["OMNIROUTE_KEY"] = "test-management-token"
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [str(BRIDGE_PATH), *args],
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )


class TestOmniRouteCliBridge(unittest.TestCase):
    def test_status_json_reports_remote_daemon_health_and_upstream_version(self) -> None:
        expected_pkg_version = json.loads(
            (OMNIROUTE_ROOT / "package.json").read_text(encoding="utf-8")
        )["version"]

        with _MockOmniRouteServer() as server, tempfile.TemporaryDirectory() as tmp_cwd:
            res = _run_bridge(
                [
                    "status",
                    "--output",
                    "json",
                    "--base-url",
                    f"http://localhost:{server.port}/v1/",
                ],
                cwd=Path(tmp_cwd),
            )
            assert res.returncode == 0, res.stderr
            assert res.stderr == ""
            payload = json.loads(res.stdout)
            assert payload["status"] == "healthy"
            assert payload["gateway"] == "healthy"
            assert payload["version"] == "3.8.51"
            assert payload["cliVersion"] == expected_pkg_version
            assert payload["baseUrl"] == f"http://127.0.0.1:{server.port}"
            assert payload["database"] == {"status": "healthy", "connected": True, "source": "remote"}
            assert payload["providers"] == {"configured": 3, "active": 2, "healthy": 2, "disabled": 1}
            paths = [p for _, p, _ in server.requests]
            assert "/api/monitoring/health" in paths
            assert "/api/omniroute/status" in paths

    def test_status_fails_closed_when_daemon_unreachable(self) -> None:
        dead_port = _find_unused_port()
        res = _run_bridge(
            ["status", "--output", "json", "--base-url", f"http://127.0.0.1:{dead_port}"]
        )
        assert res.returncode == 3
        assert res.stdout.strip() == ""
        assert "unreachable" in res.stderr.lower()

    def test_status_fails_closed_on_degraded_gateway_or_unauthorized(self) -> None:
        with _MockOmniRouteServer() as server:
            server.omniroute_status_payload["gateway"] = "degraded"
            res = _run_bridge(
                [
                    "status",
                    "--output",
                    "json",
                    "--base-url",
                    f"http://127.0.0.1:{server.port}",
                ]
            )
            assert res.returncode == 1
            payload = json.loads(res.stdout)
            assert payload["gateway"] == "degraded"
            assert not payload["database"]["connected"]

            server.omniroute_status_code = 401
            server.omniroute_status_payload = {"error": "Invalid management token"}
            res_unauth = _run_bridge(
                [
                    "status",
                    "--output",
                    "json",
                    "--base-url",
                    f"http://127.0.0.1:{server.port}",
                ]
            )
            assert res_unauth.returncode == 4
            assert res_unauth.stdout.strip() == ""
            assert "401" in res_unauth.stderr

    def test_status_rejects_unsupported_output_and_unknown_flags(self) -> None:
        for bad_args in (
            ["status", "--output", "csv"],
            ["status", "--output", "jsonl"],
            ["status", "--unknown-flag"],
            ["status", "extra-arg"],
        ):
            res = _run_bridge(bad_args)
            assert res.returncode == 2, f"args={bad_args} stderr={res.stderr}"
            assert res.stdout.strip() == ""

    def test_keys_list_filters_apikey_connections_and_masks_strictly(self) -> None:
        with _MockOmniRouteServer() as server:
            res = _run_bridge(
                [
                    "keys",
                    "list",
                    "--output",
                    "json",
                    "--base-url",
                    f"http://localhost:{server.port}/v1",
                ]
            )
            assert res.returncode == 0, res.stderr
            assert "pa-raw-secret-value-1234567890abcd" not in res.stdout
            assert "shortkey" not in res.stdout
            data = json.loads(res.stdout)
            keys = data["keys"]
            assert len(keys) == 3
            assert keys[0] == {"id": "conn-11111111", "provider": "openrouter", "name": "main-or", "isActive": True, "maskedKey": "sk-or-***99aa"}
            assert keys[1] == {"id": "conn-22222222", "provider": "voyage-ai", "name": "unmasked-server-test", "isActive": False, "maskedKey": "pa-raw***abcd"}
            assert keys[2] == {"id": "conn-33333333", "provider": "jina-ai", "name": "short-key-test", "isActive": True, "maskedKey": "***"}
            paths = [p for _, p, _ in server.requests]
            assert "/api/providers?limit=5000" in paths
            assert not any(p.startswith("/api/keys") for p in paths)

    def test_keys_list_fails_closed_on_404_or_offline_without_local_db_fallback(self) -> None:
        with _MockOmniRouteServer() as server:
            server.providers_status_code = 404
            server.providers_payload = {"error": "Not found"}
            res_404 = _run_bridge(
                [
                    "keys",
                    "list",
                    "--output",
                    "json",
                    "--base-url",
                    f"http://127.0.0.1:{server.port}",
                ]
            )
            assert res_404.returncode == 2
            assert res_404.stdout.strip() == ""
            assert "not supported" in res_404.stderr.lower()

        dead_port = _find_unused_port()
        res_offline = _run_bridge(
            ["keys", "list", "--output", "json", "--base-url", f"http://127.0.0.1:{dead_port}"]
        )
        assert res_offline.returncode == 3
        assert res_offline.stdout.strip() == ""
        assert "unreachable" in res_offline.stderr.lower()

    def test_providers_list_formats_table_and_json_and_fails_closed(self) -> None:
        with _MockOmniRouteServer() as server:
            # 1. JSON output
            res_json = _run_bridge(
                ["providers", "list", "--output", "json", "--base-url", f"http://127.0.0.1:{server.port}"]
            )
            assert res_json.returncode == 0, res_json.stderr
            data = json.loads(res_json.stdout)
            assert "providers" in data
            providers = data["providers"]
            assert len(providers) == 5
            assert providers[0]["id"] == "conn-11111111"
            assert providers[0]["provider"] == "openrouter"
            assert providers[0]["name"] == "main-or"
            assert providers[4]["provider"] == "codex"
            assert providers[4]["authType"] == "oauth"
            assert providers[0]["testStatus"] == "unknown"
            assert "apiKey" not in providers[0]
            assert "maskedKey" not in providers[0]

            # 2. Table output
            res_table = _run_bridge(
                ["providers", "list", "--base-url", f"http://127.0.0.1:{server.port}"]
            )
            assert res_table.returncode == 0, res_table.stderr
            assert "OmniRoute Providers" in res_table.stdout
            assert "conn-111" in res_table.stdout
            assert "openrouter" in res_table.stdout

            # 3. 404 failure
            server.providers_status_code = 404
            server.providers_payload = {"error": "Not found"}
            res_404 = _run_bridge(
                ["providers", "list", "--base-url", f"http://127.0.0.1:{server.port}"]
            )
            assert res_404.returncode == 2
            assert "not supported" in res_404.stderr.lower()

        # 4. Offline failure
        dead_port = _find_unused_port()
        res_offline = _run_bridge(
            ["providers", "list", "--base-url", f"http://127.0.0.1:{dead_port}"]
        )
        assert res_offline.returncode == 3
        assert "unreachable" in res_offline.stderr.lower()

    def test_passthrough_commands_emit_zero_env_shadow_warnings_on_stderr(self) -> None:
        with _MockOmniRouteServer() as server:
            res_ver = _run_bridge(["--version"], cwd=OMNIROUTE_ROOT)
            assert res_ver.returncode == 0, res_ver.stderr
            assert "is ignored" not in res_ver.stdout
            assert "is ignored" not in res_ver.stderr
            assert "Loaded env from" not in res_ver.stdout
            assert "Loaded env from" not in res_ver.stderr

            res_health = _run_bridge(
                ["health", "--json", "--base-url", f"http://127.0.0.1:{server.port}"],
                cwd=OMNIROUTE_ROOT,
            )
            assert res_health.returncode == 0, res_health.stderr
            assert "is ignored" not in res_health.stdout
            assert "is ignored" not in res_health.stderr
            assert "Loaded env from" not in res_health.stdout
            assert "Loaded env from" not in res_health.stderr


if __name__ == "__main__":
    unittest.main()
