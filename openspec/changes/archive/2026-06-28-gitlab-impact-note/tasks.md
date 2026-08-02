# GitLab MR Impact Note — Tasks

## Phase 1: Foundation — tdt-core GitLab Note Writer

### Task 1.1 — Add `find_mr_notes` + `upsert_mr_note` to `tdt_core.clients.gitlab_mr`
- [x]
**Owner**: tdt-core
**Estimated**: 1h
**Target**: `tdt-core/src/tdt_core/clients/gitlab_mr.py`

Add two functions alongside the existing `fetch_mr_changes` / `fetch_mr_metadata`:

```python
NOTE_PREFIX = "⚠️ Impact Analysis — MR !"

def find_mr_notes(
    project_path: str,
    mr_iid: int,
    *,
    prefix: str = NOTE_PREFIX,
    factory: GitlabClientFactory | None = None,
) -> list[dict[str, Any]]:
    """Return MR notes whose body starts with ``prefix`` (prefix match).

    Uses ``GET /projects/:id/merge_requests/:iid/notes``.
    Returns ``[{"id": int, "body": str, "author": str}]``.
    """

def upsert_mr_note(
    project_path: str,
    mr_iid: int,
    body: str,
    *,
    note_id: int | None = None,
    factory: GitlabClientFactory | None = None,
) -> int:
    """Create (POST) or edit (PUT) a GitLab MR note. Returns note ID.

    The idempotency marker (NOTE_PREFIX) is prepended to body by
    ``post_gitlab_note`` before this call. Pattern matches
    ai-review/gitlab/review_posting.py:GitLabReviewPoster.
    - ``note_id is None`` → ``POST /projects/:id/merge_requests/:iid/notes``
    - ``note_id is not None`` → ``GET`` note, set ``.body``, ``.save()`` (PUT)
    """
```

**Why this ships first**: both the `jira-skill` markdown poster and the webhook workflow need these. Mirrors the `fetch_mr_changes` / `fetch_mr_metadata` pattern — same factory injection, same sync-then-thread pattern.

**Verification**:
```bash
cd tdt-core && uv run python -c "
from tdt_core.clients.gitlab_mr import find_mr_notes, upsert_mr_note, NOTE_PREFIX
print(NOTE_PREFIX)  # ⚠️ Impact Analysis — MR !
# Smoke: find on a real project/MR
notes = find_mr_notes('pspl/poems-mobile3-android', 1)
print(f'found {len(notes)} notes')
"
```

---

## Phase 2: SDK — jira-skill GitLab Note Module

### Task 2.1 — Create `jira_skill/impact/gitlab_note.py`
- [x]
**Owner**: jira-skill
**Estimated**: 2h
**Target**: `jira-skill/src/jira_skill/impact/gitlab_note.py`
**After**: Task 1.1

Create `jira_skill/src/jira_skill/impact/gitlab_note.py`:

```python
"""GitLab MR impact note — markdown builder and poster."""

NOTE_PREFIX = "⚠️ Impact Analysis — MR !"

def build_gitlab_note(report: ImpactReport, raw_report_path: Path | None = None) -> str:
    """Render an ImpactReport as GitLab markdown.

    Reads ImpactReport fields directly (not ADF). Title is
    "### Impact Analysis — MR !{mr_iid}" with " merged" suffix
    only for ``triggered_by == "webhook-merge"``.
    Sections omitted when empty: changed_files, test_files_to_run, coverage_gaps.
    """

def post_gitlab_note(
    report: ImpactReport,
    project_path: str,
    mr_iid: int,
    *,
    factory: GitlabClientFactory | None = None,
    raw_report_path: Path | None = None,
) -> int:
    """Build markdown + upsert to GitLab MR. Returns note ID or -1 on failure.

    Prepends NOTE_PREFIX to body before calling upsert_mr_note, so
    find_mr_notes (using prefix match) can locate the note on re-runs.
    Never propagates — all exceptions logged and suppressed.
    Pattern mirrors ai-review/gitlab/review_posting.py:GitLabReviewPoster.
    """
```

**Verification**:
```bash
cd jira-skill && uv run python -c "
from jira_skill.impact.gitlab_note import build_gitlab_note, NOTE_PREFIX
from jira_skill.impact.impact_report import ImpactReport
from datetime import datetime, UTC
r = ImpactReport(
    mr_iid=42, mr_url='https://git.example.com/g/r/-/merge_requests/42',
    project_path='g/r', commit_sha='abc123', triggered_by='webhook-merge',
    changed_files=[], resolved_features=['feature.auth'], at_risk_modules=['core'],
    test_files_to_run=[], coverage_gaps=[], unmapped_paths=[],
    analysis_timestamp=datetime.now(tz=UTC), analysis_duration_ms=50,
    gitnexus_index_stale=False, cache_hits=5, cache_misses=0,
)
note = build_gitlab_note(r)
assert 'Impact Analysis' in note
assert 'feature.auth' in note
assert 'core' in note
assert NOTE_PREFIX not in note  # marker prepended by post_gitlab_note, not here
print('build_gitlab_note OK, length:', len(note))
"
```

### Task 2.2 — Export from `jira_skill.impact`
- [x]
**Owner**: jira-skill
**Estimated**: 5min
**Target**: `jira-skill/src/jira_skill/impact/__init__.py`
**After**: Task 2.1

Add `"gitlab_note"` to `__all__`.

---

## Phase 3: Webhook Workflow — gitlab_note_workflow

### Task 3.1 — Add `run_gitlab_note_workflow` to `webhook_receiver.impact`
- [x]
**Owner**: webhook-receiver
**Estimated**: 1h
**Target**: `webhook-receiver/src/webhook_receiver/impact.py`
**After**: Task 2.1

Add `GitLabNoteWorkflowResult` dataclass and `run_gitlab_note_workflow` (mirror `run_impact_workflow`):

```python
@dataclass(frozen=True)
class GitLabNoteWorkflowResult:
    project_path: str
    mr_iid: int
    commit_sha: str
    report: ImpactReport | None
    note_id: int | None = None
    skipped_reason: str | None = None

    @property
    def posted(self) -> bool:
        return self.note_id is not None and self.note_id >= 0

async def run_gitlab_note_workflow(
    payload: dict[str, Any],
    settings: Any,
    action: str = "merge",
) -> GitLabNoteWorkflowResult:
    # 1. Extract project_path, mr_iid, sha from payload
    # 2. Call _run_pipeline(payload, settings) → ImpactReport
    # 3. Set triggered_by = f"webhook-{action}"  (webhook-open / webhook-reopen / webhook-merge)
    # 4. Call post_gitlab_note(updated_report, project_path, mr_iid) via asyncio.to_thread
    # 5. Return GitLabNoteWorkflowResult; never raise
```

Add `register_gitlab_note_step(engine)` mirror of `register_impact_step`.

**Verification**:
```bash
cd webhook-receiver && uv run python -c "
from webhook_receiver.impact import run_gitlab_note_workflow, GitLabNoteWorkflowResult
print('imports OK')
r = GitLabNoteWorkflowResult(project_path='g/r', mr_iid=42, commit_sha='abc',
                              report=None, note_id=None, skipped_reason='test')
assert not r.posted
print('dataclass OK')
"
```

---

## Phase 4: Dispatch — app.py Gate Change

### Task 4.1 — Update `handle_merge_request` dispatch
- [x]
**Owner**: webhook-receiver
**Estimated**: 1h
**Target**: `webhook-receiver/src/webhook_receiver/api/app.py`
**After**: Task 3.1

1. Add `_gitlab_note_step: Any = None` module-level binding
2. In `create_app()`: after `_impact_step = register_impact_step(engine)`:
   ```python
   _gitlab_note_step = register_gitlab_note_step(engine)
   ```
3. Add `_run_gitlab_note_dispatch(...)` (mirror `_run_impact_dispatch`)
4. Replace the existing impact trigger block:
   ```python
   # GitLab MR note: fires on open, reopen, merge when GITLAB_IMPACT_NOTE_ENABLED=true
   gitlab_enabled = bool(getattr(settings, "gitlab_impact_note_enabled", False))
   if action in ("open", "reopen", "merge") and gitlab_enabled:
       asyncio.create_task(_run_gitlab_note_dispatch(...))
   # Jira comment: fires only on merge (existing behaviour)
   if action == "merge" and bool(getattr(settings, "jira_impact_webhook_enabled", False)):
       asyncio.create_task(_run_impact_dispatch(...))
   ```
5. Add `gitlab_impact_note_enabled` field to `AppSettings` (`webhook_receiver.config.settings`) backed by `GITLAB_IMPACT_NOTE_ENABLED` env var, default `False` — the dispatch gate reads this attribute.
6. Add `gitlab_impact_note_enabled` to `/health` output (already wired in `app.py:_health_response`)
7. Add `gitlab_impact_note_enabled` to `AppSettings._log_settings()` for visibility in startup logs

**Verification**:
```bash
# Restart webhook-receiver, then:
curl -s http://127.0.0.1:8080/health | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('gitlab_impact_note_enabled:', d.get('gitlab_impact_note_enabled'))
"
```

---

## Phase 5: Tests — build_gitlab_note

### Task 5.1 — Unit tests for `build_gitlab_note`
- [x]
**Owner**: jira-skill
**Estimated**: 1h
**Target**: `jira-skill/tests/unit/test_gitlab_note.py`
**After**: Task 2.1

Test cases (reads `ImpactReport` fields directly, not ADF nodes):

| # | Test | Input | Expected |
|---|------|-------|----------|
| 5.1.1 | staleness warning prepended | `gitnexus_index_stale=True, cache_misses=3` | `"GitNexus index may be stale"` and `"3 symbols not found"` |
| 5.1.2 | title without "merged" | `triggered_by="webhook-open"` | `"**Impact Analysis — MR !42**"` but NOT "merged" |
| 5.1.3 | stats line | 2 files, 3 features, 150ms, 5 hits | contains "2 changed files", "3 features", "150ms", "5 hits" |
| 5.1.4 | affected features rendered | `resolved_features=["feature.auth", "feature.billing"]` | contains both feature names |
| 5.1.5 | at-risk modules rendered | `at_risk_modules=["core", "auth"]` | contains "At-Risk Modules" and both names |
| 5.1.6 | changed files section | one `ChangedFileModel` with path, feature_tags, symbols | `### Changed Files (1)` + backtick-quoted path |
| 5.1.7 | recommended tests section | one `TestFileModel` with path, test_type=UNIT | `### Recommended Tests (1)` + path + "unit" |
| 5.1.8 | coverage gaps omitted when empty | `coverage_gaps=[]` | no "Coverage Gap" text |
| 5.1.9 | coverage gaps included when non-empty | `coverage_gaps=["src/uncovered.py"]` | contains "Coverage Gaps" and gap text |
| 5.1.10 | unmapped paths section | `unmapped_paths=["src/legacy/"]` | contains "Unmapped Paths" |
| 5.1.11 | raw report link appended | `raw_report_path=Path("/home/.tdt/state/...")` | contains `[View raw impact report](...)` |
| 5.1.12 | empty optional sections omitted | all optional fields empty | no Changed Files, Recommended Tests, Coverage Gaps, Unmapped Paths sections |

```python
# Fixture:
def make_report(**overrides) -> ImpactReport:
    from datetime import UTC, datetime as dt
    from jira_skill.impact.impact_report import ImpactReport, ChangedFileModel, TestFileModel, TestType
    base = {
        "mr_iid": 42,
        "mr_url": "https://git.example.com/g/r/-/merge_requests/42",
        "project_path": "g/r",
        "commit_sha": "abc123",
        "triggered_by": "webhook-merge",
        "changed_files": [],
        "resolved_features": [],
        "at_risk_modules": [],
        "test_files_to_run": [],
        "coverage_gaps": [],
        "unmapped_paths": [],
        "analysis_timestamp": dt.now(tz=UTC),
        "analysis_duration_ms": 150,
        "gitnexus_index_stale": False,
        "cache_hits": 10,
        "cache_misses": 2,
        "ticket_key": None,
    }
    base.update(overrides)
    return ImpactReport(**base)
```

**Verification**: `cd jira-skill && uv run pytest tests/impact/test_gitlab_note.py -v`

---

## Phase 6: Tests — upsert_mr_note

### Task 6.1 — Unit tests for `upsert_mr_note` and `find_mr_notes`
- [x]
**Owner**: tdt-core
**Estimated**: 1h
**Target**: `tdt-core/tests/unit/test_gitlab_mr.py`
**After**: Task 1.1

Test cases:

| # | Test | Expected |
|---|------|----------|
| 6.1.1 | `upsert_mr_note` creates when `note_id=None` | `notes.create({"body": body})` called |
| 6.1.2 | `upsert_mr_note` edits when `note_id=55` | `notes.get(55)` + `.save()` called |
| 6.1.3 | `find_mr_notes` returns only prefix-matching notes | note without `NOTE_PREFIX` excluded |
| 6.1.4 | `find_mr_notes` empty when none match | `[]` |
| 6.1.5 | `upsert_mr_note` does NOT prepend the marker (pure write) | body stored verbatim; marker is prepended by `post_gitlab_note` before the call |
| 6.1.6 | `upsert_mr_note` returns created note ID | `note.id` returned |

```python
@pytest.fixture
def mock_gitlab_client():
    with patch("tdt_core.clients.gitlab_mr.GitlabClientFactory") as factory_cls:
        mock_gl = MagicMock()
        factory_cls.from_env.return_value.create_client.return_value = mock_gl
        mock_project = MagicMock()
        mock_mr = MagicMock()
        mock_gl.projects.get.return_value = mock_project
        mock_project.mergerequests.get.return_value = mock_mr
        yield {"mr": mock_mr, "factory_cls": factory_cls}
```

**Verification**: `cd tdt-core && uv run pytest tests/unit/test_gitlab_mr.py -v -k "note"`

---

## Phase 7: Integration — Real MR Replay

### Task 7.1 — Real MR replay: open + merge events
- [x]
**Owner**: webhook-receiver
**Estimated**: 1h
**Target**: `webhook-receiver/tests/integration/`
**After**: Task 4.1

Create `webhook-receiver/tests/integration/test_gitlab_note_replay.py`:

```python
import time, json

SECRET = "..."  # from env

def build_payload(action, mr_iid):
    return {
        "object_kind": "merge_request",
        "event_type": "merge_request",
        "user": {"id": 999, "username": "test"},
        "project": {
            "id": 232,
            "path_with_namespace": "pspl/poems-mobile3-android",
            "web_url": "https://git.ecomedic.vn/pspl/poems-mobile3-android",
            "default_branch": "develop",
        },
        "object_attributes": {
            "id": 12345678,
            "iid": mr_iid,
            "state": "merged" if action == "merge" else "opened",
            "action": action,
            "source_branch": "test/test-branch",
            "target_branch": "develop",
            "merge_status": "can_be_merged",
            "url": f"https://git.ecomedic.vn/pspl/poems-mobile3-android/-/merge_requests/{mr_iid}",
            "last_commit": {
                "id": "cd21805ad17825e03b17360cb2ea8e146b016fac",
                "message": "test commit",
            },
        },
        "merge_request": {"iid": mr_iid},
    }
```

Tests:

| # | Test | Check |
|---|------|-------|
| 7.1.1 | `action=open` fires GitLab note | log contains `gitlab_note_created` |
| 7.1.2 | `action=open` does NOT fire Jira comment | no `impact_dispatch_triggered` |
| 7.1.3 | `action=merge` fires both | `gitlab_note_created` AND `impact_dispatch_triggered` |
| 7.1.4 | Idempotency: 2nd `open` → same note ID | 1 note, same ID, not 2 |
| 7.1.5 | `GITLAB_IMPACT_NOTE_ENABLED=false` → no GitLab call | no `gitlab_note_created` |

**Verification**:
```bash
# Replay open event
python3 -c "
import hashlib, hmac, json, urllib.request, time
SECRET = '...'
# POST to http://127.0.0.1:8080/gitlab-webhook
# Check logs:
grep 'gitlab_note_created\|gitlab_note_edited\|gitlab_note_failed' \
  ~/.tdt/deployments/webhook-receiver/logs/webhook-receiver.stdout.log | tail -5
"
```

---

## Phase 8: Verification — Full Smoke

### Task 8.1 — Full pipeline smoke
- [x]
**Owner**: team
**Estimated**: 30min
**Target**: live service
**After**: Task 7.1

1. Enable `GITLAB_IMPACT_NOTE_ENABLED=true` in `~/.tdt/.env`
2. Redeploy webhook-receiver
3. Replay `action=open`, `action=reopen`, `action=merge` webhooks against a test MR
4. Verify log lines:
   - `gitlab_note_dispatch_triggered` (action=open/reopen/merge)
   - `gitlab_note_created` or `gitlab_note_edited` (idempotency)
   - `impact_dispatch_triggered` (action=merge only)
   - `impact_analysis_complete posted_count=1` (action=merge only)
5. Disable via env and redeploy

**Verification**: all 5 log assertions pass, no duplicate notes, no exceptions in logs.
