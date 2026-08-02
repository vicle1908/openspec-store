# redis-monitoring (delta)

## Purpose

Enhanced Redis monitoring with explicit slowlog server-side configuration.

## MODIFIED Requirements

### Requirement: RM-005: Slowlog Integration

Redis SLOWLOG SHALL be monitored. Slow commands (> 10ms) SHALL be logged and available for debugging. The exporter shall expose `redis_commands_duration_seconds` metrics. Redis nodes SHALL configure `slowlog-log-slower-than 10000` (10ms) and `slowlog-max-len 128` explicitly. The slowlog configuration SHALL NOT rely on Redis defaults.

#### Scenario: Slow Command Detection

Given a Redis node with slowlog enabled at 10ms threshold
When a command takes > 10ms
Then it shall be recorded in SLOWLOG
And the exporter shall expose the duration metric

#### Scenario: Slowlog Config Explicit

Given a Redis node with explicit slowlog configuration
When the node starts
Then `slowlog-log-slower-than` shall be `10000`
And `slowlog-max-len` shall be `128`
And the configuration shall NOT depend on Redis defaults

#### Scenario: Slowlog Retrieval

Given a Redis node with slowlog entries
When `SLOWLOG GET 10` is executed
Then up to 10 slow commands shall be returned
And each entry shall show command name, duration, and timestamp
