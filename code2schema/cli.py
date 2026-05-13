"""
code2schema.cli
~~~~~~~~~~~~~~~
CLI v3 — pełny pipeline.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from code2schema.analyzer.cqrs import analyze
from code2schema.analyzer.events import infer_event_model
from code2schema.analyzer.graph import (
    build_rich_graph,
    detect_cycles,
    graph_summary,
    write_dot,
    write_graphml,
)
from code2schema.codegen import write_json, write_markdown, write_proto
from code2schema.codegen.visualizer import write_html
from code2schema.core.extractor import extract_project


_SPECIAL_PROJECT_DIRS = {"backend", "frontend", "src", "app", "api"}
_GENERIC_PATH_PARTS = {"home", "github", "workspace", "projects", "src"}


def _project_name_from_path(path: Path) -> str:
    """Extract project name from path (e.g., /path/to/c2004/backend -> c2004)."""
    # Try to find a meaningful name from the path
    parts = path.parts
    for i, part in enumerate(reversed(parts)):
        if part in _SPECIAL_PROJECT_DIRS:
            # Use parent directory name
            if i < len(parts) - 1:
                return parts[-(i + 2)]
        # Skip common generic names
        if part not in _GENERIC_PATH_PARTS:
            return part
    return path.name or "project"


def _build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    from code2schema import __version__

    parser = argparse.ArgumentParser(
        prog="code2schema",
        description="Semantic Compiler: Code → CQRS → Schema / Proto / Graph",
    )
    parser.add_argument("path")
    parser.add_argument(
        "-o",
        "--out",
        metavar="FILE",
        help="Output JSON schema (default: <project>_schema.json)",
    )
    parser.add_argument(
        "--proto",
        metavar="FILE",
        nargs="?",
        const=True,
        default=None,
        help="Output .proto file (default: <project>_api.proto if flag present)",
    )
    parser.add_argument(
        "--md",
        metavar="FILE",
        nargs="?",
        const=True,
        default=None,
        help="Output Markdown report (default: <project>_report.md if flag present)",
    )
    parser.add_argument("--graphml", metavar="FILE")
    parser.add_argument("--dot", metavar="FILE")
    parser.add_argument(
        "--html",
        metavar="FILE",
        nargs="?",
        const=True,
        default=None,
        help="Interactive HTML visualization (default: <project>_viz.html if flag present)",
    )
    parser.add_argument("--events", action="store_true")
    parser.add_argument("--cycles", action="store_true")
    parser.add_argument("--graph-summary", action="store_true")
    parser.add_argument("--no-rules", action="store_true")
    parser.add_argument("--exclude", nargs="*", default=[])
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _resolve_output_dir(root: Path) -> Path:
    if not root.is_dir():
        return root.parent
    if root.name in _SPECIAL_PROJECT_DIRS:
        return root.parent
    return root


def _resolve_required_path(out_dir: Path, value: str | None, default_name: str) -> Path:
    return out_dir / (value or default_name)


def _resolve_optional_path(
    out_dir: Path,
    value: str | bool | None,
    default_name: str,
) -> Path | None:
    if isinstance(value, str):
        return out_dir / value
    if value is True:
        return out_dir / default_name
    return None


def _validate_root(args: argparse.Namespace) -> Path:
    """Return ``Path`` for the analysis root from CLI args."""
    return Path(args.path)


def _build_output_paths(
    root: Path, args: argparse.Namespace
) -> tuple[Path, Path | None, Path | None, Path | None]:
    """Build output file paths (JSON / proto / md / html) for the resolved root."""
    proj_name = _project_name_from_path(root)
    out_dir = _resolve_output_dir(root)

    out_path = _resolve_required_path(out_dir, args.out, f"{proj_name}_schema.json")
    proto_path = _resolve_optional_path(out_dir, args.proto, f"{proj_name}_api.proto")
    md_path = _resolve_optional_path(out_dir, args.md, f"{proj_name}_report.md")
    html_path = _resolve_optional_path(out_dir, args.html, f"{proj_name}_viz.html")
    return out_path, proto_path, md_path, html_path


def _resolve_paths(
    args: argparse.Namespace,
) -> tuple[Path, Path, Path | None, Path | None, Path | None]:
    """Resolve root and all output file paths from CLI args."""
    root = _validate_root(args)
    out_path, proto_path, md_path, html_path = _build_output_paths(root, args)
    return root, out_path, proto_path, md_path, html_path


def _run_extraction(args, root):
    """Parse project and run CQRS analysis. Returns (modules, schema, G) or None on failure."""
    modules = extract_project(root, exclude=args.exclude or None)
    if not modules:
        print("ERROR: Brak plików .py.", file=sys.stderr)
        return None
    schema = analyze(modules)
    if args.no_rules:
        schema.rules = []
    G = build_rich_graph(schema)
    return modules, schema, G


def _run_reports(args, modules, schema, G):
    """Print optional reports: cycles, graph summary, events."""
    if args.cycles:
        cycles = detect_cycles(G)
        if cycles:
            print(f"\n⚠️  Cykle ({len(cycles)}):")
            for c in cycles[:5]:
                print(f"  {' → '.join(c[:5])}")
        else:
            print("✅ Brak cykli.")

    if args.graph_summary:
        print("\n── Graph Summary ──────────────────────")
        print(graph_summary(G, schema))

    if args.events:
        em = infer_event_model(modules)
        print("\n── Event Model ────────────────────────")
        print(em.summary())


def _write_outputs(args, schema, G, out_path, proto_path, md_path, html_path):
    """Write all output files (JSON, proto, md, html, graphml, dot)."""
    write_json(schema, out_path)
    if proto_path:
        write_proto(schema, proto_path)
    if md_path:
        write_markdown(schema, md_path)
    if html_path:
        write_html(schema, html_path)
    if args.graphml:
        write_graphml(G, Path(args.graphml))
    if args.dot:
        write_dot(G, Path(args.dot))


def _print_summary(modules, schema, G, t0, out_path, proto_path, md_path, html_path):
    """Print final summary with metrics and output file names."""
    funcs = schema.all_functions()
    outputs = [f"   → {out_path.name}"]
    if proto_path:
        outputs.append(f"   → {proto_path.name}")
    if md_path:
        outputs.append(f"   → {md_path.name}")
    if html_path:
        outputs.append(f"   → {html_path.name}")
    print(
        f"\n✅ Gotowe ({time.perf_counter() - t0:.2f}s)\n"
        f"   Modules  : {len(modules)}\n"
        f"   Functions: {len(funcs)}\n"
        f"   Queries  : {len(schema.queries())}\n"
        f"   Commands : {len(schema.commands())}\n"
        f"   Orchest. : {len(schema.orchestrators())}\n"
        f"   Workflows: {len(schema.workflows)}\n"
        f"   Rules    : {len(schema.rules)}\n"
        f"   Graph    : {G.number_of_nodes()}N / {G.number_of_edges()}E\n" + "\n".join(outputs)
    )


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    root, out_path, proto_path, md_path, html_path = _resolve_paths(args)
    if not root.exists():
        print(f"ERROR: {root}", file=sys.stderr)
        return 1

    t0 = time.perf_counter()
    if not args.quiet:
        print(f"⏳ Parsing: {root}")

    result = _run_extraction(args, root)
    if result is None:
        return 1
    modules, schema, G = result

    _run_reports(args, modules, schema, G)
    _write_outputs(args, schema, G, out_path, proto_path, md_path, html_path)

    if not args.quiet:
        _print_summary(modules, schema, G, t0, out_path, proto_path, md_path, html_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
