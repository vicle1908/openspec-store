# Design: go-microservices store pointer

## Current state

`go-microservices/openspec/config.yaml` does not exist (no `openspec/` directory at all).

The repo's AGENTS.md instructs agents to use `--store openspec-store` explicitly,
and the global `defaultStore` covers commands run without flags.

## Change

Create `go-microservices/openspec/config.yaml` with:

```yaml
store: openspec-store
```

This makes the store relationship explicit in the config, matching the guide's
recommended pattern and the convention used by all 15 Python repos.

## Verification

```bash
# Confirm the pointer is detected
cat ~/Developer/go-microservices/openspec/config.yaml

# Confirm openspec resolves correctly from within go-microservices
cd ~/Developer/go-microservices && openspec context

# Confirm doctor still passes
openspec store doctor
```
