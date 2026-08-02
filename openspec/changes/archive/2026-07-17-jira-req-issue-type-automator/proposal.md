## Why

The POEMS Mobile 3.0 development process surfaces a recurring gap: requirements ambiguity discovered mid-sprint forces rework. Currently, the team has no standardized way to create a "Req" (Requirements Clarification) work item — developers either file a "Task" with a misleading type, or the clarification is tracked informally in comments.

Adding a "Req" issue type programmatically across the PSplit Jira instance (211 projects) requires handling two fundamentally different project models: **classic** (company-managed, 35 projects) and **team-managed** (next-gen, 176 projects). They use completely different APIs.

The trigger: the DLC Visibility URS document analysis workflow needs a standard type to track requirements clarification work alongside development tasks.

## What Changes

- **`tdt-core/src/tdt_core/clients/jira_types.py`** — new REST client wrapping issue type and issue type scheme APIs for classic projects
- **`jira-skill/src/jira_skill/issue_type.py`** — new CLI command `jira-skill issue-type` with `create`, `update`, and `list` subcommands
- **`jira-skill/src/jira_skill/issue/models.py`** — extend `IssueType` enum with `REQ = "Req"`
- **`~/.tdt/.env`** — `JIRA_CLASSIC_PROJECTS` env var already written (35 comma-separated project keys from dashboard 11827)

## Capabilities

### New Capabilities

- **`issue-type-create`**: Create a new global issue type and wire it to all (or a subset of) classic Jira projects via issue type schemes — idempotent, dry-run mode
- **`issue-type-update`**: Update the name or description of an existing global issue type — propagates to all schemes that contain it
- **`issue-type-list`**: Enumerate all global issue types and which schemes/projects use each

### Modified Capabilities

- **`jira-skill`** CLI — gains `issue-type` sub-app, registered as `app.add_typer(issue_type_app, name="issue-type")`

## Impact

**Dependencies:**
- `tdt-core` (already a dependency of `jira-skill`)
- `atlassian-python-api` (for `requests.Session` reuse)
- `tdt_core.env.load_tdt_env()` for credentials
- `JIRA_CLASSIC_PROJECTS` env var in `~/.tdt/.env` (already in place)

**Affected repos:**
- `tdt-core/` — new `jira_types.py` file, no changes to existing files
- `jira-skill/` — new `issue_type.py`, extended `models.py`, modified `cli.py`
- `tdt-meta/` — `AGENTS.md` Jira Skill Routing table updates (optional, for discoverability)

**Constraints:**
- Classic projects only for write operations (issue type scheme API is not available for team-managed)
- `PUT .../issuetypescheme/{id}/issuetype` fails if type already in scheme — idempotency requires pre-check
- `POST .../issuetype` requires Administer Jira global permission
- PSplit has **35 classic projects** across **20 unique issue type schemes** — no single "assign to all" endpoint; must iterate schemes
- "Req" name is short and unlikely to conflict — confirmed not present in global types

**Risk:**
- LOW: read-only discovery steps first, mutations behind `--dry-run` flag
- LOW: idempotent design means re-runs are safe
- MEDIUM: 20 scheme iterations = 20 API calls = ~2s total (acceptable)
- HIGH: team-managed projects cannot be automated — documented as known limitation

## API Verification (Live Tests against PSplit, 2026-06-23) + Official Atlassian Confirmation

Live tests against PSplit confirmed, and official Atlassian staff responses on the developer community forums independently confirm, the following:

### Official Atlassian Statements (community.developer.atlassian.com)

> *"There is no public REST API available to create project-scoped entities like issue types, statuses and custom fields... All write operations (create and update) will NOT work when operating on next-gen project entities."*
— Atlassian staff, community.developian.com

> *"Currently this is not possible. You may watch and vote this issue https://jira.atlassian.com/browse/JSWCLOUD-23545."*
— Atlassian staff, community.atlassian.com, June 2024

> *"Nope. Refer to JRACLOUD-87581."*
— Atlassian staff, community.atlassian.com

> *"Forge apps run in a sandbox and currently can't create issue types or schemes."*
— Atlassian staff, community.atlassian.com

### Live Tests (PSplit)

| Test | Method | Endpoint | Result |
|---|---|---|---|
| Create type in team-managed project | `POST` | `/rest/api/3/issuetype/project` | **405 Method Not Allowed** |
| Read types for team-managed project | `GET` | `/rest/api/3/issuetype/project?projectId=11287` | **200 OK** |
| Read types for classic project | `GET` | `/rest/api/3/issuetype/project?projectId=11351` | **200 OK** |
| Create globally with scope param | `POST` | `/rest/api/3/issuetype` + `scope` | **201** but scope silently ignored |
| **Update team-managed scoped type** | `PUT` | `/rest/api/3/issuetype/{id}` | **400 Can not update issue type, because it is not a global issue type** |
| Update global type | `PUT` | `/rest/api/3/issuetype/10005` | **200 OK** |
| Assign scheme to team-managed | `PUT` | `/rest/api/3/issuetypescheme/project` | **400 Invalid request payload** |
| Bulk issue operations | `POST` | `/rest/api/3/bulk` | **404 Not Found** |
| Automation rules API | `GET` | `/rest/automation/latest/global/rules` | **404 Not Found** |
| Project work item endpoint | `GET` | `/rest/api/3/project/{id}/workitemtype` | **404 Not Found** |
| Project issue types endpoint | `GET` | `/rest/api/3/project/{id}/issuetype` | **404 Not Found** |
| Work item types (any case) | `GET` | `/rest/api/3/workitemtype`, `/workItemType` | **404 Not Found** |

### The Critical Validation: Update on Team-Managed Scoped Type

```python
# Get Q&A type from PP1 (team-managed project)
GET /rest/api/3/issuetype/project?projectId=11287
→ {"id": "11977", "name": "Q&A",
   "scope": {"type": "PROJECT", "project": {"id": "11287"}}}

# Try to update it
PUT /rest/api/3/issuetype/11977
{"name": "Q&A Updated"}
→ Status: 400
{"errorMessages": ["Can not update issue type, because it is not a global issue type."]}
```

This **officially confirms bug JRACLOUD-76503** on PSplit: not only can you not create work item types in team-managed projects via REST — you cannot even update or delete them. The error message is explicit: "not a global issue type."

### Project Style Classifier

The `style` field in `/rest/api/3/project/{id}` is the reliable classifier:

```python
Classic project (PUB, id=11351):
  "style": null        # absent / null
  "issueTypes": []     # empty in project response

Team-managed project (PP1, id=11287):
  "style": "next-gen"  # explicit string
  "issueTypes": ["Story", "Task", "Bug", "Epic", "Subtask", "Q&A"]
```

## Team-Managed Projects: Confirmed Gap

Atlassian provides **no REST API** for creating, updating, or deleting work item types in team-managed (next-gen) projects. This is confirmed by:

1. **Official Atlassian staff statements** on community forums (multiple, dated 2024-2025)
2. **Live testing on PSplit** — every write endpoint returns 4xx errors
3. **Open feature requests** — JRACLOUD-87581 and JSWCLOUD-23545 (both Unresolved as of June 2026)
4. **Official documentation** — [Add, edit, and delete a work type](https://support.atlassian.com/jira-cloud-administration/docs/add-edit-and-delete-an-issue-type/) explicitly covers only company-managed spaces

### Official Atlassian Statements (community.developer.atlassian.com)

| Quote | Source |
|---|---|
| *"There is no public REST API available to create project-scoped entities like issue types, statuses and custom fields. All write operations (create and update) will NOT work when operating on next-gen project entities."* | Atlassian staff |
| *"Nope. Refer to JRACLOUD-87581."* | Atlassian staff |
| *"Forge apps run in a sandbox and currently can't create issue types or schemes."* | Atlassian staff |
| *"Currently this is not possible... watch and vote this issue JSWCLOUD-23545."* | Atlassian staff, June 2024 |
| *"Issue type schemes can only be assigned to classic projects."* | [Official docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-schemes/) |

### Exhaustive API Testing — All Results

The following 20+ endpoints were tested live against PSplit. All write operations fail:

| Endpoint | Method | Result | Meaning |
|---|---|---|---|
| `/rest/api/3/issuetype` | POST | **201** (but scope ignored) | Creates globally, scope param silently discarded |
| `/rest/api/3/issuetype` | GET | **200** | Returns all types (735) |
| `/rest/api/3/issuetype/{id}` | PUT | **400** on scoped types | `"Can not update issue type, because it is not a global issue type."` |
| `/rest/api/3/issuetype/{id}` | DELETE | **204** on global types | Only works for global types |
| `/rest/api/3/issuetype/project` | GET | **200** | Read-only — works for both project types |
| `/rest/api/3/issuetype/project` | POST | **405** | GET-only endpoint |
| `/rest/api/3/issuetype/project` | PUT | **405** | GET-only endpoint |
| `/rest/api/3/issuetype/project` | DELETE | **405** | GET-only endpoint |
| `/rest/api/3/workitemtype` | GET | **404** | No such resource |
| `/rest/api/3/workitemtype/{id}` | GET | **404** | No such resource |
| `/rest/api/3/worktype` | GET | **404** | No such resource (JSM only, not JSW) |
| `/rest/api/3/worktypescheme` | GET | **404** | No such resource (JSM only, not JSW) |
| `/rest/automation/latest/global/rules` | GET | **404** | No automation REST API |
| `/rest/api/3/project/{id}/issuetype` | GET | **404** | No project-level type endpoint |
| `/rest/api/3/project/{id}/workitemtype` | GET | **404** | No project-level work item endpoint |
| `/rest/api/3/issuetypescheme/project` | PUT | **400** | Cannot assign scheme to team-managed project |
| `/rest/api/3/bulk` | POST | **404** | No bulk type creation |
| `/rest/api/2/issue/createmeta` | GET | **200** | Read-only metadata (shows scoped types) |
| Jira Forge | — | **403** | Sandbox cannot create types |
| Jira Expressions | POST | **200** | Read-only evaluation, no side effects |

### The `scope` Parameter: Vestigial and Inert

The `scope` field appears in the POST `/rest/api/3/issuetype` request schema, suggesting project-scoped type creation. Live testing proves this is a **forward-compatibility stub**:

```python
POST /rest/api/3/issuetype
{
    "name": "TestType",
    "type": "standard",
    "scope": {"type": "PROJECT", "project": {"id": "11287"}}
}
→ 201 Created (type appears globally, id=12268)
→ scope SILENTLY DISCARDED — type does NOT appear in PP1's work types
→ DELETE /rest/api/3/issuetype/12268 → 204  (cleanup confirmed)
```

Atlassian is likely maintaining the `scope` field for when JRACLOUD-87581 is resolved. It currently has no effect.

### Project Features: Classic vs Team-Managed

The `/rest/api/3/project/{id}/features` endpoint reveals the fundamental difference:

```
PP1 (team-managed): 13 features  — jsw.agility.* namespace
PUB (classic):      18 features  — jsw.classic.* namespace
```

Team-managed projects have fewer features and do not expose the configuration endpoints (schemes, workflows, fields) that classic projects use. This is by design — team-managed projects are self-contained with no shared configuration layer.

### Changelog: Feb 2026 Work Type API

The Feb 2026 changelog mentions a "Create work type API" change — this applies to **Jira Service Management** (request types), NOT Jira Software. All `/worktypescheme` and `/worktype` endpoints return **404** on PSplit (Jira Software Cloud). This is a different product line.

### Bottom Line

**There is no path — REST API, Forge, Automation, Jira Expressions, or workaround — to programmatically create or update work item types in team-managed Jira projects as of June 2026.** The only path is manual: **Project Settings > Work types > Add work type**.
