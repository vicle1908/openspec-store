# Evidence: `setup-omniroute-typesafe-jev-provider`

## 1. Dedicated `typesafe` Provider Provisioning & Validation (`Tasks 1.1 & 1.2`)

- **Credential Source**: `~/.zshenv` verified `mode 0600` (`0o600`), parsed in memory via `shlex.split(line, comments=True)` without echoing or logging any plaintext secret value.
- **Validation Probe (`POST http://127.0.0.1:20128/api/providers/validate`)**:
  - Valid `TYPESAFE_API_KEY`: `HTTP 200`, `{"valid": true, "method": "typesafe_systemone"}`.
  - Invalid probe key (`ts_invalid_probe_key_000000`): `HTTP 200`, `{"valid": false, "error": "Invalid API key"}`.
- **Provisioning (`POST http://127.0.0.1:20128/api/providers` with `x-skip-model-sync: true`)**:
  - Created dedicated connection ID `f21a6be2-fef5-45ca-a881-6716ab87f48a` (`provider: "typesafe"`, `name: "typesafe-primary"`, `authType: "apikey"`, `priority: 1`).
  - Background creation auto-test settled during the 3-second `GET /api/providers/{id}` poll without racing a duplicate test request.
- **Active Health & Masked Credential Verification (`GET /api/providers/f21a6be2-fef5-45ca-a881-6716ab87f48a` & `POST /api/providers/f21a6be2-fef5-45ca-a881-6716ab87f48a/test`)**:
  - `GET /api/providers/f21a6be2-fef5-45ca-a881-6716ab87f48a`: `.connection.provider === "typesafe"`, `.connection.isActive === true`, `.connection.testStatus === "active"`, `.connection.apiKey` masked (`length: 16`, contains `"*"`, does not equal raw key).
  - `POST /api/providers/f21a6be2-fef5-45ca-a881-6716ab87f48a/test`: `HTTP 200`, `valid: true`, `diagnosis.type: "ok"`, `latencyMs: 439`.
  - `~/.local/bin/omniroute providers list --output json`: includes `{"id": "f21a6be2-fef5-45ca-a881-6716ab87f48a", "provider": "typesafe", "name": "typesafe-primary", "authType": "apikey", "isActive": true, "testStatus": "active"}`.

## 2. Specialty Provider & Zero-Customization Boundary Verification (`Tasks 2.1 & 2.2`)

- **Chat Model Catalog Exclusion (`GET http://127.0.0.1:20128/v1/models`)**:
  - `1292` total models returned; `0` models with `id` or `owned_by` matching `typesafe` (`serviceKinds: []` invariant preserved).
- **Zero-Monkeypatch & Git Cleanliness Invariant (`/Users/androidteam/Omniroute`)**:
  - `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` returned empty output (`0` modified tracked files).
  - `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` contains `0` occurrences of `systemone` or `typesafe`.
- **Automated Test Suites**:
  - `uv run pytest /Users/androidteam/Developer/platform/openspec-store/tests/test_omniroute_typesafe_provider.py /Users/androidteam/Developer/platform/openspec-store/tests/test_omniroute_cli_bridge.py -v`: `11 passed in 7.22s` (`4 passed` in `test_omniroute_typesafe_provider.py`, `7 passed` in `test_omniroute_cli_bridge.py`).
  - `openspec validate "setup-omniroute-typesafe-jev-provider" --strict --json --store openspec-store`: `valid: true` (`0` issues).
