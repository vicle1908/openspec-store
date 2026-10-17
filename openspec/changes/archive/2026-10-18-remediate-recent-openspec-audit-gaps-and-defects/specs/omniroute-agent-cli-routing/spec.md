# omniroute-agent-cli-routing Specification Delta

## ADDED Requirements

### Requirement: OmniRoute Muse Code compatibility layer SHALL persist across container recreations without dirtying upstream git

Any OmniRoute compatibility layer required by Meta Muse Code (`/muse-code` catalog path rewrite and non-null `resp_keepalive` identifier on `/v1/responses`) SHALL be wired through untracked deployment overrides (`docker-compose.override.yml` and host-mounted runtime scripts) rather than ephemeral writable-layer container edits or modifications to git-tracked upstream source files in `~/Omniroute`.

#### Scenario: Compatibility layer survives compose down and up lifecycle
- **WHEN** `~/Developer/scripts/docker-service.sh stop` and `~/Developer/scripts/docker-service.sh start` (or `docker compose --profile base down` followed by `docker compose --profile base up -d`) recreate the `omniroute` container without invoking `~/Omniroute/scripts/update.sh`
- **THEN** `GET http://127.0.0.1:20128/v1/muse-code/models` and `GET http://127.0.0.1:20128/muse-code/models` SHALL both return HTTP 200 with the `muse-spark-1.3` model entry
- **AND** `POST http://127.0.0.1:20128/v1/responses` pre-flight keepalive frames SHALL carry a non-null string `response.id` compatible with Muse Code's Rust SSE decoder

#### Scenario: Upstream OmniRoute git worktree remains clean
- **WHEN** `git -C ~/Omniroute status --porcelain --untracked-files=no` is executed
- **THEN** the output SHALL be empty with zero modified tracked files (`open-sse/utils/sseHeartbeat.ts` and `scripts/dev/peer-stamp.mjs` restored to `HEAD`)
- **AND** this compose-mounted runtime override SHALL supersede the legacy transient bundle-patch prohibition for the Muse Code compatibility surface

### Requirement: Goose CLI runtime documentation SHALL accurately reflect Chat Completions wire routing

Ecosystem documentation and verification ledgers for the Goose CLI OmniRoute runtime SHALL accurately record that `custom_omniroute` routes over OpenAI Chat Completions (`/v1/chat/completions`) via `OPENAI_BASE_PATH: chat/completions` to avoid the `/v1/responses` pre-flight keepalive decoder incompatibility.

#### Scenario: Wiki and runtime config agree on Chat Completions wire dialect
- **WHEN** `wiki/entities/goose.md` and `~/.config/goose/config.yaml` are inspected
- **THEN** both artifacts SHALL identify `/v1/chat/completions` (`OPENAI_BASE_PATH: chat/completions`) as the active wire protocol for `custom_omniroute`
- **AND** neither artifact SHALL claim that Goose routes default turns through `/v1/responses`
