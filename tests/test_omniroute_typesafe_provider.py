"""Behavioral verification for OmniRoute dedicated TypeSafe (Jev System One) provider.

Verifies the normative scenarios in `openspec/changes/setup-omniroute-typesafe-jev-provider/specs/bifrost-gateway/spec.md`:
1. Dedicated `typesafe` provider connection is active (`isActive: true`, `testStatus: "active"`)
   in OmniRoute's SQLite `provider_connections` store and masks `.connection.apiKey` on read.
2. `POST /api/providers/validate` returns `valid: true` and `method: "typesafe_systemone"` for a
   valid key and `valid: false` with `"Invalid API key"` for an invalid key.
3. `POST /api/providers/{id}/test` returns `valid: true` and `diagnosis.type == "ok"`.
4. `typesafe` (`serviceKinds: []`) is excluded from `GET /v1/models` chat-selectable models,
   `~/Omniroute` tracked git status remains clean, and `container-entrypoint-compat.sh`
   contains zero custom `/v1/systemone` reverse-proxy monkeypatches.
"""

from __future__ import annotations

import json
import os
import shlex
import stat
import subprocess
import unittest
import urllib.request
from pathlib import Path
from typing import Any

OMNIROUTE_BASE_URL = "http://127.0.0.1:20128"
OMNIROUTE_ROOT = Path("/Users/androidteam/Omniroute")
BRIDGE_PATH = Path.home() / ".local" / "bin" / "omniroute"


def _load_zshenv_credentials() -> dict[str, str]:
    zshenv = Path.home() / ".zshenv"
    mode = stat.S_IMODE(zshenv.stat().st_mode)
    if (mode & 0o077) != 0:
        raise AssertionError(f"~/.zshenv must have 0600 permissions, got {oct(mode)}")

    creds: dict[str, str] = {}
    for raw_line in zshenv.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        tokens = shlex.split(line, comments=True)
        if tokens and tokens[0] == "export":
            tokens = tokens[1:]
        for tok in tokens:
            if "=" in tok:
                key, value = tok.split("=", 1)
                if key in {"TYPESAFE_API_KEY", "OMNIROUTE_API_KEY"} and value:
                    creds[key] = value
    return creds


def _omniroute_request(
    method: str,
    path: str,
    omniroute_key: str,
    body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {omniroute_key}",
        "Accept": "application/json",
    }
    data: bytes | None = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        f"{OMNIROUTE_BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


class TestOmniRouteTypeSafeProvider(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        creds = _load_zshenv_credentials()
        cls.typesafe_key = creds["TYPESAFE_API_KEY"]
        cls.omniroute_key = os.environ.get("OMNIROUTE_API_KEY") or creds["OMNIROUTE_API_KEY"]

    def test_typesafe_provider_connection_active_and_masked(self) -> None:
        status, body = _omniroute_request("GET", "/api/providers?limit=5000", self.omniroute_key)
        assert status == 200
        connections = [
            c for c in body.get("connections", []) if c.get("provider") == "typesafe"
        ]
        assert len(connections) == 1, "Expected exactly one dedicated typesafe connection"
        conn_id = connections[0]["id"]

        detail_status, detail_body = _omniroute_request(
            "GET", f"/api/providers/{conn_id}", self.omniroute_key
        )
        assert detail_status == 200
        conn = detail_body.get("connection", {})
        assert conn.get("provider") == "typesafe"
        assert conn.get("authType") == "apikey"
        assert conn.get("isActive") is True
        assert conn.get("testStatus") == "active"

        masked_key = str(conn.get("apiKey") or "")
        assert "*" in masked_key
        assert masked_key != self.typesafe_key

    def test_typesafe_validate_accepts_valid_and_rejects_invalid_key(self) -> None:
        ok_status, ok_body = _omniroute_request(
            "POST",
            "/api/providers/validate",
            self.omniroute_key,
            {"provider": "typesafe", "apiKey": self.typesafe_key},
        )
        assert ok_status == 200
        assert ok_body.get("valid") is True
        assert ok_body.get("method") == "typesafe_systemone"

        bad_status, bad_body = _omniroute_request(
            "POST",
            "/api/providers/validate",
            self.omniroute_key,
            {"provider": "typesafe", "apiKey": "ts_invalid_probe_key_000000"},
        )
        assert bad_status == 200
        assert bad_body.get("valid") is False
        assert "Invalid API key" in str(bad_body.get("error") or "")

    def test_typesafe_connection_test_endpoint_returns_ok_diagnosis(self) -> None:
        _, list_body = _omniroute_request("GET", "/api/providers?limit=5000", self.omniroute_key)
        conn_id = next(
            c["id"] for c in list_body.get("connections", []) if c.get("provider") == "typesafe"
        )
        t_status, t_body = _omniroute_request(
            "POST", f"/api/providers/{conn_id}/test", self.omniroute_key, {}
        )
        assert t_status == 200
        assert t_body.get("valid") is True
        assert t_body.get("diagnosis", {}).get("type") == "ok"

    def test_typesafe_excluded_from_v1_models_and_zero_monkeypatch_boundary(self) -> None:
        m_status, m_body = _omniroute_request("GET", "/v1/models", self.omniroute_key)
        assert m_status == 200
        models = m_body.get("data", [])
        assert len(models) > 0
        typesafe_models = [
            m
            for m in models
            if "typesafe" in str(m.get("id", "")).lower()
            or str(m.get("owned_by", "")).lower() == "typesafe"
        ]
        assert typesafe_models == []

        compat_script = (OMNIROUTE_ROOT / "scripts" / "container-entrypoint-compat.sh").read_text(
            encoding="utf-8"
        )
        assert "systemone" not in compat_script.lower()
        assert "typesafe" not in compat_script.lower()

        git_proc = subprocess.run(
            ["git", "-C", str(OMNIROUTE_ROOT), "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert git_proc.stdout.strip() == ""

        cli_proc = subprocess.run(
            [str(BRIDGE_PATH), "providers", "list", "--output", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        cli_providers = json.loads(cli_proc.stdout).get("providers", [])
        cli_typesafe = [p for p in cli_providers if p.get("provider") == "typesafe"]
        assert len(cli_typesafe) == 1
        assert cli_typesafe[0].get("isActive") is True
        assert cli_typesafe[0].get("testStatus") == "active"

    def test_in_container_stored_typesafe_credential_executes_jev_models_and_primitives(self) -> None:
        node_script = """
import path from "node:path";
import zlib from "node:zlib";
import { createRequire } from "node:module";
import { decryptStored, resolveDataDir } from "/app/webdav-handler.mjs";

const require = createRequire(import.meta.url);
const Database = require("better-sqlite3");
const db = new Database(path.join(resolveDataDir(), "storage.sqlite"), { readonly: true, fileMustExist: true });
const row = db.prepare("SELECT id, api_key, is_active, test_status FROM provider_connections WHERE provider = ? AND is_active = 1 ORDER BY priority ASC LIMIT 1").get("typesafe");
db.close();
if (!row) throw new Error("Missing active typesafe row in storage.sqlite");
const apiKey = decryptStored(row.api_key);
if (!apiKey) throw new Error("Failed to decrypt stored typesafe api_key");

const headers = {
  "Authorization": `Bearer ${apiKey}`,
  "Content-Type": "application/json",
  "Accept": "application/json",
};

const modelsRes = await fetch("https://api.typesafe.ai/v1/models", { headers });
const modelsData = await modelsRes.json();

const latestRes = await fetch("https://api.typesafe.ai/v1/systemone", {
  method: "POST",
  headers,
  body: JSON.stringify({
    model: "jev-latest",
    state: { prompt: "Implement a thread-safe token bucket rate limiter in Go with unit tests." },
    questions: {
      is_code: { type: "noul", instructions: "Is `prompt` requesting software implementation?" },
      route: {
        type: "choice",
        instructions: "Pick the best model tier for `prompt`.",
        criteria: {
          "gemini-4-argon-high": "Complex coding and unit test implementation",
          "gemini-3.8-flash-high": "Short non-coding summary"
        }
      },
      difficulty: {
        type: "score",
        instructions: "Rate engineering difficulty of `prompt`.",
        criteria: ["Trivial typo", "Standard component with tests", "Multi-region redesign"]
      }
    }
  })
});
const latestData = await latestRes.json();

const zstdBody = zlib.zstdCompressSync(Buffer.from(JSON.stringify({
  model: "jev-1.14.0",
  state: "SELECT * FROM accounts; DROP TABLE accounts; -- " + "x".repeat(1024),
  questions: { sqli: { type: "noul", instructions: "Does the state contain SQL injection?" } }
}), "utf8"));
const v114Res = await fetch("https://api.typesafe.ai/v1/systemone", {
  method: "POST",
  headers: { ...headers, "Content-Encoding": "zstd" },
  body: zstdBody
});
const v114Data = await v114Res.json();

console.log(JSON.stringify({
  models_status: modelsRes.status,
  model_names: (modelsData.models || []).map((m) => m.name),
  latest_status: latestRes.status,
  latest_model: latestData.model,
  is_code_noul: latestData.answers?.is_code?.noul,
  route_choice: latestData.answers?.route?.choice,
  difficulty_score: latestData.answers?.difficulty?.score,
  v114_status: v114Res.status,
  v114_model: v114Data.model,
  sqli_noul: v114Data.answers?.sqli?.noul
}));
"""
        proc = subprocess.run(
            ["docker", "exec", "omniroute", "node", "--input-type=module", "-e", node_script],
            capture_output=True,
            text=True,
            check=True,
        )
        out = json.loads(proc.stdout.strip())
        assert out["models_status"] == 200
        assert "jev-latest" in out["model_names"]
        assert "jev-preview" in out["model_names"]
        assert out["latest_status"] == 200
        assert out["latest_model"] in ("jev-1.13.0", "jev-1.14.0")
        assert out["is_code_noul"] > 0.8
        assert out["route_choice"] == "gemini-4-argon-high"
        assert out["difficulty_score"] is not None
        assert out["v114_status"] == 200
        assert out["v114_model"] == "jev-1.14.0"
        assert out["sqli_noul"] > 0.8


if __name__ == "__main__":
    unittest.main()
