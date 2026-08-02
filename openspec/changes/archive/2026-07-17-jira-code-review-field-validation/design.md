## Context

Currently, issues can be moved from "In Progress" to "Code Review" without populating the "Developer" and "Dev in Charge" fields. This creates gaps in sprint reporting and capacity planning.

The TDT ecosystem uses:
- **jira-skill** for CLI-based Jira operations
- **jira_guard** (webhook-receiver) for transition-based automation
- **PatchedJira** (via tdt_core.clients) for Jira API access

The Jira Cloud REST API v3 supports programmatic workflow modification via `POST /rest/api/3/workflows/update` with validators.

## Goals / Non-Goals

**Goals:**
- Create a jira-skill CLI command to add Field Required validators to workflow transitions
- Discover field IDs programmatically (no manual lookup required)
- Support idempotent execution (safe to run multiple times)
- Support dry-run mode for preview before applying

**Non-Goals:**
- Modifying Jira field configurations (global required fields)
- Creating Jira Automation rules (alternative approach)
- Retroactively filling missing field values
- Supporting Jira Server/Data Center (Cloud-only via v3 API)

## Decisions

### Decision 1: Use Jira Workflow API (Bulk Update) over Automation Rules API

**Chosen:** Jira Workflow API (`POST /rest/api/3/workflows/update`)

**Rationale:**
- Direct workflow modification, no separate automation entity
- Validator added as part of workflow definition (versioned, auditable)
- Uses existing `manage:jira-configuration` permission scope
- Workflow REST API is well-documented with Python examples

**Alternatives considered:**
- **Automation Rules API**: More complex rule structure, requires understanding automation rule schema, harder to idempotently check existing rules
- **jira_guard extension**: Reactive only (can't block transition), works post-transition

### Decision 2: Add CLI Command to jira-skill, Not webhook-receiver

**Chosen:** New module in `jira-skill/src/jira_skill/workflow/`

**Rationale:**
- jira-skill is the home for Jira CLI operations
- webhook-receiver's jira_guard is reactive (post-transition)
- We need a proactive, one-time enforcement setup
- Consistent with existing jira-skill patterns (CRUD, board, sprint modules)

**Alternatives considered:**
- **Extend webhook-receiver jira_guard**: Can't block transitions, only notify/remind
- **New standalone CLI**: Duplicates jira-skill infrastructure

### Decision 3: Use tdt_core.clients.jira for API Calls

**Chosen:** Direct REST calls via requests or PatchedJira instance

**Rationale:**
- Follows TDT convention: always use tdt_core.clients factories
- `PatchedJira` provides enhanced v3 APIs
- Workflow update API may need raw requests for specific payload structure

**Implementation:**
```python
# Via PatchedJira instance
jira = JiraClientFactory.from_env()

# Or direct requests for complex workflow payloads
response = requests.put(
    f"{jira.server}/rest/api/3/workflows/update",
    json=payload,
    headers={"Authorization": f"Bearer {jira.token}"}
)
```

### Decision 4: Idempotent Validator Detection

**Chosen:** Check existing validators before adding; skip if already exists

**Rationale:**
- Safe to run multiple times
- No duplicate validators on re-run
- Requires GET workflow first, then compare

**Algorithm:**
1. GET workflow with `?expand=transitions.rules`
2. Find transition by name or from/to status
3. Check `validators[]` for existing `ruleKey: "system:validate-field-value"` with same `fieldsRequired`
4. If exists → skip with "already configured" message
5. If not exists → POST workflow update with new validator

### Decision 5: Field ID Discovery via createmeta or JQL

**Chosen:** Use Jira field metadata to map field names to customfield IDs

**Rationale:**
- Field names vary by project configuration
- Custom fields have `customfield_XXXXX` IDs
- Need programmatic lookup, not hardcoded IDs

**Implementation:**
```python
# Via PatchedJira createmeta
meta = jira.createmeta(project_keys=[project], expand="projects.issuetypes.fields")
# Search for "Developer" and "Dev in Charge" in fields

# Or via JQL search with fields=* to see actual field structure
issues = jira.search_issues('project = PROJ', fields="*")
```

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Jira Cloud API rate limiting | Bulk updates may fail | Implement exponential backoff, batch by workflow |
| Workflow versioning conflicts | Concurrent edits could conflict | Require workflow be in draft/editable state |
| Wrong field IDs | Validator targets wrong field | Validate field exists before adding validator |
| Permission errors | Non-admin users can't modify workflows | Check permissions first, provide clear error |
| Validator removal | No built-in removal command | Document manual removal in Jira UI |

## API Payload Structure

```python
# Workflow update payload for adding validator
payload = {
    "workflows": [{
        "id": "<workflow-entity-id>",
        "version": <current-version-number>,
        "transitions": [{
            "id": "<transition-id>",
            "validators": [{
                "ruleKey": "system:validate-field-value",
                "parameters": {
                    "ruleType": "fieldRequired",
                    "fieldsRequired": "customfield_10020,customfield_10021",
                    "ignoreContext": "true",
                    "errorMessage": "Developer and Dev in Charge are required before Code Review"
                }
            }]
        }]
    }]
}
```

## Open Questions

1. **Which projects?** Need to determine target projects (all POEMS2 projects or specific ones)
2. **Status naming variations?** "Code Review" vs "In Review" vs "Review" - need to handle variations
3. **Validator removal?** Should we add a companion command to remove validators?
4. **Dry-run output?** What should the preview output look like?
