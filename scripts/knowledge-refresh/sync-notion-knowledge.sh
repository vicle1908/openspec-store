#!/usr/bin/env bash
# sync-notion-knowledge.sh — Fail-closed ecosystem knowledge sync to Notion via ntn CLI.
# Usage: sync-notion-knowledge.sh [OPTIONS]
# Options:
#   --dry-run            Simulate execution without modifying Notion or manifest
#   --section <name>     Sync only specific section: concepts, entities, specs, freshness
#   --force              Bypass SHA-256 cache and force re-upload
#   --all                Full sync across all sections (default)
#   --incremental        Only sync modified/new items (default)
#   -h, --help           Show this help message

set -euo pipefail

# Environment & Binary
export PATH="${HOME}/.npm-global/bin:${HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
readonly NTN_BIN="${NTN_BIN:-${HOME}/.local/bin/ntn}"
export SSL_CERT_FILE="${SSL_CERT_FILE:-/etc/ssl/cert.pem}"
if [[ -z "${NOTION_API_TOKEN:-}" && -f "${HOME}/.config/notion/.token" ]]; then
  NOTION_API_TOKEN="$(cat "${HOME}/.config/notion/.token")"
  export NOTION_API_TOKEN
fi

# Directory & Manifest Paths
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly _SCRIPT_DIR
readonly WORKSPACE_ROOT="${WORKSPACE_ROOT:-${HOME}/Developer}"
readonly OPENSPEC_STORE_ROOT="${OPENSPEC_STORE_ROOT:-${WORKSPACE_ROOT}/platform/openspec-store}"
export OPENSPEC_STORE_ROOT
readonly STATE_DIR="${STATE_DIR:-${WORKSPACE_ROOT}/.knowledge-refresh}"
readonly MANIFEST_FILE="${MANIFEST_FILE:-${STATE_DIR}/notion-sync-manifest.json}"
readonly LOG_FILE="${LOG_FILE:-${STATE_DIR}/notion-sync.log}"

# Notion Knowledge Targets (Parameterized via Environment)
KNOWLEDGE_ROOT_ID="${NOTION_KNOWLEDGE_ROOT_ID:-}"
PACING_DELAY_SEC="${PACING_DELAY_SEC:-0.5}"
# Section Display Names
readonly SECTION_NAME_CONCEPTS="Ecosystem Concepts & Architecture"
readonly SECTION_NAME_ENTITIES="Ecosystem Component Entities"
readonly SECTION_NAME_SPECS="OpenSpec Architecture & Specifications"
readonly SECTION_NAME_FRESHNESS="Knowledge Health & Freshness Matrix"

# Operational Flags
DRY_RUN=false
FORCE=false
TARGET_SECTION="all"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --force) FORCE=true; shift ;;
    --section) TARGET_SECTION="$2"; shift 2 ;;
    --all) TARGET_SECTION="all"; shift ;;
    --incremental) shift ;;
    -h|--help)
      grep '^# ' "${BASH_SOURCE[0]}" | cut -c 3-
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Logging helper (directs to log file and stderr so stdout captures stay clean)
log() {
  local level="$1" msg="$2"
  if [[ "$DRY_RUN" == "true" ]]; then
    printf '[%s] [%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$level" "$msg" >&2
  else
    printf '[%s] [%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$level" "$msg" | tee -a "$LOG_FILE" >&2
  fi
}

# Fail-closed secret sanitization & dynamic path normalization
# Returns sanitized content via stdout
sanitize_content() {
  sed -E \
    -e 's/(MCPR_TOKEN|AGENTMEMORY_URL|AGENTMEMORY_SECRET|GITNEXUS_EMBEDDING_API_KEY|GITNEXUS_MCP_AUTH_TOKEN|GITNEXUS_WIKI_API_KEY|GITHUB_TOKEN|GEMINI_API_KEY|GOOGLE_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|NEO4J_PASSWORD|FALKORDB_PASSWORD|GRAPHIFY_POSTGRES_DSN)=["'"'"']?[^[:space:]"'"'"']+["'"'"']?/\1=REDACTED/g' \
    -e 's/((api[_-]?key|auth[_-]?token|bearer[_-]?token|password|secret|token)=)["'"'"']?[^[:space:]"'"'"']+["'"'"']?/\1REDACTED/Ig' \
    -e 's#([a-zA-Z0-9+.-]+://)[^/@[:space:]]+:[^/@[:space:]]+@#\1REDACTED@#g' \
    -e 's#/Users/[a-zA-Z0-9_.-]+/Developer/#~/Developer/#g' \
    -e 's#/Users/[a-zA-Z0-9_.-]+(/|[:"'\''`[:space:]]|$)#~\1#g'
}

# Residual secret scanner with explicit disclosure allowlist
# Fails closed if any unredacted credential, token, or private key is detected
scan_residual_secrets() {
  local content="$1"
  SCAN_PAYLOAD="$content" python3 - << 'PYEOF'
import sys, os, re

content = os.environ.get("SCAN_PAYLOAD", "")

ALLOWLIST = {
    "redacted", "<redacted>", "[redacted]", "xxx", "test", "dummy", "example",
    "placeholder", "<token>", "<key>", "your_api_key", "your-api-key", "none", "null"
}

# 1. Private keys
if re.search(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", content):
    print("Residual secret scan: Detected private key block in payload", file=sys.stderr)
    sys.exit(1)

# 2. Known token signatures
token_patterns = [
    r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{16,}\b",
    r"\bsk-[A-Za-z0-9_-]{20,}\b",
    r"\bsk-ant-[A-Za-z0-9_-]{20,}\b",
    r"\bAIza[0-9A-Za-z\-_]{35}\b",
    r"\bxox[baprs]-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24,}\b",
]
for pat in token_patterns:
    for m in re.finditer(pat, content):
        val = m.group(0).lower()
        if not any(al in val for al in ALLOWLIST):
            print(f"Residual secret scan: Detected unredacted token ({m.group(0)[:8]}...)", file=sys.stderr)
            sys.exit(1)

# 3. Known secret environment variable assignments
secret_env_vars = [
    "MCPR_TOKEN", "AGENTMEMORY_SECRET", "GITNEXUS_EMBEDDING_API_KEY",
    "GITNEXUS_MCP_AUTH_TOKEN", "GITNEXUS_WIKI_API_KEY", "GITHUB_TOKEN",
    "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "NEO4J_PASSWORD", "FALKORDB_PASSWORD", "GRAPHIFY_POSTGRES_DSN"
]
for env_var in secret_env_vars:
    for m in re.finditer(rf"\b{env_var}=([^\s\"\'\`]+)", content):
        val = m.group(1).strip()
        if val != "REDACTED" and val.lower() not in ALLOWLIST and not val.startswith("$"):
            print(f"Residual secret scan: Detected unredacted secret assignment: {env_var}", file=sys.stderr)
            sys.exit(1)

# 4. Generic credential assignments
for m in re.finditer(r"\b(api[_-]?key|auth[_-]?token|bearer[_-]?token|password|secret|token)=([^\s\"\'\`]+)", content, re.IGNORECASE):
    val = m.group(2).strip().lower()
    if val != "redacted" and val not in ALLOWLIST and not val.startswith("$"):
        print(f"Residual secret scan: Detected unredacted credential assignment: {m.group(1)}", file=sys.stderr)
        sys.exit(1)

sys.exit(0)
PYEOF
}
ensure_manifest() {
  if [[ "$DRY_RUN" == "true" ]]; then
    return 0
  fi
  mkdir -p "$STATE_DIR"
  touch "$LOG_FILE"
  if [[ ! -f "$MANIFEST_FILE" ]] || ! jq -e . "$MANIFEST_FILE" >/dev/null 2>&1; then
    cat <<EOF > "$MANIFEST_FILE"
{
  "version": "1.0",
  "knowledge_root_id": "${KNOWLEDGE_ROOT_ID}",
  "sections": {},
  "documents": {},
  "last_synced_at": null
}
EOF
  fi
}
# Initialize manifest if missing
ensure_manifest() {
  mkdir -p "$STATE_DIR"
  touch "$LOG_FILE"
  if [[ ! -f "$MANIFEST_FILE" ]] || ! jq -e . "$MANIFEST_FILE" >/dev/null 2>&1; then
    cat <<EOF > "$MANIFEST_FILE"
{
  "version": "1.0",
  "knowledge_root_id": "${KNOWLEDGE_ROOT_ID}",
  "sections": {},
  "documents": {},
  "last_synced_at": null
}
EOF
  fi
}

# Bootstrap section sub-pages under Knowledge Root using regex discovery
# Returns section page ID via stdout
bootstrap_section() {
  local section_key="$1"
  local section_title="$2"
  local section_desc="$3"

  # 1. Environment variable override
  local env_id=""
  case "$section_key" in
    concepts) env_id="${NOTION_SECTION_CONCEPTS_ID:-}" ;;
    entities) env_id="${NOTION_SECTION_ENTITIES_ID:-}" ;;
    specs) env_id="${NOTION_SECTION_SPECS_ID:-}" ;;
    freshness) env_id="${NOTION_SECTION_FRESHNESS_ID:-}" ;;
  esac
  if [[ -n "$env_id" ]]; then
    echo "$env_id"
    return 0
  fi

  # 2. Check if already recorded in manifest
  if [[ -f "$MANIFEST_FILE" ]]; then
    local recorded_id
    recorded_id="$(jq -r "try (.sections[\"${section_key}\"]) // empty" "$MANIFEST_FILE" 2>/dev/null || true)"
    if [[ -n "$recorded_id" ]]; then
      echo "$recorded_id"
      return 0
    fi
  fi

  # 3. Dry-run mode: strictly read-only, never mutate manifest or call ntn
  if [[ "$DRY_RUN" == "true" ]]; then
    log "INFO" "[DRY-RUN] Section '${section_title}' (${section_key}) discovery simulated"
    echo "dry-run-section-${section_key}-id"
    return 0
  fi

  ensure_manifest

  # 4. Require KNOWLEDGE_ROOT_ID for live discovery/creation
  if [[ -z "$KNOWLEDGE_ROOT_ID" ]]; then
    log "ERROR" "KNOWLEDGE_ROOT_ID is required to bootstrap section '${section_title}' but is unset"
    return 1
  fi

  # 5. Inspect child pages of Knowledge Root via regex
  log "INFO" "Discovering child pages of Knowledge Root to locate section '${section_title}'..."
  local root_md="" root_status=0
  root_md="$("$NTN_BIN" pages get "$KNOWLEDGE_ROOT_ID" 2>/dev/null)" || root_status=$?

  local discovered_id=""
  if [[ $root_status -eq 0 && -n "$root_md" ]]; then
    while IFS= read -r line; do
      if [[ "$line" =~ \<page\ url=\"https://app\.notion\.com/p/([0-9a-f]+)\"\>(.+)\</page\> ]]; then
        local page_id="${BASH_REMATCH[1]}"
        local page_title="${BASH_REMATCH[2]}"
        if [[ "$page_title" == "$section_title" ]]; then
          discovered_id="$page_id"
          break
        fi
      fi
    done <<< "$root_md"
  fi

  if [[ -n "$discovered_id" ]]; then
    log "INFO" "Discovered existing section page for '${section_title}' (ID: ${discovered_id})"
    local tmp_manifest
    tmp_manifest="$(mktemp "${MANIFEST_FILE}.tmp.XXXXXX")"
    jq ".sections[\"${section_key}\"] = \"${discovered_id}\"" "$MANIFEST_FILE" > "$tmp_manifest"
    mv "$tmp_manifest" "$MANIFEST_FILE"
    echo "$discovered_id"
    return 0
  fi

  # 6. Create new section page under Knowledge Root
  log "INFO" "Creating new section page '${section_title}' under Knowledge Root..."
  local content
  content="$(cat <<EOF
---
title: ${section_title}
---

# ${section_title}

> Automated Ecosystem Knowledge Hub Section
> Last synchronized: $(date -u '+%Y-%m-%d %H:%M:%SZ')

${section_desc}
EOF
)"

  local create_res="" create_status=0
  create_res="$(printf '%s' "$content" | "$NTN_BIN" pages create --parent "page:${KNOWLEDGE_ROOT_ID}" --json 2>&1)" || create_status=$?

  if [[ $create_status -ne 0 ]]; then
    log "ERROR" "Failed to create section page '${section_title}': exit code ${create_status}, output: ${create_res}"
    return 1
  fi

  local new_id=""
  new_id="$(echo "$create_res" | jq -r '.id // empty' 2>/dev/null || true)"

  if [[ -z "$new_id" ]]; then
    log "ERROR" "Failed to parse page ID from section creation output: ${create_res}"
    return 1
  fi

  log "INFO" "Successfully created section '${section_title}' (ID: ${new_id})"
  local tmp_manifest
  tmp_manifest="$(mktemp "${MANIFEST_FILE}.tmp.XXXXXX")"
  jq ".sections[\"${section_key}\"] = \"${new_id}\"" "$MANIFEST_FILE" > "$tmp_manifest"
  mv "$tmp_manifest" "$MANIFEST_FILE"
  sleep "$PACING_DELAY_SEC"
  echo "$new_id"
  return 0
}

bootstrap_all_sections() {
  log "INFO" "Bootstrapping 4 Knowledge Root sections..."
  bootstrap_section "concepts" "$SECTION_NAME_CONCEPTS" "Curated architectural patterns, platform concepts, and durable system models across the workspace." >/dev/null
  bootstrap_section "entities" "$SECTION_NAME_ENTITIES" "Core repository, microservice, agent runtime, and tooling entity definitions." >/dev/null
  bootstrap_section "specs" "$SECTION_NAME_SPECS" "Domain catalog of OpenSpec specifications and in-flight governance changes." >/dev/null
  bootstrap_section "freshness" "$SECTION_NAME_FRESHNESS" "Nightly knowledge index health and commit-equality freshness reports." >/dev/null
}

# Sync a single markdown document into Notion
# Arguments: $1 = local_file_rel_path, $2 = section_key, $3 = optional_display_title
sync_document() {
  local rel_path="$1"
  local section_key="$2"
  local override_title="${3:-}"
  local full_path="${WORKSPACE_ROOT}/${rel_path}"

  if [[ ! -f "$full_path" ]]; then
    log "WARN" "Source file does not exist: ${full_path}"
    return 0
  fi

  # Extract or infer title
  local title="$override_title"
  if [[ -z "$title" ]]; then
    title="$(grep -m1 '^title:' "$full_path" 2>/dev/null | sed -E 's/^title:[[:space:]]*["'"'"']?([^"'"'"']+)["'"'"']?/\1/' || true)"
    if [[ -z "$title" ]]; then
      title="$(grep -m1 '^# ' "$full_path" 2>/dev/null | sed 's/^# //' || true)"
    fi
    if [[ -z "$title" ]]; then
      title="$(basename "$rel_path" .md)"
    fi
  fi

  # Prepare sanitized content
  local body_content
  body_content="$(sanitize_content < "$full_path")"

  # Residual secret scan - fail-closed before upload
  if ! scan_residual_secrets "$body_content"; then
    log "ERROR" "Residual secret scan failed for '${rel_path}'. Aborting fail-closed."
    return 1
  fi

  # Stable SHA-256 based on sanitized body content for idempotency
  local current_sha
  current_sha="$(printf '%s' "$body_content" | shasum -a 256 | awk '{print $1}')"

  local recorded_sha="" recorded_page_id=""
  if [[ -f "$MANIFEST_FILE" ]]; then
    recorded_sha="$(jq -r "try (.documents[\"${rel_path}\"].sha256) // empty" "$MANIFEST_FILE" 2>/dev/null || true)"
    recorded_page_id="$(jq -r "try (.documents[\"${rel_path}\"].page_id) // empty" "$MANIFEST_FILE" 2>/dev/null || true)"
  fi

  if [[ "$FORCE" != "true" ]] && [[ -n "$recorded_page_id" ]] && [[ "$recorded_sha" == "$current_sha" ]]; then
    log "INFO" "fresh_noop: ${rel_path} (Page ID: ${recorded_page_id})"
    return 0
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    local action="create"
    [[ -n "$recorded_page_id" ]] && action="edit (${recorded_page_id})"
    log "INFO" "[DRY-RUN] Would sync '${title}' (${rel_path}) -> ${action}"
    return 0
  fi

  ensure_manifest

  local sanitized_content
  sanitized_content="$(cat <<EOF
---
title: ${title}
---

> **Ecosystem Knowledge Synchronization**
> Source: \`${rel_path}\`

${body_content}
EOF
)"

  local section_id=""
  case "$section_key" in
    concepts) section_id="${NOTION_SECTION_CONCEPTS_ID:-}" ;;
    entities) section_id="${NOTION_SECTION_ENTITIES_ID:-}" ;;
    specs) section_id="${NOTION_SECTION_SPECS_ID:-}" ;;
    freshness) section_id="${NOTION_SECTION_FRESHNESS_ID:-}" ;;
  esac
  if [[ -z "$section_id" && -f "$MANIFEST_FILE" ]]; then
    section_id="$(jq -r ".sections[\"${section_key}\"] // empty" "$MANIFEST_FILE" 2>/dev/null || true)"
  fi
  if [[ -z "$section_id" ]]; then
    log "ERROR" "Section ID for '${section_key}' not found in environment or manifest"
    return 1
  fi

  if [[ -n "$recorded_page_id" ]]; then
    log "INFO" "Updating Notion page ${recorded_page_id} for '${title}' (${rel_path})..."
    local edit_out="" edit_status=0
    edit_out="$(printf '%s' "$sanitized_content" | "$NTN_BIN" pages edit "$recorded_page_id" --allow-deleting-content --json 2>&1)" || edit_status=$?
    sleep "$PACING_DELAY_SEC"

    if [[ $edit_status -ne 0 ]]; then
      log "ERROR" "Failed to update page ${recorded_page_id} for '${title}' (${rel_path}): exit code ${edit_status}, output: ${edit_out}"
      return 1
    fi

    local receipt_id=""
    receipt_id="$(echo "$edit_out" | jq -r '.id // empty' 2>/dev/null || true)"
    if [[ -z "$receipt_id" ]]; then
      log "ERROR" "Write receipt validation failed for page ${recorded_page_id} ('${title}'): missing page ID in output: ${edit_out}"
      return 1
    fi

    local tmp_manifest
    tmp_manifest="$(mktemp "${MANIFEST_FILE}.tmp.XXXXXX")"
    jq ".documents[\"${rel_path}\"] = {page_id: \"${receipt_id}\", sha256: \"${current_sha}\", title: \"${title}\", last_synced: \"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\"}" "$MANIFEST_FILE" > "$tmp_manifest"
    mv "$tmp_manifest" "$MANIFEST_FILE"
    log "INFO" "Successfully updated page ${receipt_id} for '${title}'"
  else
    log "INFO" "Creating new Notion page under section '${section_key}' for '${title}' (${rel_path})..."
    local create_out="" create_status=0
    create_out="$(printf '%s' "$sanitized_content" | "$NTN_BIN" pages create --parent "page:${section_id}" --json 2>&1)" || create_status=$?
    sleep "$PACING_DELAY_SEC"

    if [[ $create_status -ne 0 ]]; then
      log "ERROR" "Failed to create page for '${title}' (${rel_path}): exit code ${create_status}, output: ${create_out}"
      return 1
    fi

    local new_page_id=""
    new_page_id="$(echo "$create_out" | jq -r '.id // empty' 2>/dev/null || true)"

    if [[ -z "$new_page_id" ]]; then
      log "ERROR" "Write receipt validation failed on create for '${title}' (${rel_path}): missing page ID: ${create_out}"
      return 1
    fi

    local tmp_manifest
    tmp_manifest="$(mktemp "${MANIFEST_FILE}.tmp.XXXXXX")"
    jq ".documents[\"${rel_path}\"] = {page_id: \"${new_page_id}\", sha256: \"${current_sha}\", title: \"${title}\", last_synced: \"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\"}" "$MANIFEST_FILE" > "$tmp_manifest"
    mv "$tmp_manifest" "$MANIFEST_FILE"
    log "INFO" "Successfully created page ${new_page_id} for '${title}'"
  fi
  return 0
}

sync_concepts() {
  log "INFO" "Syncing Ecosystem Concepts & Architecture..."
  local files=(
    "wiki/concepts/go-microservices-platform.md"
    "wiki/concepts/go-platform-architecture.md"
    "wiki/concepts/python-agent-ecosystem.md"
    "wiki/concepts/mcp-transport-layer.md"
    "wiki/concepts/openspec-change-lifecycle.md"
    "wiki/concepts/knowledge-graph-system.md"
    "wiki/concepts/workspace-domain-topology.md"
    "wiki/concepts/workstation-terminal-and-storage-resilience.md"
    "wiki/comparisons/knowledge-tools.md"
    "wiki/architecture/agent-core-llm-loading-and-cli-verification.md"
  )
  local f rel
  for f in "${WORKSPACE_ROOT}"/wiki/concepts/*.md; do
    [[ -f "$f" ]] || continue
    rel="wiki/concepts/$(basename "$f")"
    local seen=false existing
    for existing in "${files[@]}"; do
      if [[ "$existing" == "$rel" ]]; then seen=true; break; fi
    done
    [[ "$seen" == "true" ]] || files+=("$rel")
  done
  for file in "${files[@]}"; do
    sync_document "$file" "concepts"
  done
}

sync_entities() {
  log "INFO" "Syncing Ecosystem Component Entities..."
  local files=(
    "wiki/entities/agent-core.md"
    "wiki/entities/agentmemory.md"
    "wiki/entities/gitnexus.md"
    "wiki/entities/go-microservices.md"
    "wiki/entities/graphify.md"
    "wiki/entities/jira-skill.md"
    "wiki/entities/mcp-router.md"
    "wiki/entities/ollama-embedding-server.md"
    "wiki/entities/tdt-core.md"
    "wiki/entities/tdt-observability.md"
    "wiki/entities/tdt-sheets.md"
    "wiki/entities/webhook-receiver.md"
    "wiki/entities/notion-cli.md"
    "wiki/entities/shb.md"
    "wiki/entities/omniroute.md"
    "wiki/entities/pi.md"
    "wiki/entities/goose.md"
    "wiki/entities/kimi-code.md"
    "wiki/entities/shb-schedule.md"
    "wiki/entities/docker-workstation.md"
  )
  local f rel
  for f in "${WORKSPACE_ROOT}"/wiki/entities/*.md; do
    [[ -f "$f" ]] || continue
    rel="wiki/entities/$(basename "$f")"
    local seen=false existing
    for existing in "${files[@]}"; do
      if [[ "$existing" == "$rel" ]]; then seen=true; break; fi
    done
    [[ "$seen" == "true" ]] || files+=("$rel")
  done
  for file in "${files[@]}"; do
    sync_document "$file" "entities"
  done
}

# Generate OpenSpec specifications domain catalog and sync to Notion
generate_and_sync_specs() {
  log "INFO" "Generating OpenSpec Domain Catalog..."
  if [[ "$DRY_RUN" == "true" ]]; then
    log "INFO" "[DRY-RUN] Would generate domain catalog from OpenSpec specs and sync to specs"
    return 0
  fi
  local catalog_file="${STATE_DIR}/openspec-domain-catalog.md"

  CATALOG_FILE="$catalog_file" python3 - << 'PYEOF'
import os, glob, json, sys
from datetime import datetime, timezone

store_root = os.environ.get("OPENSPEC_STORE_ROOT", os.path.expanduser("~/Developer/platform/openspec-store"))
store_specs = os.path.join(store_root, "openspec", "specs")
all_specs = glob.glob(f"{store_specs}/**/spec.md", recursive=True)

if not all_specs:
    print(f"ERROR: Spec discovery found 0 specs at {store_specs}. Aborting fail-closed.", file=sys.stderr)
    sys.exit(1)

# Categorization domains
domains = {
    "Agent Runtime & AI Capabilities": [],
    "Documentation & Knowledge Sync": [],
    "Go Microservices Platform & Temporal": [],
    "TDT Shared SDK & Services": [],
    "MCP Transport & Agent CLI Routing": [],
    "Workspace & Knowledge Infrastructure": [],
    "General Domain Capabilities": []
}

for s in sorted(all_specs):
    rel = os.path.relpath(s, store_specs)
    cap = os.path.dirname(rel)
    # Extract purpose
    purpose = "Capability specification"
    try:
        with open(s, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith("## Purpose"):
                    for follow in lines[i+1:i+6]:
                        clean = follow.strip()
                        if clean and not clean.startswith("<!--") and not clean.startswith("#"):
                            purpose = clean
                            break
                    break
    except Exception:
        pass

    if cap.startswith("agent-core") or cap.startswith("agent-runtime") or cap.startswith("memory-") or "guardrail" in cap or "jev" in cap:
        domains["Agent Runtime & AI Capabilities"].append((cap, purpose))
    elif "doc" in cap or "wiki" in cap:
        domains["Documentation & Knowledge Sync"].append((cap, purpose))
    elif "microservices" in cap or "temporal" in cap or "postgres" in cap or "cdc" in cap:
        domains["Go Microservices Platform & Temporal"].append((cap, purpose))
    elif cap.startswith("tdt-") or "jira" in cap or "webhook" in cap or "scheduler" in cap:
        domains["TDT Shared SDK & Services"].append((cap, purpose))
    elif "mcp" in cap or "omniroute" in cap or "hermes" in cap or "omp" in cap or "claude" in cap or "coding" in cap:
        domains["MCP Transport & Agent CLI Routing"].append((cap, purpose))
    elif "knowledge" in cap or "freshness" in cap or "gitnexus" in cap or "graphify" in cap or "cleanup" in cap:
        domains["Workspace & Knowledge Infrastructure"].append((cap, purpose))
    else:
        domains["General Domain Capabilities"].append((cap, purpose))

# Discover active changes dynamically
changes_dir = os.path.join(store_root, "openspec", "changes")
active_changes = []
if os.path.isdir(changes_dir):
    for entry in sorted(os.listdir(changes_dir)):
        p = os.path.join(changes_dir, entry)
        if os.path.isdir(p) and entry != "archive" and not entry.startswith("."):
            tasks_file = os.path.join(p, "tasks.md")
            completed, total = 0, 0
            if os.path.isfile(tasks_file):
                try:
                    with open(tasks_file, "r", encoding="utf-8") as tf:
                        for line in tf:
                            if "- [x]" in line or "- [X]" in line:
                                completed += 1
                                total += 1
                            elif "- [ ]" in line:
                                total += 1
                except Exception:
                    pass
            status = f"{completed}/{total}" if total > 0 else "In-Progress"
            active_changes.append((entry, completed, total, status))

# Discover recently archived changes dynamically
archive_dir = os.path.join(changes_dir, "archive")
recent_archived = []
if os.path.isdir(archive_dir):
    for entry in sorted(os.listdir(archive_dir), reverse=True):
        p = os.path.join(archive_dir, entry)
        if os.path.isdir(p) and not entry.startswith("."):
            tasks_file = os.path.join(p, "tasks.md")
            completed, total = 0, 0
            if os.path.isfile(tasks_file):
                try:
                    with open(tasks_file, "r", encoding="utf-8") as tf:
                        for line in tf:
                            if "- [x]" in line or "- [X]" in line:
                                completed += 1
                                total += 1
                            elif "- [ ]" in line:
                                total += 1
                except Exception:
                    pass
            status = f"{completed}/{total} (Archived)" if total > 0 else "Archived"
            recent_archived.append((entry, completed, total, status))
            if len(recent_archived) >= 10:
                break

out_path = os.environ.get("CATALOG_FILE", os.path.expanduser("~/.knowledge-refresh/openspec-domain-catalog.md"))
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"> Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}\n")
    f.write(f"> Total Governed Specifications: **{len(all_specs)}**\n\n")
    f.write("## Active Changes Ledger\n\n")
    f.write("| Change Name | Completed Tasks | Total Tasks | Status |\n")
    f.write("| :--- | :--- | :--- | :--- |\n")
    if active_changes:
        for ch_name, comp, tot, stat in active_changes:
            f.write(f"| `{ch_name}` | {comp} | {tot} | {stat} |\n")
    else:
        f.write("| *None* | 0 | 0 | Clean |\n")
    f.write("\n")

    if recent_archived:
        f.write("## Recently Archived Changes\n\n")
        f.write("| Archived Change | Completed Tasks | Total Tasks | Status |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for ch_name, comp, tot, stat in recent_archived:
            f.write(f"| `{ch_name}` | {comp} | {tot} | {stat} |\n")
        f.write("\n")

    f.write("## Specifications by Architecture Domain\n\n")
    for dom_name, specs in domains.items():
        f.write(f"### {dom_name} ({len(specs)} specs)\n\n")
        f.write("| Capability | Purpose / Contract |\n")
        f.write("| :--- | :--- |\n")
        for cap, purp in specs[:20]: # Show top 20 per category in overview table
            # clean purp for table
            purp_clean = purp.replace("|", "\\|")[:120]
            f.write(f"| `{cap}` | {purp_clean} |\n")
        if len(specs) > 20:
            f.write(f"| *... and {len(specs) - 20} more capabilities* | *See platform/openspec-store/openspec/specs/* |\n")
        f.write("\n")
PYEOF

  sync_document ".knowledge-refresh/openspec-domain-catalog.md" "specs" "OpenSpec Specifications & Governance Catalog"
}

# Generate Knowledge Health & Freshness Matrix and sync to Notion
generate_and_sync_freshness() {
  log "INFO" "Generating Knowledge Health & Freshness Matrix..."
  if [[ "$DRY_RUN" == "true" ]]; then
    log "INFO" "[DRY-RUN] Would generate freshness matrix and sync to freshness"
    return 0
  fi
  local status_script="${WORKSPACE_ROOT}/scripts/knowledge-refresh/knowledge-status.sh"
  local status_json="${STATUS_JSON:-}"
  if [[ -z "$status_json" ]] && [[ -x "$status_script" ]]; then
    status_json="$("$status_script" --json 2>/dev/null || true)"
  fi
  local matrix_file="${STATE_DIR}/knowledge-freshness-matrix.md"

  STATUS_JSON="$status_json" MATRIX_FILE="$matrix_file" python3 - << 'PYEOF'
import json, os
from datetime import datetime, timezone

status_path = os.environ.get("MATRIX_FILE", os.path.expanduser("~/.knowledge-refresh/knowledge-freshness-matrix.md"))
raw_json = os.environ.get("STATUS_JSON", "")
data = {}
try:
    if raw_json:
        data = json.loads(raw_json)
except Exception:
    pass

repos = data.get("repos", [])
digest = data.get("inventoryDigest", "unknown")
versions = data.get("providerVersions", {})

# Aggregate per repo
repo_map = {}
for r in repos:
    r_name = r.get("repo")
    tool = r.get("tool")
    freshness = r.get("freshness", "UNKNOWN")
    head = r.get("headSha", "-")
    if r_name not in repo_map:
        repo_map[r_name] = {"GitNexus": "-", "Graphify": "-", "Dirty": "Clean", "HEAD": head}
    if head and head != "-" and repo_map[r_name]["HEAD"] in ("", "-"):
        repo_map[r_name]["HEAD"] = head
    if tool == "GitNexus":
        repo_map[r_name]["GitNexus"] = freshness
    elif tool == "Graphify":
        repo_map[r_name]["Graphify"] = freshness
    elif tool == "Dirty":
        repo_map[r_name]["Dirty"] = f"DIRTY ({r.get('dirtyFiles', 0)})"

with open(status_path, "w", encoding="utf-8") as f:
    f.write("# Workspace Knowledge Index Freshness Matrix\n\n")
    f.write(f"> Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}\n")
    f.write(f"> Inventory Digest: `{digest}`\n")
    f.write(f"> Tool Versions: GitNexus `{versions.get('gitnexus', '-')}`, Graphify `{versions.get('graphify', '-')}`\n\n")

    f.write(f"## {len(repo_map)}-Repository Index Freshness Matrix\n\n")
    f.write("| Repository | GitNexus Index | Graphify Graph | Workspace State | HEAD |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
    for r_name in sorted(repo_map.keys()):
        row = repo_map[r_name]
        f.write(f"| `{r_name}` | {row['GitNexus']} | {row['Graphify']} | {row['Dirty']} | `{row['HEAD']}` |\n")

    f.write("\n## Freshness SLA & Operational Rules\n\n")
    f.write("1. Freshness is strictly evaluated by commit-equality (`indexed_sha == current_head_sha`), not file timestamp.\n")
    f.write("2. LaunchAgent `com.developer.index-refresh` re-indexes all clean repositories nightly at 02:30 AM.\n")
    f.write("3. Dirty repositories and active worktrees are preserved without destructive re-indexing.\n")
PYEOF

  sync_document ".knowledge-refresh/knowledge-freshness-matrix.md" "freshness" "Workspace Knowledge Index Freshness Matrix"
}

# Export functions for testing if sourced
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  return 0 2>/dev/null || exit 0
fi

if [[ "$DRY_RUN" != "true" ]]; then
  ensure_manifest
fi
bootstrap_all_sections
case "$TARGET_SECTION" in
  concepts)
    sync_concepts
    ;;
  entities)
    sync_entities
    ;;
  specs)
    generate_and_sync_specs
    ;;
  freshness)
    STATUS_JSON="$("${WORKSPACE_ROOT}/scripts/knowledge-refresh/knowledge-status.sh" --json 2>/dev/null || echo '')" \
    generate_and_sync_freshness
    ;;
  all)
    sync_concepts
    sync_entities
    generate_and_sync_specs
    STATUS_JSON="$("${WORKSPACE_ROOT}/scripts/knowledge-refresh/knowledge-status.sh" --json 2>/dev/null || echo '')" \
    generate_and_sync_freshness
    ;;
  *)
    log "ERROR" "Unknown section: $TARGET_SECTION"
    exit 1
    ;;
esac

log "INFO" "Sync completed successfully."
