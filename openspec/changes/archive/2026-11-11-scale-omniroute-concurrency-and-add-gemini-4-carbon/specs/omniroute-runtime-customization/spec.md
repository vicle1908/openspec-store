# omniroute-runtime-customization Spec Delta

## ADDED Requirements

### Requirement: High-Concurrency Heavyweight Chat Admission, Queue Byte Budgets, and Libuv Threadpool Scaling via Configuration Only
The OmniRoute gateway deployment (`/Users/androidteam/Omniroute/.env` and `/Users/androidteam/Omniroute/docker-compose.override.yml`) SHALL configure `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=32`, `OMNIROUTE_CHAT_ADMISSION_MAX_QUEUED_BYTES=67108864`, `OMNIROUTE_CHAT_MAX_INFLIGHT_BYTES=268435456`, `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=30000`, and `UV_THREADPOOL_SIZE=32` while keeping zero tracked git modifications in `/Users/androidteam/Omniroute` and fast-forwarding local `main` to `origin/main`.

#### Scenario: 32 primary heavy slots plus 32 healthy-heap headroom slots admit up to 64 concurrent tool-bearing agent streams without queueing
- **WHEN** the `omniroute` container is running under `--profile base` and `docker exec omniroute env` is inspected
- **THEN** `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT` SHALL be `32`, `OMNIROUTE_CHAT_ADMISSION_MAX_QUEUED_BYTES` SHALL be `67108864` (`64 MB`), `OMNIROUTE_CHAT_MAX_INFLIGHT_BYTES` SHALL be `268435456` (`256 MB`), `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS` SHALL be `30000` (`30s`), and `UV_THREADPOOL_SIZE` SHALL be `32`
- **AND** up to 64 concurrent heavy requests (`tools.length >= 64` or `content-length >= 256 KB`) while V8 heap utilization is below `0.75` and total active request bytes are below `256 MB` SHALL be admitted immediately without entering the wait queue or returning `HTTP 503 chat_admission_busy`

#### Scenario: Burst overflow beyond active heavy slots parks up to 64 MB in the fairness queue without premature 4 MB byte-budget shedding
- **WHEN** a burst of concurrent heavy requests exceeds active heavy admission slots and waits in `acquireHeavyWithin(30000)`
- **THEN** parked waiters up to `67,108,864` bytes (`64 MB`) total buffered payload SHALL remain queued for up to `30,000 ms` rather than being immediately shed at the legacy `4,194,304` byte (`4 MB`) default with `reason: "queued_bytes_budget"`

#### Scenario: Upstream git checkout remains clean and fast-forwarded for official release upgrades
- **WHEN** `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` and `git -C /Users/androidteam/Omniroute rev-list --left-right --count HEAD...origin/main` are executed
- **THEN** `git status --porcelain --untracked-files=no` SHALL output zero lines (all runtime tuning confined to untracked `.env`, `docker-compose.override.yml`, and the `omniroute-data` SQLite volume)
- **AND** local `main` SHALL be fast-forwarded to `origin/main` (`0` commits behind) so `~/Omniroute/scripts/update.sh` Gate P and Gate 8b (`MEM_OFF|CACHE_ALIGNED|COMP_OFF|TTFT_ZERO|PATCH_OK`) pass without manual conflict resolution
