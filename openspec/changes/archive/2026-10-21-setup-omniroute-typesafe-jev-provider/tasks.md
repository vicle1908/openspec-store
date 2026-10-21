# Tasks

## 1. Provision and Validate Dedicated `typesafe` Provider Connection in OmniRoute

- [x] 1.1 Validate `TYPESAFE_API_KEY` from `~/.zshenv` (`mode 0600`) via `POST http://127.0.0.1:20128/api/providers/validate` (`valid: true`, `method: "typesafe_systemone"`) and idempotently provision the dedicated `typesafe` (`provider: "typesafe"`, `name: "typesafe-primary"`, `priority: 1`) connection via `POST http://127.0.0.1:20128/api/providers` with `Authorization: Bearer $OMNIROUTE_API_KEY` and `x-skip-model-sync: true` (calling the HTTP endpoints directly rather than un-intercepted `omniroute providers add/test` CLI subcommands, and never echoing or logging any secret value).
- [x] 1.2 Poll `GET http://127.0.0.1:20128/api/providers/{id}` (up to 3s for the creation auto-test to settle, falling back to `POST http://127.0.0.1:20128/api/providers/{id}/test` and asserting `valid: true` and `diagnosis.type: "ok"`) and verify `.connection.provider === "typesafe"`, `.connection.isActive === true`, `.connection.testStatus === "active"`, and `.connection.apiKey` is masked (`"***"`).

## 2. Verify Zero-Customization & Specialty Provider Boundaries

- [x] 2.1 Verify via `GET http://127.0.0.1:20128/v1/models` and `git -C /Users/androidteam/Omniroute status --porcelain` that `typesafe` (`serviceKinds: []`) does not advertise chat-selectable models in `/v1/models`, `~/Omniroute` tracked files remain clean, and `~/Omniroute/scripts/container-entrypoint-compat.sh` contains zero custom `/v1/systemone` reverse-proxy hooks.
- [x] 2.2 Create `/Users/androidteam/Developer/platform/openspec-store/tests/test_omniroute_typesafe_provider.py` and run `uv run pytest /Users/androidteam/Developer/platform/openspec-store/tests/test_omniroute_typesafe_provider.py -v` to verify the active `typesafe` connection, value-blind credential hygiene, `/v1/models` exclusion invariant, and zero-monkeypatch boundary.
