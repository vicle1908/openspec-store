# Proposal: dev-perf-merged-at-fallback

## Problem

The `jira-daily-reports dev-performance` tab computes cycle time as `In Progress → First Deploy to Dev`. The spec defines "First Deploy to Dev" as `min(d.created_at for d in deployments if d.environment == DEV_PERFORMANCE_DEPLOY_ENVIRONMENT)`, fetching `GET /projects/:id/merge_requests/:iid/deployments` from GitLab API v4.

On `git.ecomedic.vn` (GitLab 17.5.5), the Deployments API is not enabled at the instance level — all `GET /deployments` calls return `GitlabHttpError 404: 404 Not Found` even for fully-merged MRs with successful pipelines. This causes `missing_first_deploy` to be inflated to ~N (all tickets) and cycle time to be empty for every row.

The GitLab PAT (`E_7cHT2HFquyHu7UxTVD`) is fully valid and has `api_access_scope: true` — the 404 is an instance-level feature gap, not a credential issue.

## Proposed Solution

When the Deployments API returns no results (404), fall back to `MR.merged_at` as the "deploy" signal. The fallback is:

1. **Only applied per-MR when `fetch_deployments()` returns an empty list** (not on exceptions — those still warn and continue with `first_deploy_at = None`).
2. **Only used when the MR is in `merged` state** — open/draft MRs don't count.
3. **Logged** as a new `merged_at_fallback` INFO event so operators can distinguish fallback rows from genuine deployment rows.
4. **Named semantically** as `DEV_PERFORMANCE_USE_MERGED_AT_FALLBACK` (default `true`) so it can be disabled if deployments are later enabled.

The fallback is less precise than a real deployment event, but it is:
- Monotonically after `In Progress` (merge happens after code review, which follows In Progress).
- A stable, available signal for every merged MR.
- Semantically sound: the MR merge moment is when code enters the "ready to deploy" state.

## Out of Scope

- Enabling the GitLab Deployments feature on `git.ecomedic.vn` — requires GitLab admin access and a paid tier.
- Replacing the existing `fetch_deployments` call with a pipelines-based alternative — pipeline `status=success` is a CI signal (pre-merge), not a deployment signal.
- Adding new environment variables beyond `DEV_PERFORMANCE_USE_MERGED_AT_FALLBACK`.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Pipeline `status=success` timestamp as "deploy" | Pipelines run pre-merge; `head_pipeline.created_at` is before `merged_at`, which can produce negative cycle times. |
| Skip cycle time entirely when deployments unavailable | Loses a useful metric; fallback is still informative. |
| Enable GitLab Deployments via admin | Requires GitLab Premium; out of operator control. |

## Success Criteria

1. The `dev_performance_summary` log line shows a new `merged_at_fallback=N` counter when fallback is used.
2. Rows with merged MRs but no deployments show a non-null `In Progress → Deploy` duration computed from `merged_at`.
3. `missing_first_deploy` count drops from N to a non-zero count reflecting only MRs that are not merged.
4. A new spec requirement documents the fallback behavior.
