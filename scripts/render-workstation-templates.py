#!/usr/bin/env python3
"""Workstation template renderer.

Renders launchd plist and shell configuration templates by substituting registered
variables ({{HOME}}, {{HOMEBREW_PREFIX}}, {{WORKSPACE_ROOT}}, {{OPENSPEC_STORE_ROOT}})
with concrete absolute paths. Standard library only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
preflight_path = SCRIPT_DIR / "bootstrap-workstation-preflight.py"
if preflight_path.is_file():
    _spec = importlib.util.spec_from_file_location("bootstrap_workstation_preflight", preflight_path)
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules["bootstrap_workstation_preflight"] = _mod
    _spec.loader.exec_module(_mod)
    detect_system_info = _mod.detect_system_info
else:
    def detect_system_info(**kwargs):
        return {
            "home": str(Path.home()),
            "homebrew_prefix": "/opt/homebrew",
            "workspace_root": str(Path.home() / "Developer"),
            "openspec_store_root": str(Path.home() / "Developer" / "platform" / "openspec-store"),
        }

REGISTERED_VARIABLES = {
    "HOME",
    "HOMEBREW_PREFIX",
    "WORKSPACE_ROOT",
    "OPENSPEC_STORE_ROOT",
}


@dataclass
class RenderResult:
    source_path: str
    target_path: str | None
    unresolved_tags: list[str]
    success: bool
    content: str | None = None
    error: str | None = None


def build_variable_context(
    home: str | None = None,
    homebrew_prefix: str | None = None,
    workspace_root: str | None = None,
    openspec_store_root: str | None = None,
    arch: str | None = None,
    extra_vars: dict[str, str] | None = None,
) -> dict[str, str]:
    """Build the dictionary of replacement variables."""
    sys_info = detect_system_info(
        arch_override=arch,
        home_override=home,
        brew_prefix_override=homebrew_prefix,
        workspace_root_override=workspace_root,
        store_root_override=openspec_store_root,
    )

    ctx = {
        "HOME": sys_info["home"],
        "HOMEBREW_PREFIX": sys_info["homebrew_prefix"],
        "WORKSPACE_ROOT": sys_info["workspace_root"],
        "OPENSPEC_STORE_ROOT": sys_info["openspec_store_root"],
    }

    if extra_vars:
        ctx.update(extra_vars)

    # Validate that registered variables are concrete absolute paths
    for key in REGISTERED_VARIABLES:
        val = ctx.get(key)
        if not val or not val.startswith("/"):
            raise ValueError(f"Variable {key} must resolve to a non-empty absolute path, got '{val}'")

    return ctx


def render_content(template_text: str, context: dict[str, str]) -> tuple[str, list[str]]:
    """Render template text by replacing {{VAR}} placeholders.

    Returns the rendered string and a list of any unexpanded {{TAG}} occurrences.
    """
    rendered = template_text
    for key, val in context.items():
        placeholder = f"{{{{{key}}}}}"
        rendered = rendered.replace(placeholder, val)
        # Also support legacy @VAR@ format if present in legacy plists
        legacy_placeholder = f"@{key}@"
        rendered = rendered.replace(legacy_placeholder, val)

    # Check for any remaining unresolved {{...}} tags
    unresolved = re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", rendered)
    return rendered, unresolved


def render_file(
    source_path: Path,
    output_path: Path | None,
    context: dict[str, str],
    dry_run: bool = False,
) -> RenderResult:
    """Render a single template file and optionally write output."""
    try:
        content = source_path.read_text(encoding="utf-8")
    except Exception as exc:
        return RenderResult(
            source_path=str(source_path),
            target_path=str(output_path) if output_path else None,
            unresolved_tags=[],
            success=False,
            error=f"Failed to read template: {exc}",
        )

    rendered, unresolved = render_content(content, context)

    if unresolved:
        return RenderResult(
            source_path=str(source_path),
            target_path=str(output_path) if output_path else None,
            unresolved_tags=unresolved,
            success=False,
            content=rendered,
            error=f"Unresolved template tags found: {', '.join(unresolved)}",
        )

    if output_path and not dry_run:
        # Prevent path traversal outside intended directory
        target_resolved = output_path.resolve()
        try:
            target_resolved.parent.mkdir(parents=True, exist_ok=True)
            target_resolved.write_text(rendered, encoding="utf-8")
        except Exception as exc:
            return RenderResult(
                source_path=str(source_path),
                target_path=str(output_path),
                unresolved_tags=[],
                success=False,
                error=f"Failed to write output file: {exc}",
            )

    return RenderResult(
        source_path=str(source_path),
        target_path=str(output_path) if output_path else None,
        unresolved_tags=[],
        success=True,
        content=rendered,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Render workstation templates with concrete absolute paths.")
    parser.add_argument("--template", "-t", help="Template file path")
    parser.add_argument("--output", "-o", help="Rendered output file path (stdout if omitted)")
    parser.add_argument("--template-dir", help="Directory containing template files (*.tmpl, *.template)")
    parser.add_argument("--output-dir", help="Output directory for rendered files")
    parser.add_argument("--dry-run", action="store_true", help="Render in-memory and validate without writing files")
    parser.add_argument("--json", action="store_true", help="Output structured JSON results")
    parser.add_argument("--home", help="Override HOME path")
    parser.add_argument("--homebrew-prefix", help="Override Homebrew prefix")
    parser.add_argument("--workspace-root", help="Override Workspace root")
    parser.add_argument("--openspec-store-root", help="Override OpenSpec store root")
    parser.add_argument("--arch", help="Override architecture (arm64, x86_64)")
    parser.add_argument("--var", action="append", help="Extra variable in KEY=VALUE format")

    args = parser.parse_args()

    extra_vars = {}
    if args.var:
        for v in args.var:
            if "=" in v:
                k, val = v.split("=", 1)
                extra_vars[k.strip()] = val.strip()

    try:
        ctx = build_variable_context(
            home=args.home,
            homebrew_prefix=args.homebrew_prefix,
            workspace_root=args.workspace_root,
            openspec_store_root=args.openspec_store_root,
            arch=args.arch,
            extra_vars=extra_vars,
        )
    except Exception as exc:
        if args.json:
            print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        else:
            print(f"Error building template context: {exc}", file=sys.stderr)
        return 1

    results: list[RenderResult] = []

    if args.template_dir:
        tmpl_dir = Path(args.template_dir)
        if not tmpl_dir.is_dir():
            print(f"Template directory not found: {tmpl_dir}", file=sys.stderr)
            return 1
        out_dir = Path(args.output_dir) if args.output_dir else tmpl_dir / "rendered"

        tmpl_files = list(tmpl_dir.glob("*.tmpl")) + list(tmpl_dir.glob("*.template"))
        if not tmpl_files:
            print(f"No .tmpl or .template files found in {tmpl_dir}", file=sys.stderr)
            return 1

        for tmpl_path in tmpl_files:
            # Strip .tmpl or .template extension for output file name
            out_name = tmpl_path.stem if tmpl_path.suffix in (".tmpl", ".template") else tmpl_path.name
            target = out_dir / out_name
            res = render_file(tmpl_path, target, ctx, dry_run=args.dry_run)
            results.append(res)
    elif args.template:
        tmpl_path = Path(args.template)
        if not tmpl_path.is_file():
            print(f"Template file not found: {tmpl_path}", file=sys.stderr)
            return 1
        out_path = Path(args.output) if args.output else None
        res = render_file(tmpl_path, out_path, ctx, dry_run=args.dry_run)
        results.append(res)
        if not out_path and not args.json and res.success and res.content:
            print(res.content)
            return 0
    else:
        parser.print_help()
        return 1

    all_success = all(r.success for r in results)

    if args.json:
        payload = {
            "success": all_success,
            "dry_run": args.dry_run,
            "context": ctx,
            "results": [asdict(r) for r in results],
        }
        print(json.dumps(payload, indent=2))
    else:
        for r in results:
            status = "OK" if r.success else "FAILED"
            print(f"[{status}] {r.source_path} -> {r.target_path or 'stdout'}")
            if not r.success and r.error:
                print(f"  Error: {r.error}", file=sys.stderr)

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
