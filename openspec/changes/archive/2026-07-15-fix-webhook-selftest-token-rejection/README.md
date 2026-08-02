# fix-webhook-selftest-token-rejection

Webhook selftest probe sends an empty X-Gitlab-Token; receiver rejects with 401 because GITLAB_WEBHOOK_SECRET is set in deployment. Forward the real secret to the probe workflow.
