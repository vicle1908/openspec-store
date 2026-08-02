#!/bin/bash
set -euo pipefail

echo "=== Agentmemory Installation Verification ==="
echo ""

MIN_VERSION="0.9.24"

echo "1. Checking agentmemory on PATH..."
if ! command -v agentmemory &>/dev/null; then
  echo "   FAIL: agentmemory not on PATH"
  exit 1
fi
VERSION=$(agentmemory --version 2>&1)
python3 - "$VERSION" "$MIN_VERSION" <<'PY'
import sys
from packaging.version import Version
version = Version(sys.argv[1].strip())
minimum = Version(sys.argv[2])
if version < minimum:
    raise SystemExit(f"agentmemory {version} is older than required {minimum}")
print(f"   OK: agentmemory {version} >= {minimum}")
PY

echo "2. Checking OmniRoute credentials..."
if ! grep -q "^OMNIROUTE_API_KEY=" "$HOME/.tdt/.env" 2>/dev/null; then
  echo "   FAIL: OMNIROUTE_API_KEY not in ~/.tdt/.env"
  exit 1
fi
if ! grep -q "^OMNIROUTE_URL=" "$HOME/.tdt/.env" 2>/dev/null; then
  echo "   FAIL: OMNIROUTE_URL not in ~/.tdt/.env"
  exit 1
fi
echo "   OK: OmniRoute credentials found"

echo "3. Checking Ollama embedding model..."
if ! curl -sf http://localhost:11434/api/tags >/dev/null; then
  echo "   FAIL: Ollama is not reachable on localhost:11434"
  echo "   Run: brew services start ollama"
  exit 1
fi
if ! ollama list 2>/dev/null | grep -q nomic-embed-text; then
  echo "   FAIL: nomic-embed-text not pulled"
  echo "   Run: ollama pull nomic-embed-text"
  exit 1
fi
echo "   OK: nomic-embed-text available"

echo "4. Checking .env config..."
if ! (
  # shellcheck source=/dev/null
  source "$HOME/.tdt/.env" 2>/dev/null && agentmemory doctor &>/dev/null
); then
  echo "   FAIL: agentmemory doctor failed"
  echo "   Check ~/.agentmemory/.env"
  exit 1
fi
echo "   OK: Config verified"

echo ""
echo "=== ALL CHECKS PASSED ==="
