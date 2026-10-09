# Tasks

## 1. Ignore Policy

- [ ] 1.1 Add `!uv.lock` after the generic `*.lock` rule in `shb-schedule/.gitignore`; verify other runtime lock/database patterns remain unchanged.
- [ ] 1.2 Verify `uv.lock` becomes trackable while generated runtime lock files remain ignored using `git check-ignore`, `git ls-files`, and an isolated temporary runtime-state fixture.

## 2. Reproducible Installation

- [ ] 2.1 Run `uv sync --frozen --no-dev --no-editable` in `/Users/androidteam/Developer/shb/shb-schedule` without modifying `uv.lock`; record the exit status and lockfile hash.
- [ ] 2.2 Verify the Docker build context includes `uv.lock` and the existing multi-stage build can consume it without changing image versions or dependency declarations.

## 3. Final Verification and Delivery

- [ ] 3.1 Run the scheduler's relevant tests, type checks, and source lint checks; preserve unrelated Graphify output changes.
- [ ] 3.2 Inspect changed paths and commit only `.gitignore`, OpenSpec artifacts, and any explicitly required lockfile change; do not stage unrelated work or push.
- [ ] 3.3 Run strict validation for the change and verify apply instructions report all planning artifacts ready for implementation.
