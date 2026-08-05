## Why

The TDT ecosystem has 4 config file formats (TOML, YAML, JSON, .env) and 3 competing loading patterns across 16 Python repos. This causes config duplication, roundtrip injection, silent failures, no schema validation, and version drift.

## What Changes

- Merge config.toml into config.yaml as single source of truth
- Add pydantic-settings[yaml]>=2.14.2 to tdt-core
- Upgrade pydantic to >=2.13.4
- Create TDTSettings root model with YamlConfigSettingsSource
- Migrate JiraConfig/GitlabConfig to BaseSettings
- Add backward-compat shims for load_sprint_config()
- Run migration script to consolidate config files

## Impact

- **Primary target:** tdt-core config loading, all Python repos consuming tdt_core.env
- **Repos affected:** tdt-core (HIGH), ai-review (MEDIUM), jira-daily-reports (MEDIUM), 7 others (LOW)
- **Operational risk:** LOW — backward-compat shims preserve existing behavior
- **Blast radius:** 10 repos using tdt_core.env, 12 repos using tdt_core.paths
