# Tasks

## 1. Ignore Policy

- [x] 1.1 Add `!uv.lock` after the generic `*.lock` rule in `shb-schedule/.gitignore`; verify other runtime lock/database patterns remain unchanged.
- [x] 1.2 Verify `uv.lock` becomes trackable while generated runtime lock files remain ignored using `git check-ignore`, `git ls-files`, and an isolated temporary runtime-state fixture.

## 2. Reproducible Installation

- [x] 2.1 Run `uv sync --frozen --no-dev --no-editable` in `/Users/androidteam/Developer/shb/shb-schedule` without modifying `uv.lock`; record the exit status and lockfile hash.
- [x] 2.2 Verify the Docker build context includes `uv.lock` and the existing multi-stage build can consume it without changing image versions or dependency declarations.

## 3. Final Verification and Delivery

- [x] 3.1 Fix the seven diagnosed runtime-source Ruff issues approved during apply; preserve reload task lifetime, reloader encapsulation, ownership, and permissions. Run `uv lock --check`, scheduler tests, mypy, source lint, and isolated CLI/container smoke checks; preserve unrelated Graphify outputs and the lockfile hash.
- [ ] 3.2 Inspect changed paths and commit only `.gitignore`, unchanged `uv.lock`, the four scoped source files, related behavior regression tests/documentation, and this change's OpenSpec artifacts. Verify a fresh local checkout retains the exact lockfile. Do not stage unrelated work or push.
- [ ] 3.3 Run strict validation for the change and verify apply instructions report all implementation tasks complete (`all_done`).
