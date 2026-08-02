# scheduler-entrypoint-log-hygiene

Add line-buffering (stdbuf) and startup rotation to scheduler entrypoint dual-sink logging. Fixes tee's 8 KB block-buffering that delays structlog lines from reaching docker logs and the host file. Adds 50 MB rotation at startup.
