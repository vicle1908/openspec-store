# Design: Four-Provider Architecture Baseline and Model Updates

## Overview

This design establishes the canonical four-provider topology across all agent CLIs:
1. `shopapikey` (`Claude-Fable`)
2. `phanmemvip` (`codex-x`)
3. `cockpit` (`gpt-6-astra` and cockpit-native models)
4. `omniroute` (`sh/codex-x`, `sh/Claude-Fable`, `pm/Claude-Fable`)

## Key Decisions

### Decision 1: Phased Provider Model Migration
Migrate all direct `phanmemvip` references from deprecated `gpt-5.6-sol` to `codex-x` and rotate API credentials. Keep `shopapikey` and `cockpit` configurations strictly isolated.

### Decision 2: Hermes MoA Alignment
Update Hermes MoA presets and goal judge to use `cockpit/gpt-6-astra` rather than `cockpit/gpt-5.6-sol`.

### Decision 3: OMP OmniRoute Fallback Routing
Configure `omniroute/sh/codex-x:xhigh` as default task model in `~/.omp/agent/config.yml`. Add `omniroute/sh/Claude-Fable:xhigh` to default and `phanmemvip/codex-x` fallback chains.

### Decision 4: Legacy Giaoduc Provider Deprecation
Completely remove legacy Giaoduc provider configurations from active CLI profiles (Cline `models.json`), ensuring only the four approved provider families are active.

## Verification Strategy

Automated direct and OmniRoute endpoint checks, YAML/JSON schema validation, and CLI invocation smoke tests.
