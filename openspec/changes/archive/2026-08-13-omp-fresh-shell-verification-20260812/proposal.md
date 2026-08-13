## Why

A fresh-shell verification pass was requested to ensure omp works with the
three configured providers. The tests confirm native Cockpit, giaoduc, and
the default role. Shopapikey is currently blocked by an upstream HTTP 403
burst-throttle response, not by omp or local configuration.

## What Changes

- Record fresh-shell and real CLI evidence.
- Record the shopapikey provider-side throttle as an external blocker.
- Preserve the corrected role map and live configuration.
- Do not change provider routing to hide an upstream rate-limit condition.

## Non-Goals

- No credential rotation.
- No provider replacement or fallback routing change.
- No changes to Hermes, Claude Code, adapter infrastructure, or omp binaries.
