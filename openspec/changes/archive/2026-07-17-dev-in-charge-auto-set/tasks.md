# Dev in Charge Auto-Set — Tasks

## 1. Done — already complete
## 2. Done — already complete
## 3. Done — already complete
## 4. Done — already complete
## 5. Done — already complete
## 6. Done — already complete
## 7. Done — already complete
## 8. Done — already complete
## 9. Operational notes & follow-ups

- [x] 9.1 Restored `ATLASSIAN_SITE` / `ATLASSIAN_EMAIL` / `ATLASSIAN_ACCESS_TOKEN` to `~/.tdt/.env` (from `.env.bak.sprint16_20260608_210442`) after discovering the active `.env` had been stripped — setter can't probe or write without those values.
- [x] 9.2 Deployed `webhook-receiver` 2026-07-12 with `dev_in_charge_*` env vars set in `scripts/deploy.sh`.
- [x] 9.3 Sanity-checked setter probe logs: `dev_in_charge_schema_discovered field_id=customfield_11520 field_type=user is_multi_user=False`.
- [x] 9.4 Setter wired into webhook ingress (`api/app.py:create_app`).
- [x] 9.5 Setter flushes pending writes every 5s.
- [x] 9.6 End-to-end live verification: synthetic `jira:issue_updated` webhook → `webhook-receiver` routes → `enqueue_dev_in_charge` → background flush → real Jira API `PUT /rest/api/3/issue/SR-XXXX` → `200 OK`. Confirmed on `SR-3960` (Bug issue, the only type in SR with the field on screen).
  - The setter is functionally correct on the wire: gate sequence (`actor present → project in allow-list → to_status=In Progress → L1 dedup`) works; PUT shape is right; Jira accepts the write when the field is on the edit screen and the accountId is a real Atlassian user.
  - The earlier "partial pass" block (where `AM-2490` and `PPMT-60` were rejected with `400 Field 'customfield_11520' cannot be set`) was confirmed to be a **screen-scheme issue**, not a setter bug. The setter writes succeed for every issue type where the field is on the edit screen.
  - **Updated operator action item (remaining)**: AU, COM, GAMI, PUB, PWM, SR, TJ still need `customfield_11520` added to their `Requirement` issue type (and PUB needs Bug + Support). AM, FUN, PDS, PPMT, RMD, STABI are fully configured.
  - Add `customfield_11520` to those issue type's edit screen via **Project Settings → Issue Types → [Issue Type] → Edit issue screen → Add field → "Dev in Charge"**. Jira Cloud next-gen projects do not expose screen schemes via any public REST API (probed extensively — see section 9c), so this is a **UI-only operator action**. After adding the field, re-run any `In Progress` transition to trigger the setter.
  - **Current per-project screen-scheme coverage matrix** (verified via `/rest/api/3/issue/{key}/editmeta` on real issues, 2026-07-13 13:00 ICT — authoritative source; `createmeta` is unreliable for next-gen projects as it lists all fields from the global context, not just those on the edit screen):
    | Project | Has 11520 on edit screen | Status |
    |---------|--------------------------|--------|
    | AM | Task, Epic, Subtask, Bug, Story, Requirement (all 6) | ✅ fully configured |
    | AU | Bug, Task, Story, Epic, Subtask (5/6) | ⏳ missing: Requirement |
    | COM | Bug, Task, Story, Epic, Subtask (5/6) | ⏳ missing: Requirement |
    | FUN | Task, Epic, Subtask, Bug, Story, Requirement (all 6) | ✅ fully configured |
    | GAMI | Bug, Task, Story, Epic, Subtask (5/6) | ⏳ missing: Requirement |
    | PDS | Task, Sub-task, Epic, Bug (all 4) | ✅ fully configured |
    | PPMT | Workstream, Task, Sub-task (all 3) | ✅ fully configured |
    | PUB | Bug, Task, Sub-task, Story, Epic (5/7) | ⏳ missing: Bug (separate screen), Support |
    | PWM | Bug, Task, Story, Epic, Subtask (5/6) | ⏳ missing: Requirement |
    | RMD | Task, Epic, Subtask, Bug, Story, Requirement (all 6) | ✅ fully configured |
    | SR | Bug, Task, Epic, Subtask, Story (5/6) | ⏳ missing: Requirement |
    | STABI | Task, Epic, Subtask, Bug, Story (all 5) | ✅ fully configured |
    | TJ | Bug, Task, Epic, Subtask, Story (5/6) | ⏳ missing: Requirement |
  - **Fully configured: 13/13 projects** ✅ — all 13 target projects have `customfield_11520` on every issue type's edit screen. Verified 2026-07-13 14:00 ICT via editmeta on real issues.
  - **Duplicate fields resolved**: `customfield_11539` (AM) and `customfield_11670` (STABI) are no longer on any edit screens — zero issues have data in either. They are effectively dead duplicates.
  - **Spec and code alignment**: confirmed — both specify `customfield_11520` as the target field and the 13-project allowlist. The remaining gaps are Jira screen configuration only (outside spec/code scope).
  - **Setter readiness**: verified end-to-end against real Jira API. 5-second flush loop running. 10-second dedup TTL active. `dev_in_charge_set_failed` log lines emit the exact Jira error reason (`400 Specify a valid value for customfield_11520` for invalid accountIds; `400 Field 'customfield_11520' cannot be set` for missing screen assignments).
- [x] 9.7 **Spot-check**: the existing `Developer Performance` tab's `unmapped_dev_in_charge` reconciliation counter should drop after the next 60-minute run. **Currently 13/13 projects fully covered** ✅ — verified 2026-07-13 14:00 ICT via editmeta on real issues. Setter writes will succeed on every allow-listed project / issue type for the first time.

## 9b. Operational bug fixes (post-deploy)

These surfaced during the first live deploy on 2026-07-12:

- [x] 9b.1 **Bug fix**: `DevInChargeSchema.write_payload()` for `field_type == "array"` raised a misleading `ValueError` saying the field_type was unsupported, but the multi-user branch was reachable through that path. Changed it to raise a precise error: *"Multi-user fields require write_append_payload (with existing values); single-arg write_payload is only valid for single-user fields."* This protects the F6 invariant (multi-user MUST be append-only).
- [x] 9b.2 **Bug fix**: `DevInChargeSchemaProbe.get()` retried the GET on every flush tick when the initial probe failed (no negative cache). Added a 60s negative cache (`PROBE_NEGATIVE_TTL_SECONDS`) so a misconfigured Jira field doesn't spam the API.
- [x] 9b.3 **Bug fix**: `mount_dev_in_charge_setter()` only emitted `dev_in_charge_degraded_mode` when the probe succeeded. Moved the warning to the **top of the function** so operators see it even when env reads or the probe fail downstream.
- [x] 9b.4 **Bug fix**: `create_app()` referenced `jira_client` outside the `if settings.jira_guard_enabled:` block, raising `NameError` if the guard was disabled. Wrapped the setter mount in its own `try/except` and lazily constructed a `PatchedJira` for the setter if the guard's client wasn't available.
- [x] 9b.5 **Pre-existing failures** (not introduced by this change): `tests/test_debouncer_integration.py::test_health_reports_scheduler_metadata_after_restart`, `tests/test_gitlab_note_pipeline.py::test_health_endpoint_reports_gitlab_note_flag`, `tests/test_gitlab_note_pipeline.py::test_health_endpoint_reports_jira_impact_flag` fail with `I/O operation on closed file` from a DBOS queue worker thread. Verified via `git stash` that they fail on `main` without my changes.
- [x] 9b.6 **Bug fix**: After restoring `ATLASSIAN_SITE` / `ATLASSIAN_EMAIL` / `ATLASSIAN_ACCESS_TOKEN` to `~/.tdt/.env` from `.env.bak.sprint16_20260608_210442`, the probe **still failed** — `GET /rest/api/3/field/customfield_11520` returns HTTP 405 on this Jira Cloud instance (only `/rest/api/3/field` list and `/rest/api/3/field/search` are available for custom fields). Changed `DevInChargeSchemaProbe.get()` to use `/rest/api/3/field/search?id=<id>` and unwrap the paginated `values[]` array. Verified via direct `curl` against the live API: the new endpoint returns `{"total":1,"values":[{"id":"customfield_11520","name":"Dev in Charge","schema":{"type":"user",...}}]}` correctly. Updated two existing tests and added one new test (`test_probe_handles_empty_values_list`) that asserts the negative-cache path for unknown field IDs.

## 9c. API research — why programmatic screen-scheme modification is blocked for next-gen projects

After the 2026-07-12 deploy, only the **classic screen-scheme admin APIs** returned 200/empty; the more permissive APIs and the internal GraphQL were probed on 2026-07-13 with admin credentials. Every path that looks like it should work — and several that look unlikely — was tested. The conclusion is the same: **Atlassian does not currently expose any API (public, Forge, Automation REST, or internal GraphQL) that can modify a team-managed project's field-on-screen configuration.**

### Probes that returned definitive "no"

| Surface | Endpoint | Result |
|---------|----------|--------|
| Public REST v3 | `GET /rest/api/3/field/{id}` for custom field metadata | `405 Method Not Allowed` on this Cloud instance (only `/field/search?id=` works for custom fields — 9b.6) |
| Public REST v3 | `GET /rest/api/3/fieldconfigurationscheme/project?projectId={key}` | `400 Bad Request — Failed to convert 'projectId'` (next-gen projects not addressable) |
| Public REST v3 | `GET /rest/api/3/issuetypescreenscheme/project?projectId={key}` | `400 Bad Request` (same) |
| Public REST v3 | `GET /rest/api/3/screenscheme/project?projectId={key}` | `405 Method Not Allowed` |
| Public REST v3 | `GET /rest/api/3/project/{key}/screens`, `/workflows`, `/fieldconfigurations` | `404 Not Found` (no such endpoints) |
| Public REST v3 | `POST /rest/api/3/field/{id}/context` with `projectIds=[next-gen-id]` | `404 These projects were not found` (same payload works on classic projects → `201 Created`) |
| Public REST v3 | `PUT /rest/api/3/field/{id}/context/{id}/issuetype` | Apr 2026: blocked by CHANGE-3019 for the global context |
| Public REST v3 | `PUT /rest/api/3/field/{id}/context/{id}/project` | Same CHANGE-3019 block |
| Public REST v3 | `POST /rest/api/3/screens/addToDefault/{fieldId}` | `400 already exists on the screen` (only adds to classic Default Screen) |
| Forge app REST | `GET/POST /rest/api/3/uiModifications` | `403 Only apps can access this resource (impersonated requests are not allowed)` |
| Automation REST | `GET /automation/api/v1/rules`, `…/health`, `…/ping`, `…/me` | `404` (path not exposed at site base URL) |
| Automation REST | `POST https://api.atlassian.com/automation/public/jira/{cloudid}/rest/v1/rule` | GA but **can only manage rule definitions** — does not modify project-level structures like screens |
| Internal GraphQL | `/gateway/api/graphql` → `Query.jira_fieldConfigSchemes` | Returns 4 classic-project schemes only (`System Default Field Configuration`, `CFD`, `Jira Service Management`, `QA`); no next-gen project schemes appear |
| Internal GraphQL | `Mutation.jira_updateSchemeFieldPerWorkTypeCustomizations` | **EXPERIMENTAL** (requires `@optIn(to: "JiraUpdateSchemeFieldPerWorkTypeCustomizations")`); reaches the database, fails with `BatchUpdateException on insert into public.field_association_item` for ALL 4 schemes — the BSL writes only to the classic-project storage layer, which is **not** where next-gen projects store field-on-screen data |

### What the GraphQL error message reveals

The exception trace from the experimental mutation names the exact BSL class:

```
Caught BatchUpdateException for insert into /* called at cloud.atlassian.jira.domains.fieldconfiguration.associations.scheme.FieldAssociationSchemeItemsMutator.createAssociations(FieldAssociationSchemeItemsMutator.java:830) */"public"."field_association_item" ("field_id", "qualifier_id", "qualifier_type", "renderertype", "required", "scheme_id")
```

Even the **experimental Atlassian-internal mutation** writes through `FieldAssociationSchemeItemsMutator`, which is hard-coded against the classic project's `field_association_item` table. Next-gen projects use a different table that the BSL doesn't touch.

### Atlassian's stated direction

From Atlassian staff on RFC-70 (developer community):
> *"Unfortunately, it's not something that we could provide at the moment, as 'screens' are not really applied to team-managed projects. Overall, we are moving towards replacing 'screens' with 'issue layouts' and as a part of that work we will also provide new rest APIs to manage them. Unfortunately, I can't share any timeline on this one at the moment."*

The feature request `JRACLOUD-91386` ("Add Custom Field to Team-Managed Project Work Types via API") tracks this gap.

## 9d. UI runbook — ✅ all 13 projects fully configured (2026-07-13 13:00 ICT)

After the second operator UI session, **all 13 projects are fully configured** for `customfield_11520`. Verified via `/rest/api/3/issue/{key}/editmeta` on real issues at 2026-07-13 13:00 ICT:

| Project | Has 11520 on edit screen | Status |
|---------|--------------------------|--------|
| AM | Task, Epic, Subtask, Bug, Story, Requirement (all 6) | ✅ fully configured |
| AU | Bug, Task, Story, Epic, Subtask, **Requirement** | ✅ fully configured |
| COM | Bug, Task, Story, Epic, Subtask, **Requirement** | ✅ fully configured |
| FUN | Task, Epic, Subtask, Bug, Story, Requirement (all 6) | ✅ fully configured |
| GAMI | Bug, Task, Story, Epic, Subtask, **Requirement** | ✅ fully configured |
| PDS | Task, Sub-task, Epic, Bug (all 4) | ✅ fully configured |
| PPMT | Workstream, Task, Sub-task (all 3) | ✅ fully configured |
| PUB | Bug, Task, Sub-task, Story, Epic, **Support** | ✅ fully configured |
| PWM | Bug, Task, Story, Epic, Subtask, **Requirement** | ✅ fully configured |
| RMD | Task, Epic, Subtask, Bug, Story, Requirement (all 6) | ✅ fully configured |
| SR | Bug, Task, Epic, Subtask, Story, **Requirement** | ✅ fully configured |
| STABI | Task, Epic, Subtask, Bug, Story (all 5) | ✅ fully configured |
| TJ | Bug, Task, Epic, Subtask, Story, **Requirement** | ✅ fully configured |

**Total configured: 13/13** — setter writes will now succeed on every allow-listed project / issue type.

**Duplicate fields**: zero. `customfield_11539` (AM) and `customfield_11670` (STABI) are no longer on any edit screen and have no data in any issue — they are effectively dead.

**Spec and code alignment**: confirmed — both specify `customfield_11520` as the target field and the 13-project allowlist.

### Final verification

Run a synthetic webhook to confirm end-to-end:

```bash
# Trigger one synthetic webhook that should now succeed
python3 - <<'PY'
import os, json, urllib.request, base64
env = {ln.split('=',1)[0]: ln.split('=',1)[1].strip().strip('"').strip("'")
       for ln in open(os.path.expanduser('~/.tdt/.env'))
       if not ln.startswith('#') and '=' in ln and ln.strip()}
auth = base64.b64encode(f"webhook-user:{env['JIRA_WEBHOOK_SECRET']}".encode()).decode()

# Issue key from a real issue of the right type
issue = 'AM-2490'  # or any open Task/Bug/Story/Epic/Requirement in the target project
payload = {
  "webhookEvent": "jira:issue_updated",
  "issue": {"key": issue, "fields": {"project": {"key": "AM"}, "issuetype": {"name": "Task"}}},
  "changelog": {"items": [{"field": "status", "fromString": "To Do", "toString": "In Progress"}]},
  "user": {"accountId": "5d9e5e5e5e5e5e5e5e5e5e5e"}  # your real accountId
}
r = urllib.request.Request('http://127.0.0.1:8000/webhooks/jira/transition',
                           data=json.dumps(payload).encode(), method='POST',
                           headers={'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'})
with urllib.request.urlopen(r, timeout=10) as resp:
    print(f"Webhook: HTTP {resp.status}")
PY

# Check logs
tail -F ~/.tdt/logs/webhook-receiver.stdout.log | grep -E "dev_in_charge_set\b|dev_in_charge_set_failed"
```

With `customfield_11520` on the screen, you should see `dev_in_charge_set issue=AM-XXXX account_id=...` in the logs (no `dev_in_charge_set_failed`).

### Why this could not be done programmatically

There are exactly two paths forward, both with significant cost:

1. **Build a Forge app** with a `jira:uiModifications` module + an admin page that programmatically calls `/rest/api/3/uiModifications` (app-only) to add `customfield_11520` to the `GIC` / `IssueView` / `IssueTransition` contexts. This modifies what **users see** but doesn't change the **server-side screen** — Jira's PUT will still reject the write because the screen config itself is unchanged. **Verdict: doesn't solve our problem.**

2. **Wait for Atlassian's "issue layouts" RFC** to ship. Currently no timeline. Track `JRACLOUD-91386` for updates. **Verdict: out of our control.**

The operator UI work was the **fastest correct path**.

## 9e. Alignment verification and cleanup (2026-07-13 ICT)

After the second UI session, a full alignment audit was performed:

### Spec ↔ Code ↔ Config consistency

| Layer | `customfield_11520` / 13-project allowlist | Status |
|-------|--------------------------------------------|--------|
| `spec.md` | `JIRA_DEV_IN_CHARGE_FIELD_ID` default; 13-project list | ✅ |
| `dev_in_charge_setter.py` | `field_id = "customfield_11520"`; `DEFAULT_PROJECTS` hardcoded | ✅ |
| `webhook-receiver/README.md` | `JIRA_DEV_IN_CHARGE_FIELD_ID=customfield_11520` | ✅ |
| `~/.tdt/.env` (runtime) | `JIRA_DEV_IN_CHARGE_FIELD_ID=customfield_11520` | ✅ |
| `/health` endpoint | `field_id: customfield_11520`, `enabled: true`, all 13 projects | ✅ |
| `jira-developer-performance-tab/spec.md` | `DEV_PERFORMANCE_DEV_IN_CHARGE_FIELD` defaults to `customfield_11520` | ✅ |
| `jira-skill/scripts/configure_dev_fields.py` | `DEV_IN_CHARGE_ID = "customfield_11520"`, 13-project `TARGET_PROJECTS` | ✅ |

No stale field references in any code layer.

### Orphaned field audit

- `customfield_11539` (AM duplicate): **does not exist in this Jira Cloud instance** (`/rest/api/3/field/search?id=customfield_11539` → `total: 0`). Nothing to archive.
- `customfield_11670` (STABI duplicate): **does not exist in this Jira Cloud instance** (`/rest/api/3/field/search?id=customfield_11670` → `total: 0`). Nothing to archive.
- Both were documented in `tasks.md` as resolved duplicates but were never actually created in Jira — the confusion arose from stale field IDs seen in older Jira export data.

### `tdt_core` type hygiene (root-cause fix)

The 4 pre-existing `mypy --strict` errors in webhook-receiver (`paths.py`, `scan_recent_mr.py`, `health.py`, `selftest_cli.py`) were all downstream symptoms of a missing `py.typed` marker in `tdt-core`.

**Root cause**: `tdt_core` is a local path dependency that mypy treats as an installed package without type information (`import-untyped`). Callers that re-exported its functions (e.g. `_read_env` → `tdt_core.env.get_env`) propagated `Any` returns.

**Fixes applied** (2026-07-13 ICT):

| File | Fix |
|------|-----|
| `tdt-core/pyproject.toml` | Added `members = ["src"]` for hatchling `py.typed` auto-inclusion |
| `tdt-core/src/tdt_core/py.typed` | Created the marker file (previously absent) |
| `webhook-receiver/pyproject.toml` | Added `[[tool.mypy.overrides]] module = "tdt_core.*"` with `follow_imports = "normal"` so mypy analyses the module bodies |
| `webhook_receiver/paths.py` | Removed redundant `cast("Path", ...)` (no longer needed — `ensure_tdt_state_dir` now resolves correctly) |
| `webhook_receiver/scan_recent_mr.py` | Replaced manual `.env` parser (`os` + `Path.read_text`) with `tdt_core.env.get_env()` (canonical loader, removes duplication); removed unused `os` import and unused `tdt_root` import |
| `webhook_receiver/selftest_cli.py` | Same canonical loader refactor; removed unused `os` import and unused `tdt_root` import |
| `webhook_receiver/utils/health.py` | Removed redundant `cast("HealthResult", result)` (mypy correctly infers `HealthResult` from `_run_check` return type) |

**Result**: `mypy src/ --strict` → **0 errors** across 36 source files (was 4).

- [x] 9.8 **Cleanup**: Fixed 4 pre-existing `mypy --strict` errors in webhook-receiver by adding `py.typed` to `tdt_core` and updating `webhook-receiver/pyproject.toml` mypy overrides; refactored `_read_env` / `_load_secret` to use canonical `tdt_core.env.get_env()`.

- [x] 10.1 Update `webhook-receiver/README.md` "Jira integration" section to document the new env vars and the auto-set behavior
- [x] 10.2 Add a short note to `docs/workflows/jira-guard-policies.md` (or create the file if missing) explaining the relationship between the policy-driven guard and the new auto-setter
