# Design: jira-req-issue-type-automator

## PSplit Jira Inventory

| Category | Count | Projects | Notes |
|---|---|---|---|
| Classic (style=classic) | **35** | All on dashboard 11827 | REST API available for type + scheme management |
| Team-managed (style=next-gen) | **176** | GMO, PP1, POEMS2, etc. | No REST API — manual only |
| Product discovery | 1 | MDS | Not a software project |

Classic projects span **20 unique issue type schemes**:

| Scheme ID | Scheme Name | Projects |
|---|---|---|
| 10127 | CFD: Kanban Issue Type Scheme | CFD, CFDAHP, CFDBO, CFDFO, CFDFOTASK, CFDMO, CFDPRJ, CFDX, GC, GCTASK (10) |
| 10429 | MQ: Software Development Issue Type Scheme | CCQ, MAQ, MQ, PWQ (4) |
| 11971 | QAT: Kanban Issue Type Scheme (1) | QATP, QATP3, QATW (3) |
| 10139 | M2QAT: Software Development Issue Type Scheme | M2QAT, RMSQAT (2) |
| 10126 | GWM: Software Development Issue Type Scheme | GWM (1) |
| 10128 | GWM4: Software Development Issue Type Scheme | GWM4 (1) |
| 10162 | GFOQAT: Software Development Issue Type Scheme | GFOMYQAT (1) |
| 10164 | GFOSG: Software Development Issue Type Scheme | GFOSGQAT (1) |
| 10170 | ATUP: Software Development Issue Type Scheme | ATUP (1) |
| 10269 | BMMQ: Software Development Issue Type Scheme | BMMQ (1) |
| 10424 | MW: Software Development Issue Type Scheme | MW (1) |
| 11537 | XRP: Scrum Issue Type Scheme | XRP (1) |
| 11599 | QP: Scrum Issue Type Scheme | QP (1) |
| 11802 | ITQA: Scrum Issue Type Scheme | ITQA (1) |
| 11835 | IP: Kanban Issue Type Scheme | IP (1) |
| 12112 | TES: Software Development Issue Type Scheme | QA (1) |
| 12145 | TS: Kanban Issue Type Scheme | TS (1) |
| 12413 | TES: Software Development Issue Type Scheme (1) | TES (1) |
| 12832 | CEX: Scrum Issue Type Scheme | CEX (1) |
| 13104 | PUB: Scrum Issue Type Scheme | PUB (1) |

No "Req" issue type currently exists globally in PSplit.

---

## Component 1: `tdt_core.clients.jira_types.IssueTypeSchemeClient`

**Location:** `tdt-core/src/tdt_core/clients/jira_types.py`

Mirrors the `CompanyManagedWorkflowHandler` pattern: holds a `requests.Session` with auth headers, makes direct REST calls via `_retry_request()`.

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class IssueType:
    id: int
    name: str
    description: str
    type: Literal["standard", "subtask"]
    hierarchyLevel: int

@dataclass
class IssueTypeScheme:
    id: int
    name: str
    isDefault: bool
    defaultIssueTypeId: int | None

@dataclass
class IssueTypeSchemeProjectMapping:
    scheme: IssueTypeScheme
    projectIds: list[int]

class IssueTypeAlreadyInSchemeError(Exception):
    pass

class IssueTypeNotFoundError(Exception):
    pass

class ProjectNotClassicError(Exception):
    pass

class IssueTypeSchemeClient:
    def __init__(self, url: str, email: str, token: str):
        self._url = url.rstrip("/")
        self._session = requests.Session()
        self._session.auth = (email, token)
        self._session.headers["Accept"] = "application/json"
        self._session.headers["Content-Type"] = "application/json"

    def create_issue_type(
        self,
        name: str,
        description: str = "",
        type: Literal["standard", "subtask"] = "standard",
    ) -> IssueType:
        """POST /rest/api/3/issuetype — returns existing if name already exists."""

    def get_issue_type_by_name(self, name: str) -> IssueType | None:
        """Search global types for name match."""

    def get_all_issue_type_schemes(
        self, start_at: int = 0, max_results: int = 100
    ) -> list[IssueTypeScheme]:
        """GET /rest/api/3/issuetypescheme — paginated."""

    def get_scheme_for_project(self, project_id: int) -> IssueTypeSchemeProjectMapping | None:
        """GET /rest/api/3/issuetypescheme/project?projectId=..."""

    def get_scheme_items(self, scheme_id: int) -> list[IssueType]:
        """GET /rest/api/3/issuetypescheme/{id} — returns types in the scheme."""

    def add_issue_types_to_scheme(
        self, scheme_id: int, issue_type_ids: list[int]
    ) -> None:
        """PUT /rest/api/3/issuetypescheme/{id}/issuetype.
        Raises IssueTypeAlreadyInSchemeError if any type already exists.
        """

    def update_issue_type(
        self,
        issue_type_id: int,
        name: str | None = None,
        description: str | None = None,
        avatar_id: int | None = None,
    ) -> IssueType:
        """PUT /rest/api/3/issuetype/{id}."""
```

**Key design decisions:**

- `scheme_id` and `project_id` are `int` (not `str`) — Jira API uses integers
- `create_issue_type` is idempotent: checks for existing by name first, returns existing without error
- `add_issue_types_to_scheme` raises `IssueTypeAlreadyInSchemeError` — callers must pre-check with `get_scheme_items`
- All HTTP calls wrapped in `_retry_request()` with exponential backoff for 429/5xx

---

## Component 2: jira-skill `issue-type` CLI

**Location:** `jira-skill/src/jira_skill/issue_type.py`
**Registration:** `cli.py` adds `@app.add_typer(issue_type_app, name="issue-type")`

### CLI Interface

```
jira-skill issue-type create "Req" \
    [--description "Tracks work to clarify ambiguous requirements..."] \
    [--projects KEY1,KEY2,... | --all-classic | --env-key JIRA_CLASSIC_PROJECTS] \
    [--dry-run] \
    [--verbose]

jira-skill issue-type update "Req" \
    [--name "New Name"] \
    [--description "Updated description"] \
    [--dry-run]

jira-skill issue-type list \
    [--verbose]
```

### `--all-classic` Flag

Reads `JIRA_CLASSIC_PROJECTS` from `~/.tdt/.env` (already written). Comma-separated list of 35 project keys.

### `create` Subcommand Flow

```
Step 1: Discover classic projects
  → Load JIRA_CLASSIC_PROJECTS from env
  → jira.get_all_projects() → filter style=classic → cross-reference keys

Step 2: Create issue type globally
  → client.get_issue_type_by_name("Req") → if found, use existing ID
  → else client.create_issue_type(name="Req", ...) → 201 Created

Step 3: Enumerate all issue type schemes
  → client.get_all_issue_type_schemes() → list of 20 schemes

Step 4: Wire type to each scheme
  For each scheme:
    a. client.get_scheme_items(scheme_id) → get existing type IDs
    b. If "Req" already in scheme → log "⊘ already present" → skip
    c. Else client.add_issue_types_to_scheme(scheme_id, [type_id])
       → 204 No Content → log "✓ added"

Step 5: Report summary
  Total schemes updated, total skipped, total errors
  List of team-managed projects (if any in JIRA_CLASSIC_PROJECTS) skipped with note
```

### `update` Subcommand Flow

```
Step 1: Find issue type by name
  → client.get_issue_type_by_name("Req") → get ID
  → if not found → error "Type 'Req' not found"

Step 2: Update globally
  → client.update_issue_type(id, name=..., description=...)
  → 200 OK

Step 3: Report
  "Updated type 'Req' (id=X)"
```

### `list` Subcommand Flow

```
Step 1: GET /rest/api/3/issuetype → all global types
Step 2: GET /rest/api/3/issuetypescheme → all schemes
Step 3: For each type, find which schemes contain it
Step 4: Print table: Type | ID | Schemes | Subtask?
```

### Output Format

Rich table with color-coded status:

```
╭──────────────────────────────────────────────────────╮
│  jira-skill issue-type create "Req"                 │
├──────────────────────────────────────────────────────┤
│  [1/4] Discovering projects...                  ✓ 35   │
│        Team-managed skipped:              MDS (1)      │
│                                                      │
│  [2/4] Creating issue type globally...         ✓     │
│        "Req" created (id=10015)                      │
│                                                      │
│  [3/4] Enumerating schemes...                  ✓ 20   │
│                                                      │
│  [4/4] Wiring to schemes...                         │
│        ✓ 10127 CFD Kanban Scheme        (10 proj)    │
│        ✓ 10429 MQ Software Dev Scheme    (4 proj)     │
│        ⊘ 13104 PUB Scrum Scheme         (1 proj)     │
│          type already present                          │
│        ...                                            │
│                                                      │
│  Summary: 19 added, 1 skipped, 0 errors             │
│  Projects covered: 35 classic projects               │
│  Type: "Req" id=10015                              │
╰──────────────────────────────────────────────────────╯
```

### `--dry-run` Flag

All steps run but API mutations (POST, PUT) are skipped. Prints what *would* happen:

```
[DRY RUN] Would POST create issue type "Req"
[DRY RUN] Would PUT add type 10015 to scheme 10127
[DRY RUN] Would PUT add type 10015 to scheme 10429
...
[DRY RUN] 19 mutations would occur across 19 schemes
```

---

## Data Model Extension

**Location:** `jira-skill/src/jira_skill/issue/models.py`

```python
class IssueType(Enum):
    BUG = "Bug"
    STORY = "Story"
    TASK = "Task"
    EPIC = "Epic"
    SUBTASK = "Sub-task"
    # --- new ---
    REQ = "Req"
```

Adding `REQ` here enables type-safe references throughout `jira-skill` (e.g., estimators, classifiers, reporters).

---

## Error Handling Strategy

| Error | CLI Behavior | Recoverable? |
|---|---|---|
| Type already in scheme | `⊘ skipped` | Yes — idempotent |
| Scheme assignment conflict | Per-scheme error, continue to next | Yes |
| 429 Rate limit | Retry with backoff | Yes |
| 403 Forbidden | Abort — lacks Administer Jira | No |
| Type not found on update | Abort | No |
| Team-managed project detected | `⊘ skipped: team-managed (no API)` | Yes — skip |

---

## File Map

```
tdt-core/src/tdt_core/clients/
    jira.py              ← unchanged
    jira_types.py        ← new (IssueTypeSchemeClient + dataclasses)

jira-skill/src/jira_skill/
    issue/
        models.py        ← extend IssueType enum
    issue_type.py       ← new (CLI sub-app + orchestration)
    cli.py               ← register issue_type_app
```

---

## Env Var

```
# Already written to ~/.tdt/.env:
JIRA_CLASSIC_PROJECTS=ATUP,BMMQ,CCQ,CEX,CFD,CFDAHP,CFDBO,CFDFO,CFDFOTASK,CFDMO,CFDPRJ,CFDX,GC,GCTASK,GFOMYQAT,GFOSGQAT,GWM,GWM4,IP,ITQA,M2QAT,MAQ,MQ,MW,PUB,PWQ,QA,QATP,QATP3,QATW,QP,RMSQAT,TES,TS,XRP
```

---

## D1: SDK vs Raw HTTP

**Decision:** Raw `requests.Session` via `_retry_request()` (same as `CompanyManagedWorkflowHandler`).

**Rationale:** `atlassian-python-api` does not wrap issue type scheme endpoints. Direct HTTP is the only path. The pattern is already proven in `jira_workflow.py`.

---

## D2: Idempotency Strategy

**Decision:** Pre-check before every mutation (`get_scheme_items` → check → `add`).

**Rationale:** `PUT .../issuetype` on a scheme returns 204 but **fails** if any type is already present. Without pre-check, re-running would error on all schemes that already received "Req" in a previous partial run.

---

## D3: Env Var vs CLI Argument for Projects

**Decision:** Use `JIRA_CLASSIC_PROJECTS` env var as source of truth.

**Rationale:** The 35 classic projects map directly to dashboard 11827. Hardcoding in CLI is fragile. Env var is already written and follows the "config in env" pattern established by `JIRA_DEFAULT_FILTER_REGISTRY_ID`, `SPREADSHEET_ID`, etc.

---

## D4: `--all-classic` vs Per-Scheme Selection

**Decision:** `--all-classic` (reads env) as default; `--schemes` accepts specific scheme IDs as override.

**Rationale:** Simpler first. If someone needs to add "Req" only to specific schemes (e.g., test first on PUB), `--schemes 13104` covers it without env changes.
