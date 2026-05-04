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
    build_rich_graph, detect_cycles, graph_summary, write_dot, write_graphml,
)
from code2schema.codegen import write_json, write_markdown, write_proto
from code2schema.codegen.visualizer import write_html
from code2schema.core.extractor import extract_project


def _project_name_from_path(path: Path) -> str:
    """Extract project name from path (e.g., /path/to/c2004/backend -> c2004)."""
    # Try to find a meaningful name from the path
    parts = path.parts
    for i, part in enumerate(reversed(parts)):
        if part in ("backend", "frontend", "src", "app", "api"):
            # Use parent directory name
            if i < len(parts) - 1:
                return parts[-(i + 2)]
        # Skip common generic names
        if part not in ("home", "github", "workspace", "projects", "src"):
            return part
    return path.name or "project"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="code2schema",
        description="Semantic Compiler: Code → CQRS → Schema / Proto / Graph")
    parser.add_argument("path")
    parser.add_argument("-o", "--out", metavar="FILE", help="Output JSON schema (default: <project>_schema.json)")
    parser.add_argument("--proto", metavar="FILE", nargs="?", const=True, default=None,
                        help="Output .proto file (default: <project>_api.proto if flag present)")
    parser.add_argument("--md", metavar="FILE", nargs="?", const=True, default=None,
                        help="Output Markdown report (default: <project>_report.md if flag present)")
    parser.add_argument("--graphml", metavar="FILE")
    parser.add_argument("--dot", metavar="FILE")
    parser.add_argument("--html", metavar="FILE", nargs="?", const=True, default=None,
                        help="Interactive HTML visualization (default: <project>_viz.html if flag present)")
    parser.add_argument("--events", action="store_true")
    parser.add_argument("--cycles", action="store_true")
    parser.add_argument("--graph-summary", action="store_true")
    parser.add_argument("--no-rules", action="store_true")
    parser.add_argument("--exclude", nargs="*", default=[])
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.exists():
        print(f"ERROR: {root}", file=sys.stderr)
        return 1

    # Determine project name and output directory
    proj_name = _project_name_from_path(root)
    # Use parent dir if path ends with backend/frontend/src/app/api, otherwise use path itself
    if root.is_dir() and root.name in ("backend", "frontend", "src", "app", "api"):
        out_dir = root.parent
    else:
        out_dir = root if root.is_dir() else root.parent

    out_path = (out_dir / args.out) if args.out else (out_dir / f"{proj_name}_schema.json")
    proto_path = out_dir / args.proto if isinstance(args.proto, str) else (out_dir / f"{proj_name}_api.proto" if args.proto is True else None)
    md_path = out_dir / args.md if isinstance(args.md, str) else (out_dir / f"{proj_name}_report.md" if args.md is True else None)
    html_path = out_dir / args.html if isinstance(args.html, str) else (out_dir / f"{proj_name}_viz.html" if args.html is True else None)

    t0 = time.perf_counter()
    if not args.quiet:
        print(f"⏳ Parsing: {root}")

    modules = extract_project(root, exclude=args.exclude or None)
    if not modules:
        print("ERROR: Brak plików .py.", file=sys.stderr)
        return 1

    schema = analyze(modules)
    if args.no_rules:
        schema.rules = []

    G = build_rich_graph(schema)

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

    if not args.quiet:
        funcs = schema.all_functions()
        outputs = [f"   → {out_path.name}"]
        if proto_path:
            outputs.append(f"   → {proto_path.name}")
        if md_path:
            outputs.append(f"   → {md_path.name}")
        if html_path:
            outputs.append(f"   → {html_path.name}")
        print(
            f"\n✅ Gotowe ({time.perf_counter()-t0:.2f}s)\n"
            f"   Modules  : {len(modules)}\n"
            f"   Functions: {len(funcs)}\n"
            f"   Queries  : {len(schema.queries())}\n"
            f"   Commands : {len(schema.commands())}\n"
            f"   Orchest. : {len(schema.orchestrators())}\n"
            f"   Workflows: {len(schema.workflows)}\n"
            f"   Rules    : {len(schema.rules)}\n"
            f"   Graph    : {G.number_of_nodes()}N / {G.number_of_edges()}E\n"
            + "\n".join(outputs)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
