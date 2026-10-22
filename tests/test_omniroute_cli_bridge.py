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

            def log_message(self, format: str, *args: object) -> None:
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
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            self.assertEqual(res.stderr, "")
            payload = json.loads(res.stdout)
            self.assertEqual(payload["status"], "healthy")
            self.assertEqual(payload["gateway"], "healthy")
            self.assertEqual(payload["version"], "3.8.51")
            self.assertEqual(payload["cliVersion"], expected_pkg_version)
            self.assertEqual(payload["baseUrl"], f"http://127.0.0.1:{server.port}")
            self.assertEqual(
                payload["database"],
                {"status": "healthy", "connected": True, "source": "remote"},
            )
            self.assertEqual(
                payload["providers"],
                {"configured": 3, "active": 2, "healthy": 2, "disabled": 1},
            )
            paths = [p for _, p, _ in server.requests]
            self.assertIn("/api/monitoring/health", paths)
            self.assertIn("/api/omniroute/status", paths)

    def test_status_fails_closed_when_daemon_unreachable(self) -> None:
        dead_port = _find_unused_port()
        res = _run_bridge(
            ["status", "--output", "json", "--base-url", f"http://127.0.0.1:{dead_port}"]
        )
        self.assertEqual(res.returncode, 3)
        self.assertEqual(res.stdout.strip(), "")
        self.assertIn("unreachable", res.stderr.lower())

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
            self.assertEqual(res.returncode, 1)
            payload = json.loads(res.stdout)
            self.assertEqual(payload["gateway"], "degraded")
            self.assertFalse(payload["database"]["connected"])

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
            self.assertEqual(res_unauth.returncode, 4)
            self.assertEqual(res_unauth.stdout.strip(), "")
            self.assertIn("401", res_unauth.stderr)

    def test_status_rejects_unsupported_output_and_unknown_flags(self) -> None:
        for bad_args in (
            ["status", "--output", "csv"],
            ["status", "--output", "jsonl"],
            ["status", "--unknown-flag"],
            ["status", "extra-arg"],
        ):
            res = _run_bridge(bad_args)
            self.assertEqual(res.returncode, 2, msg=f"args={bad_args} stderr={res.stderr}")
            self.assertEqual(res.stdout.strip(), "")

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
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            self.assertNotIn("pa-raw-secret-value-1234567890abcd", res.stdout)
            self.assertNotIn("shortkey", res.stdout)
            data = json.loads(res.stdout)
            keys = data["keys"]
            self.assertEqual(len(keys), 3)
            self.assertEqual(
                keys[0],
                {
                    "id": "conn-11111111",
                    "provider": "openrouter",
                    "name": "main-or",
                    "isActive": True,
                    "maskedKey": "sk-or-***99aa",
                },
            )
            self.assertEqual(
                keys[1],
                {
                    "id": "conn-22222222",
                    "provider": "voyage-ai",
                    "name": "unmasked-server-test",
                    "isActive": False,
                    "maskedKey": "pa-raw***abcd",
                },
            )
            self.assertEqual(
                keys[2],
                {
                    "id": "conn-33333333",
                    "provider": "jina-ai",
                    "name": "short-key-test",
                    "isActive": True,
                    "maskedKey": "***",
                },
            )
            paths = [p for _, p, _ in server.requests]
            self.assertIn("/api/providers?limit=5000", paths)
            self.assertFalse(any(p.startswith("/api/keys") for p in paths))

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
            self.assertEqual(res_404.returncode, 2)
            self.assertEqual(res_404.stdout.strip(), "")
            self.assertIn("not supported", res_404.stderr.lower())

        dead_port = _find_unused_port()
        res_offline = _run_bridge(
            ["keys", "list", "--output", "json", "--base-url", f"http://127.0.0.1:{dead_port}"]
        )
        self.assertEqual(res_offline.returncode, 3)
        self.assertEqual(res_offline.stdout.strip(), "")
        self.assertIn("unreachable", res_offline.stderr.lower())

    def test_providers_list_formats_table_and_json_and_fails_closed(self) -> None:
        with _MockOmniRouteServer() as server:
            # 1. JSON output
            res_json = _run_bridge(
                ["providers", "list", "--output", "json", "--base-url", f"http://127.0.0.1:{server.port}"]
            )
            self.assertEqual(res_json.returncode, 0, msg=res_json.stderr)
            data = json.loads(res_json.stdout)
            self.assertIn("providers", data)
            providers = data["providers"]
            self.assertEqual(len(providers), 5)
            self.assertEqual(providers[0]["id"], "conn-11111111")
            self.assertEqual(providers[0]["provider"], "openrouter")
            self.assertEqual(providers[0]["name"], "main-or")
            self.assertEqual(providers[4]["provider"], "codex")
            self.assertEqual(providers[4]["authType"], "oauth")
            self.assertEqual(providers[0]["testStatus"], "unknown")
            self.assertNotIn("apiKey", providers[0])
            self.assertNotIn("maskedKey", providers[0])

            # 2. Table output
            res_table = _run_bridge(
                ["providers", "list", "--base-url", f"http://127.0.0.1:{server.port}"]
            )
            self.assertEqual(res_table.returncode, 0, msg=res_table.stderr)
            self.assertIn("OmniRoute Providers", res_table.stdout)
            self.assertIn("conn-111", res_table.stdout)
            self.assertIn("openrouter", res_table.stdout)

            # 3. 404 failure
            server.providers_status_code = 404
            server.providers_payload = {"error": "Not found"}
            res_404 = _run_bridge(
                ["providers", "list", "--base-url", f"http://127.0.0.1:{server.port}"]
            )
            self.assertEqual(res_404.returncode, 2)
            self.assertIn("not supported", res_404.stderr.lower())

        # 4. Offline failure
        dead_port = _find_unused_port()
        res_offline = _run_bridge(
            ["providers", "list", "--base-url", f"http://127.0.0.1:{dead_port}"]
        )
        self.assertEqual(res_offline.returncode, 3)
        self.assertIn("unreachable", res_offline.stderr.lower())

    def test_passthrough_commands_emit_zero_env_shadow_warnings_on_stderr(self) -> None:
        with _MockOmniRouteServer() as server:
            res_ver = _run_bridge(["--version"], cwd=OMNIROUTE_ROOT)
            self.assertEqual(res_ver.returncode, 0, msg=res_ver.stderr)
            self.assertNotIn("is ignored", res_ver.stdout)
            self.assertNotIn("is ignored", res_ver.stderr)
            self.assertNotIn("Loaded env from", res_ver.stdout)
            self.assertNotIn("Loaded env from", res_ver.stderr)

            res_health = _run_bridge(
                ["health", "--json", "--base-url", f"http://127.0.0.1:{server.port}"],
                cwd=OMNIROUTE_ROOT,
            )
            self.assertEqual(res_health.returncode, 0, msg=res_health.stderr)
            self.assertNotIn("is ignored", res_health.stdout)
            self.assertNotIn("is ignored", res_health.stderr)
            self.assertNotIn("Loaded env from", res_health.stdout)
            self.assertNotIn("Loaded env from", res_health.stderr)


if __name__ == "__main__":
    unittest.main()
