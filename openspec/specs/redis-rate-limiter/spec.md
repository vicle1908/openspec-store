# redis-rate-limiter

## Purpose

Distributed rate limiting for the notification-service using Redis 8.8 `INCREX` command. This is a greenfield implementation using only modern Redis 8.8 features — no legacy fallbacks.

## Current State

- `ports.RateLimiter` interface exists: `Allow(ctx, channel) (allowed bool, delay time.Duration, err error)`
- Interface is channel-based (not recipient-based)
- No Redis adapter exists for rate limiting
- Mock rate limiter used in tests (`TestDispatch_RateLimited`, `TestDispatch_LimiterError`)

## Dependencies

- go-redis v9.21.0 (latest, supports Redis 8.8 INCREX via `Do()` command)
- Redis 8.8-alpine (pinned in `deploy/tools.env`)
- No fallback to older Redis versions — this is greenfield

## Requirements

### Requirement: RR-001: Rate Limiter Interface

The notification-service SHALL implement the existing `ports.RateLimiter` interface with Redis-backed rate limiting. The interface SHALL be extended to support per-recipient limiting.

#### Scenario: Interface Extension
Given the existing `ports.RateLimiter` interface
When extended for recipient-based limiting
Then the signature SHALL be `Allow(ctx context.Context, channel notification.Channel, recipientID string) (allowed bool, retryAfter time.Duration, err error)`

### Requirement: RR-002: INCREX Implementation (Redis 8.8)

The rate limiter implementation SHALL use Redis 8.8 `INCREX` command for atomic rate limiting. The command syntax is:
```
INCREX key [BYINT increment] [UBOUND upperbound] [EX seconds] [ENX]
```
The response is `[current_value, delta]` where `delta=0` indicates rate limit exceeded.

The implementation SHALL:
- Use key pattern `rate:<channel>:<recipientID>`
- Use `BYINT 1` for integer increment
- Use `UBOUND <limit>` for upper bound (rate limit)
- Use `EX <window_seconds>` for expiry
- Use `ENX` to set TTL only on first request (not reset on subsequent)
- Return `[current_value, delta]` array from Redis
- Treat `delta=0` as rate limit exceeded

#### Scenario: Within Rate Limit
Given a recipient with 0 requests in the current window
When `Allow(ctx, email, "user-123")` is called
Then it shall execute `INCREX rate:email:user-123 BYINT 1 UBOUND 100 EX 60 ENX`
And the response shall be `[1, 1]` (current_value=1, delta=1)
And it shall return `allowed=true`

#### Scenario: Rate Limit Exceeded
Given a recipient with 100 requests in the current window (limit=100)
When `Allow(ctx, email, "user-123")` is called
Then it shall execute `INCREX rate:email:user-123 BYINT 1 UBOUND 100 EX 60 ENX`
And the response shall be `[100, 0]` (current_value=100, delta=0)
And it shall return `allowed=false`
And `retryAfter` shall be the TTL remaining on the key

#### Scenario: First Request (TTL Set)
Given a recipient with no existing key
When `Allow(ctx, email, "user-123")` is called with `ENX`
Then the TTL shall be set to 60 seconds
And subsequent requests within the window shall NOT reset the TTL

### Requirement: RR-003: Per-Channel Configuration

Rate limits SHALL be configurable per notification channel (email, SMS, push). Different channels SHALL have different limits and windows.

#### Scenario: Email Rate Limit
Given email channel with limit=100, window=60s
When 100 emails are sent to a recipient in 60 seconds
Then the 101st shall be rate limited

#### Scenario: SMS Rate Limit
Given SMS channel with limit=10, window=60s
When 10 SMS are sent to a recipient in 60 seconds
Then the 11th shall be rate limited

### Requirement: RR-004: Graceful Degradation

When Redis is unavailable, the rate limiter SHALL fail open (allow all requests) rather than blocking legitimate traffic. The failure SHALL be logged as a warning.

#### Scenario: Redis Outage
Given Redis is unreachable
When `Allow(ctx, email, "user-123")` is called
Then it shall return `allowed=true`
And it shall log a warning: `rate limiter unavailable, failing open`

#### Scenario: Redis Outage with Error
Given the existing `TestDispatch_LimiterError` test
When the rate limiter returns an error
Then the dispatcher SHALL handle the error gracefully
And the notification SHALL be dispatched (fail open)

### Requirement: RR-005: Key Namespace

Rate limiter keys SHALL use the namespace `rate:<channel>:<recipientID>` to avoid collision with other Redis data. The namespace SHALL be configurable.

#### Scenario: Key Pattern
Given the rate limiter with default namespace
When checking rate limit for email to `user-123`
Then the Redis key shall be `rate:email:user-123`

### Requirement: RR-006: Adapter Location

The Redis rate limiter adapter SHALL be placed in `services/notification-service/internal/adapters/redis/ratelimiter.go`. The adapter SHALL implement `ports.RateLimiter`.

#### Scenario: Adapter Structure
Given the notification-service adapter directory
When the rate limiter adapter is created
Then it shall be at `internal/adapters/redis/ratelimiter.go`
And it shall implement `ports.RateLimiter`
