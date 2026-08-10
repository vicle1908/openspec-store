# INSTALL-01: Pre-install touched-surface manifest

Captured: 2026-08-09

## Binary resolution

- `command -v prime-agent`: NOT_FOUND
- `prime-agent --version`: NOT_INSTALLED

## User-level state

| Path | Exists | Mode | Notes |
|---|---|---|---|
| `~/.prime/` | yes | 0755 | uid 502, size 96 |
| `~/.prime/agent/` | yes | 0755 | uid 502, size 224 |
| `~/.prime/agent/auth.json` | no | — | — |
| `~/.prime/agent/models.json` | no | — | — |
| `~/.prime/agent/settings.json` | no | — | — |
| `~/.prime/sessions/` | no | — | — |
| `~/.prime/logs/` | no | — | — |
| `~/.prime/kernel/` | no | — | — |
| `~/.prime/daemon.sock` | no | — | — |

## Shell startup files

| File | Exists | SHA-256 |
|---|---|---|
| `~/.zshrc` | yes | `68f3f769377c8a6154aa3d0d5139ef76af9b5728f053cfe1a6bc2fc20224ae8c` |
| `~/.bashrc` | no | — |
| `~/.bash_profile` | no | — |
| `~/.zprofile` | yes | `3f9987e0011028369ab14476fae316a828630f062116677a70fbed9853f9a9ec` |
| `~/.config/fish/config.fish` | no | — |

## Protected configs (stability baselines)

| File | SHA-256 |
|---|---|
| `~/.hermes/config.yaml` | `3a3f2aeaa827d6704e520087be11860c950b8677ac9697cacaf7d8822bbae3da` |
| `~/.tdt/config.yaml` | `54ad6566aaea46a98f299de0bddbabfb359250910688fb2e780e1f2a9b8d16f7` |

## Credential variable presence

| Variable | Present |
|---|---|
| `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` | no |
| `HERMES_CUSTOM_GIAODUC_API_KEY` | no |
| `HERMES_CUSTOM_COCKPIT_API_KEY` | no |

## Evidence class

Discovery only. No installation, no config write, no provider call.

## Pass

Every path listed above has been checked; existence, owner, mode, and hash recorded. No credential values present in manifest.
