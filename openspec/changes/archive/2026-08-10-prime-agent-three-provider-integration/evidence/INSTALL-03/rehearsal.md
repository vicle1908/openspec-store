# INSTALL-03: Isolated Rehearsal

Date: 2026-08-09

## Setup

- Isolated HOME: `/var/folders/zw/k5ybx0c55rs88r9d09kxly8w0000gp/T/tmp.XXXXXXXX`
- Installer: `evidence/research/install.sh` (SHA-256 `38d14a1...`)
- Node.js: v26.7.0

## Installation results

- Native installer status: success
- Downloaded artifact: `prime-agent-0.7.1.tgz`
- Checksum verification: `prime-agent-0.7.1.tgz: OK`
- 193 packages installed in ~32s

## Verification

| Check | Expected | Observed | Status |
|---|---|---|---|
| `prime-agent --version` | `0.7.1` | `0.7.1` | PASS |
| `command -v prime-agent` | resolves | `/opt/homebrew/bin/prime-agent` | PASS |
| Binary SHA-256 | recorded | `16e2324a4e3aa13305c437168d44d7395bab317e292218a52d1c61a7ebdf0993` | PASS |
| `prime-agent --help` | exits 0 | exits 0 | PASS |
| `prime-agent status` | no crash | "No background services found." | PASS |
| `prime-agent doctor` | no crash | "No background services found." | PASS |

## Registry probe

- Isolated `models.json` with 3 providers, 5 models loaded and parsed correctly.
- `prime-agent model list` returned empty (expected: env var references not loaded in isolated context).

## Touched paths

Recorded under `evidence/INSTALL-03/touched-paths.txt`. Installation created directories under isolated HOME only; no global state was modified.

## Evidence class

Installation/identity only. No config mutation, no provider calls.

## Pass

Version, binary, hash, help, status, doctor, and model registry parsing all match expectations.
