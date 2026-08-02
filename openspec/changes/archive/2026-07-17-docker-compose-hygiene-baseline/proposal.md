# Proposal: Docker Compose Hygiene Baseline

## Problem

The TDT ecosystem has 3 active `docker-compose*.yml` files with inconsistent
modern practices:

| File | Issues |
|------|--------|
| `agent-core/compose.yaml` | ✅ Excellent — only minor gap: no explicit `networks:` block |
| `jira-skill/docker-compose.yml` | 🔴 Hardcoded Grafana `admin` password; missing `name:`; deprecated `version:`; `container_name:` overrides everywhere |
| `bootstrap-nexus-for-mobile/docker-compose.yml` | 🟡 Missing `name:`; deprecated `version: '3.8'`; `container_name:` overrides |

## Scope

This change only touches compose files and the OpenSpec spec artifacts. No
application code changes are required.

## Goals

1. **Eliminate security risk**: Replace hardcoded Grafana credentials.
2. **Modernize metadata**: Add `name:` fields, drop deprecated `version:`.
3. **Improve portability**: Remove `container_name:` where it is not strictly required.
4. **Establish hygiene baseline**: Document which practices are mandatory across the ecosystem.

## Non-goals

- Do not refactor `jira-skill` to use Docker secrets (out of scope for local dev).
- Do not change network topology.
- Do not touch archived or vendor-supplied compose files.
